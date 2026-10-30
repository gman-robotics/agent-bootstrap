"""Changed-line and changed-function scope for the ub gates."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.ub_changed_scope import (
    FnSpan,
    changed_lines_from_diff,
    filter_crap,
    filter_dry,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCOPE_PY = REPO_ROOT / "scripts" / "ub_changed_scope.py"


def _provider(spans: list[FnSpan]):
    def provide(path: Path, root: Path) -> list[FnSpan]:
        return spans

    return provide


class ChangedLinesTests(unittest.TestCase):
    def test_multi_hunk_accumulates_new_side_lines(self) -> None:
        diff = "\n".join(
            [
                "diff --git a/a.py b/a.py",
                "--- a/a.py",
                "+++ b/a.py",
                "@@ -1,0 +1 @@",
                "+first",
                "@@ -4 +5,3 @@",
                "+a",
                "+b",
                "+c",
                "",
            ]
        )
        self.assertEqual(changed_lines_from_diff(diff), {"a.py": [1, 5, 6, 7]})

    def test_omitted_new_count_means_one_line(self) -> None:
        diff = "\n".join(
            [
                "diff --git a/a.py b/a.py",
                "--- a/a.py",
                "+++ b/a.py",
                "@@ -4,1 +8 @@",
                "+only",
                "",
            ]
        )
        self.assertEqual(changed_lines_from_diff(diff), {"a.py": [8]})

    def test_zero_new_count_is_a_pure_deletion(self) -> None:
        diff = "\n".join(
            [
                "diff --git a/old.py b/old.py",
                "--- a/old.py",
                "+++ b/old.py",
                "@@ -3,2 +3,0 @@",
                "-gone",
                "-also",
                "@@ -8 +6 @@",
                "+kept",
                "",
            ]
        )
        self.assertEqual(changed_lines_from_diff(diff), {"old.py": [6]})

    def test_new_file_uses_the_new_path(self) -> None:
        diff = "\n".join(
            [
                "diff --git a/fresh.py b/fresh.py",
                "new file mode 100644",
                "--- /dev/null",
                "+++ b/fresh.py",
                "@@ -0,0 +1,2 @@",
                "+a",
                "+b",
                "",
            ]
        )
        self.assertEqual(changed_lines_from_diff(diff), {"fresh.py": [1, 2]})

    def test_rename_tracks_the_new_path(self) -> None:
        diff = "\n".join(
            [
                "diff --git a/old.py b/renamed.py",
                "similarity index 90%",
                "rename from old.py",
                "rename to renamed.py",
                "--- a/old.py",
                "+++ b/renamed.py",
                "@@ -2 +2 @@",
                "+edited",
                "",
            ]
        )
        self.assertEqual(changed_lines_from_diff(diff), {"renamed.py": [2]})

    def test_text_after_a_tab_on_the_plus_line_is_not_part_of_the_path(self) -> None:
        diff = "+++ b/src/a.py\tother\n@@ -1 +1 @@\n+x\n"
        self.assertEqual(changed_lines_from_diff(diff), {"src/a.py": [1]})

    def test_a_quote_on_only_one_side_stays_in_the_path(self) -> None:
        diff = '+++ b/src/a.py"\n@@ -1 +1 @@\n+x\n'
        self.assertEqual(changed_lines_from_diff(diff), {'src/a.py"': [1]})

    def test_a_quoted_path_with_a_space_is_unquoted(self) -> None:
        diff = '+++ "b/src/my file.py"\n@@ -4 +8 @@\n+only\n'
        self.assertEqual(changed_lines_from_diff(diff), {"src/my file.py": [8]})


class CrapFilterTests(unittest.TestCase):
    def test_keeps_changed_function_and_marks_unchanged_as_debt(self) -> None:
        edn = "\n".join(
            [
                "{:entries [",
                '  {:name "f", :namespace "pkg", :complexity 1, :coverage 0.0, :crap 4.0}',
                '  {:name "g", :namespace "pkg", :complexity 1, :coverage 0.0, :crap 20.0}',
                "]}",
            ]
        )
        spans = [
            FnSpan("pkg", "f", 1, 3, "a.py"),
            FnSpan("pkg", "g", 10, 12, "a.py"),
        ]
        result = filter_crap(edn, {"a.py": [2]}, _provider(spans), 10)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["debt"], [{"namespace": "pkg", "name": "g", "crap": 20.0}])

    def test_crap_above_threshold_on_a_changed_function_is_a_finding(self) -> None:
        edn = '{:entries [{:name "f", :namespace "pkg", :complexity 4, :coverage 0.0, :crap 20.0}]}'
        spans = [FnSpan("pkg", "f", 1, 4, "a.py")]
        result = filter_crap(edn, {"a.py": [2]}, _provider(spans), 10)
        self.assertEqual(result["findings"], [{"namespace": "pkg", "name": "f", "crap": 20.0}])
        self.assertEqual(result["debt"], [])

    def test_crap_equal_to_threshold_is_not_a_finding(self) -> None:
        edn = '{:entries [{:name "f", :namespace "pkg", :complexity 1, :coverage nil, :crap 10.0}]}'
        spans = [FnSpan("pkg", "f", 1, 2, "a.py")]
        result = filter_crap(edn, {"a.py": [1]}, _provider(spans), 10)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["debt"], [])

    def test_nil_crap_on_a_changed_function_is_not_a_finding(self) -> None:
        edn = "\n".join(
            [
                "{:entries [",
                '  {:name "changed", :namespace "pkg", :complexity 1, :coverage nil, :crap nil}',
                '  {:name "old", :namespace "pkg", :complexity 1, :coverage nil, :crap nil}',
                "]}",
            ]
        )
        spans = [
            FnSpan("pkg", "changed", 1, 2, "a.py"),
            FnSpan("pkg", "old", 8, 9, "a.py"),
        ]
        result = filter_crap(edn, {"a.py": [1]}, _provider(spans), 10)
        self.assertEqual(result["findings"], [])
        self.assertEqual([item["name"] for item in result["debt"]], ["old"])

    def test_absent_crap_is_not_a_finding(self) -> None:
        edn = '{:entries [{:name "f", :namespace "pkg", :complexity 1, :coverage nil}]}'
        spans = [FnSpan("pkg", "f", 1, 2, "a.py")]
        result = filter_crap(edn, {"a.py": [1]}, _provider(spans), 10)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["debt"], [])

    def test_duplicate_names_match_by_namespace(self) -> None:
        edn = "\n".join(
            [
                "{:entries [",
                '  {:name "run", :namespace "a", :complexity 4, :coverage 0.0, :crap 40.0}',
                '  {:name "run", :namespace "b", :complexity 4, :coverage 0.0, :crap 40.0}',
                "]}",
            ]
        )
        spans = [
            FnSpan("a", "run", 1, 3, "a.py"),
            FnSpan("b", "run", 20, 30, "a.py"),
        ]
        result = filter_crap(edn, {"a.py": [2]}, _provider(spans), 10)
        self.assertEqual([item["namespace"] for item in result["findings"]], ["a"])
        self.assertEqual([item["namespace"] for item in result["debt"]], ["b"])

    def test_windows_path_uses_the_forward_slash_changed_lines(self) -> None:
        edn = '{:entries [{:name "f", :namespace "pkg", :complexity 4, :coverage 0.0, :crap 20.0}]}'
        spans = [FnSpan("pkg", "f", 1, 4, "lib\\a.py")]
        result = filter_crap(edn, {"lib/a.py": [2]}, _provider(spans), 10)
        self.assertEqual(result["findings"], [{"namespace": "pkg", "name": "f", "crap": 20.0}])
        self.assertEqual(result["debt"], [])

    def test_a_short_path_matches_a_longer_changed_path(self) -> None:
        edn = '{:entries [{:name "f", :namespace "pkg", :complexity 4, :coverage 0.0, :crap 20.0}]}'
        spans = [FnSpan("pkg", "f", 1, 4, "a.py")]
        result = filter_crap(edn, {"lib/a.py": [2]}, _provider(spans), 10)
        self.assertEqual(result["findings"], [{"namespace": "pkg", "name": "f", "crap": 20.0}])
        self.assertEqual(result["debt"], [])


class DryFilterTests(unittest.TestCase):
    def _edn(self, left: str, right: str, score: str) -> str:
        return "\n".join(
            [
                "{:candidates [",
                f" {{:score {score}",
                '  :language "python"',
                f"  :left {left}",
                f"  :right {right}",
                "  :left-nodes 4",
                "  :right-nodes 4}}",
                "]}",
            ]
        )

    def test_left_overlap_is_a_finding(self) -> None:
        edn = self._edn(
            '{:file "a.py", :start-line 1, :end-line 3}',
            '{:file "b.py", :start-line 40, :end-line 44}',
            "0.91",
        )
        result = filter_dry(edn, {"a.py": [2]}, 0.8)
        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual(result["debt"], [])

    def test_right_overlap_is_a_finding(self) -> None:
        edn = self._edn(
            '{:file "b.py", :start-line 40, :end-line 44}',
            '{:file "a.py", :start-line 1, :end-line 3}',
            "0.80",
        )
        result = filter_dry(edn, {"a.py": [3]}, 0.8)
        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual(result["debt"], [])

    def test_no_overlap_is_debt(self) -> None:
        edn = self._edn(
            '{:file "a.py", :start-line 1, :end-line 2}',
            '{:file "a.py", :start-line 30, :end-line 33}',
            "0.95",
        )
        result = filter_dry(edn, {"a.py": [10]}, 0.8)
        self.assertEqual(result["findings"], [])
        self.assertEqual(len(result["debt"]), 1)

    def test_overlap_below_threshold_is_debt(self) -> None:
        edn = self._edn(
            '{:file "a.py", :start-line 1, :end-line 4}',
            '{:file "b.py", :start-line 1, :end-line 4}',
            "0.79",
        )
        result = filter_dry(edn, {"a.py": [2]}, 0.8)
        self.assertEqual(result["findings"], [])
        self.assertEqual(len(result["debt"]), 1)

    def test_score_equal_to_threshold_is_a_finding_when_one_span_overlaps(self) -> None:
        edn = "\n".join(
            [
                "{:candidates [",
                " {:score 0.8",
                '  :language "python"',
                '  :left {:file "a.py", :start-line 1, :end-line 3}}',
                "]}",
            ]
        )
        result = filter_dry(edn, {"a.py": [2]}, 0.8)
        self.assertEqual(result["debt"], [])
        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual(result["findings"][0]["score"], 0.8)
        self.assertIsNone(result["findings"][0]["right"])
        self.assertEqual(result["findings"][0]["left"]["file"], "a.py")

    def test_a_different_file_does_not_use_another_files_lines(self) -> None:
        edn = self._edn(
            '{:file "b.py", :start-line 1, :end-line 3}',
            '{:file "c.py", :start-line 1, :end-line 3}',
            "0.95",
        )
        result = filter_dry(edn, {"a.py": [2]}, 0.8)
        self.assertEqual(result["findings"], [])
        self.assertEqual(len(result["debt"]), 1)


class ScopeCliTests(unittest.TestCase):
    def test_lines_cli_prints_comma_joined_new_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _git_init(repo)
            lib = repo / "lib"
            lib.mkdir()
            (lib / "a.py").write_text("a\nb\nc\n", encoding="utf-8")
            _commit(repo, "base")
            subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
            (lib / "a.py").write_text("a\nB\nc\n", encoding="utf-8")
            _commit(repo, "change")
            proc = subprocess.run(
                [sys.executable, str(SCOPE_PY), "lines", "--base", "main", "--file", "lib/a.py"],
                cwd=repo,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), "2")

    def test_crap_cli_prefers_the_functions_json_seam(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _git_init(repo)
            (repo / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
            _commit(repo, "base")
            subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
            (repo / "a.py").write_text("def f():\n    return 2\n", encoding="utf-8")
            _commit(repo, "change")
            edn = repo / "crap.edn"
            edn.write_text(
                '{:entries [{:name "f", :namespace "custom.ns", :complexity 1, :coverage 0.0, :crap 30.0}]}\n',
                encoding="utf-8",
            )
            spec = repo / "fns.json"
            spec.write_text(
                json.dumps(
                    [
                        {
                            "namespace": "custom.ns",
                            "name": "f",
                            "start_line": 1,
                            "end_line": 2,
                            "path": "a.py",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["UB_SCOPE_FUNCTIONS_JSON"] = str(spec)
            proc = subprocess.run(
                [sys.executable, str(SCOPE_PY), "crap", "--base", "main", "--edn", str(edn)],
                cwd=repo,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["findings"][0]["namespace"], "custom.ns")

    def test_crap_cli_exits_2_when_crapper_is_missing(self) -> None:
        if _crapper_importable():
            self.skipTest("crapper is installed")
        proc = subprocess.run(
            [sys.executable, str(SCOPE_PY), "crap", "--base", "main", "--edn", "crap.edn"],
            capture_output=True,
            text=True,
            env={"PATH": os.environ.get("PATH", "")},
        )
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("not importable", proc.stderr)

    def test_lock_pins_tools(self) -> None:
        text = (REPO_ROOT / "scripts" / "ub-tools.lock").read_text(encoding="utf-8")
        self.assertIn("crapper=6fd92c4c9bcc56efb64a2f8743d5a2993bcfd42d\n", text)
        self.assertIn("dryer=66ff6d21a42c04afcad89c78a80066176d1294b0\n", text)
        self.assertIn("mutator=a5a0cb803b66e0cdb8bf471b3b08af701d424a41\n", text)
        self.assertIn("cargo_llvm_cov=0.6.21\n", text)
        self.assertIn("python=3.13\n", text)
        self.assertIn("uv=0.13.6\n", text)


def _git_init(repo: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)


def _commit(repo: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True, capture_output=True)


def _crapper_importable() -> bool:
    try:
        import crapper  # noqa: F401
    except ImportError:
        return False
    return True


if __name__ == "__main__":
    unittest.main()
