"""Real crapper, dryer, and mutator on known-bad and known-good fixtures.

Skipped when the three tools are not on PATH. UB_REQUIRE_GATE_TOOLS=1 turns
that skip into a failure so the ub-gates CI job cannot pass without them.
"""

import ast
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "run_ub_gates_ci.sh"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "ub_gate_pairs"
GATES = ("crapper", "dryer", "mutator")
KINDS = ("bad", "good")
TOOLS = ("crapper", "dryer", "mutator")

COVERAGE_CMD = (
    "coverage run -m unittest discover -s tests -p 'check_*.py'"
    " && mkdir -p target/coverage/python"
    " && coverage lcov -o target/coverage/python/lcov.info"
)
MUTATOR_CMD = "python -m unittest discover -s tests -p 'check_*.py'"

# Survivors are mutator exit 3. The outcome file has no separate count.
_BAD_KEY = {
    "crapper": "crapper_findings",
    "dryer": "dryer_findings",
    "mutator": "mutator_exit",
}


def _missing_tools() -> list[str]:
    return [name for name in TOOLS if shutil.which(name) is None]


def _functions(path: Path) -> list[ast.FunctionDef]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [node for node in tree.body if isinstance(node, ast.FunctionDef)]


def _complexity(fn: ast.AST) -> int:
    score = 1
    for node in ast.walk(fn):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.Assert, ast.IfExp)):
            score += 1
        elif isinstance(node, ast.BoolOp):
            score += len(node.values) - 1
        elif isinstance(node, ast.comprehension):
            score += 1 + len(node.ifs)
    return score


def _node_count(fn: ast.AST) -> int:
    return sum(1 for node in ast.walk(fn) if not isinstance(node, ast.expr_context))


def _git(repo: Path, args: list[str]) -> None:
    proc = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed\n{proc.stderr}")


def _repo_with(repo: Path, fixture: Path) -> None:
    _git(repo, ["init", "-b", "main"])
    _git(repo, ["config", "user.email", "t@example.com"])
    _git(repo, ["config", "user.name", "t"])
    lib = repo / "lib"
    lib.mkdir()
    (lib / "__init__.py").write_text("", encoding="utf-8")
    _git(repo, ["add", "."])
    _git(repo, ["commit", "-m", "base"])
    # Branch change keeps main at the empty lib commit so UB_GATES_BASE_REF=main has a merge base.
    _git(repo, ["checkout", "-b", "change"])
    shutil.copytree(fixture, repo, dirs_exist_ok=True)
    _git(repo, ["add", "."])
    _git(repo, ["commit", "-m", "fixture"])
    # Untracked. Keeps lcov paths relative so crapper and mutator match lib/*.py.
    (repo / ".coveragerc").write_text("[run]\nrelative_files = true\n", encoding="utf-8")


def _gate_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in list(env):
        if key.startswith("UB_GATES_") or key == "UB_SCOPE_FUNCTIONS_JSON":
            env.pop(key)
    env.pop("CURSOR_AGENT", None)
    env.pop("GITHUB_STEP_SUMMARY", None)
    env.pop("PYTHONPATH", None)
    env.pop("COVERAGE_FILE", None)
    env.pop("COVERAGE_RCFILE", None)
    env["UB_GATES_ADVISORY"] = "0"
    env["UB_GATES_BASE_REF"] = "main"
    env["UB_GATES_HUB_PATH"] = str(REPO_ROOT)
    env["UB_GATES_COVERAGE_CMD"] = COVERAGE_CMD
    env["UB_GATES_MUTATOR_TEST_CMD"] = MUTATOR_CMD
    return env


def _metrics(text: str) -> dict[str, str]:
    found = {}
    for line in text.splitlines():
        key, sep, value = line.partition("=")
        if sep:
            found[key] = value
    return found


class UbGatePairTests(unittest.TestCase):
    def test_fixture_layout_stays_outside_hub_discovery(self) -> None:
        for gate in GATES:
            for kind in KINDS:
                root = FIXTURES / gate / kind
                libs = list((root / "lib").glob("*.py"))
                checks = list((root / "tests").glob("check_*.py"))
                self.assertTrue(libs, root)
                self.assertEqual(len(checks), 1, root)
                self.assertEqual(list(root.rglob("__init__.py")), [])
                self.assertEqual(list(root.rglob("test_*.py")), [])

    def test_crapper_bad_complexity_is_at_least_11(self) -> None:
        functions = _functions(FIXTURES / "crapper" / "bad" / "lib" / "pick.py")
        self.assertEqual([fn.name for fn in functions], ["pick"])
        self.assertGreaterEqual(_complexity(functions[0]), 11)
        check = (FIXTURES / "crapper" / "bad" / "tests" / "check_pick.py").read_text(encoding="utf-8")
        self.assertNotIn("pick(", check)

    def test_dryer_bad_functions_are_large_clones(self) -> None:
        functions = _functions(FIXTURES / "dryer" / "bad" / "lib" / "shape.py")
        self.assertEqual([fn.name for fn in functions], ["shape_left", "shape_right"])
        for fn in functions:
            self.assertGreaterEqual(_node_count(fn), 20, fn.name)
            self.assertGreaterEqual(fn.end_lineno - fn.lineno + 1, 4, fn.name)
        left = ast.dump(ast.Module(body=functions[0].body, type_ignores=[]))
        right = ast.dump(ast.Module(body=functions[1].body, type_ignores=[]))
        self.assertEqual(left, right)

    def test_real_tools_score_each_pair(self) -> None:
        missing = _missing_tools()
        if missing:
            if os.environ.get("UB_REQUIRE_GATE_TOOLS") == "1":
                self.fail("UB_REQUIRE_GATE_TOOLS=1 but not on PATH: " + ", ".join(missing))
            self.skipTest("not on PATH: " + ", ".join(missing))
        for gate in GATES:
            for kind in KINDS:
                with self.subTest(gate=gate, kind=kind):
                    self._score(gate, kind)

    def _score(self, gate: str, kind: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _repo_with(repo, FIXTURES / gate / kind)
            proc = subprocess.run(
                ["/bin/bash", str(SCRIPT)],
                cwd=repo,
                env=_gate_env(),
                capture_output=True,
                text=True,
                timeout=600,
            )
            outcome_path = repo / ".metrics" / "ub-gates-outcome.txt"
            outcome = outcome_path.read_text(encoding="utf-8") if outcome_path.is_file() else ""
            detail = f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}\noutcome:\n{outcome}"
            metrics = _metrics(outcome)
            if kind == "good":
                self.assertEqual(proc.returncode, 0, detail)
                self.assertEqual(metrics.get("outcome"), "ran_clean", detail)
                self.assertEqual(metrics.get("gates_ran"), "1", detail)
                self.assertEqual(metrics.get("crapper_findings"), "0", detail)
                self.assertEqual(metrics.get("dryer_findings"), "0", detail)
                self.assertEqual(metrics.get("mutator_exit"), "0", detail)
                self.assertNotEqual(metrics.get("mutator_timeout"), "1", detail)
                return
            key = _BAD_KEY[gate]
            self.assertEqual(proc.returncode, 1, detail)
            self.assertEqual(metrics.get("outcome"), "ran_with_findings", detail)
            self.assertGreater(int(metrics.get(key, "0")), 0, detail)
            if gate == "mutator":
                self.assertEqual(metrics.get("mutator_exit"), "3", detail)


if __name__ == "__main__":
    unittest.main()
