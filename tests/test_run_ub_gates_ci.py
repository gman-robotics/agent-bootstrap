"""Tests for scripts/run_ub_gates_ci.sh (merge-base scope, tool-missing gate miss)."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "run_ub_gates_ci.sh"
REPORT_SCRIPT = REPO_ROOT / "scripts" / "run_ub_gates_report.sh"
_EMPTY_CRAP = (
    "#!/usr/bin/env bash\n"
    "mkdir -p .metrics\n"
    "echo '{:entries []}' > .metrics/crap.edn\n"
    "exit 0\n"
)


class RunUbGatesCiTests(unittest.TestCase):
    def _run_in_repo(self, repo: Path, env: dict | None = None) -> subprocess.CompletedProcess:
        run_env = os.environ.copy()
        # The ub-gates CI step exports UB_GATES_*; keep each case hermetic.
        for key in [k for k in run_env if k.startswith("UB_GATES_") or k == "UB_SCOPE_FUNCTIONS_JSON"]:
            run_env.pop(key)
        run_env["UB_GATES_OUTCOME_FILE"] = str(repo / ".metrics" / "ub-gates-outcome.txt")
        run_env.pop("GITHUB_STEP_SUMMARY", None)
        preserve_cursor_agent = env is not None and "CURSOR_AGENT" in env
        preserve_github_actions = env is not None and "GITHUB_ACTIONS" in env
        if env:
            run_env.update(env)
        if not preserve_cursor_agent:
            run_env.pop("CURSOR_AGENT", None)
        if not preserve_github_actions:
            run_env.pop("GITHUB_ACTIONS", None)
        return subprocess.run(
            ["/bin/bash", str(SCRIPT)],
            cwd=repo,
            env=run_env,
            capture_output=True,
            text=True,
        )

    def test_tools_missing_exits_zero_with_warning_not_gate_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
            (repo / "scripts").mkdir()
            (repo / "scripts" / "foo.py").write_text("x = 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
            (repo / "scripts" / "foo.py").write_text("x = 1\ny = 2\n", encoding="utf-8")
            subprocess.run(["git", "add", "scripts/foo.py"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "change"], cwd=repo, check=True, capture_output=True)
            shutil.copy(SCRIPT, repo / "run_ub_gates_ci.sh")

            proc = self._run_in_repo(
                repo,
                {
                    "UB_GATES_ADVISORY": "1",
                    "UB_GATES_BASE_REF": "main",
                    "GITHUB_ACTIONS": "true",
                    "PATH": "/usr/bin:/bin",
                },
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("skipped_tools_missing", proc.stdout + proc.stderr)
            self.assertIn("::warning title=ub-gates::", proc.stdout)
            outcome = (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")
            self.assertIn("outcome=skipped_tools_missing", outcome)
            self.assertIn("gate_miss=1", outcome)
            self.assertIn("gates_ran=0", outcome)

    def test_passes_explicit_file_list_to_mock_crapper(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            bin_dir = repo / "bin"
            bin_dir.mkdir()
            log_file = repo / "crapper-args.log"
            (bin_dir / "crapper").write_text(
                f"""#!/usr/bin/env bash
echo "$@" >> "{log_file}"
mkdir -p .metrics
echo '{{:entries []}}' > .metrics/crap.edn
exit 0
""",
                encoding="utf-8",
            )
            (bin_dir / "dryer").write_text(
                """#!/usr/bin/env bash
mkdir -p .metrics
echo '{:candidates []}' > .metrics/dry.edn
exit 0
""",
                encoding="utf-8",
            )
            (bin_dir / "mutator").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            for name in ("crapper", "dryer", "mutator"):
                (bin_dir / name).chmod(0o755)

            subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
            (repo / "lib").mkdir()
            (repo / "lib" / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
            (repo / "lib" / "a.py").write_text("def f():\n    return 2\n", encoding="utf-8")
            subprocess.run(["git", "add", "lib/a.py"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "change"], cwd=repo, check=True, capture_output=True)
            shutil.copy(SCRIPT, repo / "run_ub_gates_ci.sh")

            proc = self._run_in_repo(
                repo,
                self._empty_spans(
                    repo,
                    {
                        "UB_GATES_ADVISORY": "1",
                        "UB_GATES_BASE_REF": "main",
                        "PATH": f"{bin_dir}:/usr/bin:/bin",
                    },
                ),
            )
            self.assertEqual(
                proc.returncode,
                0,
                proc.stdout + proc.stderr + (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")
                if (repo / ".metrics" / "ub-gates-outcome.txt").exists()
                else "",
            )
            args = log_file.read_text(encoding="utf-8")
            self.assertIn("--threshold", args)
            self.assertIn("10", args)
            self.assertIn("lib/a.py", args)
            self.assertNotIn("--changed", args)
            outcome = (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")
            self.assertIn("outcome=ran_clean", outcome)
            self.assertIn("gates_ran=1", outcome)

    def _mock_repo_with_tools(self, tmp: str, crapper_body: str, dryer_body: str, mutator_body: str) -> Path:
        repo = Path(tmp)
        bin_dir = repo / "bin"
        bin_dir.mkdir()
        (bin_dir / "crapper").write_text(crapper_body, encoding="utf-8")
        (bin_dir / "dryer").write_text(dryer_body, encoding="utf-8")
        (bin_dir / "mutator").write_text(mutator_body, encoding="utf-8")
        for name in ("crapper", "dryer", "mutator"):
            (bin_dir / name).chmod(0o755)

        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
        (repo / "lib").mkdir()
        (repo / "lib" / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
        (repo / "lib" / "a.py").write_text("def f():\n    return 2\n", encoding="utf-8")
        subprocess.run(["git", "add", "lib/a.py"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "change"], cwd=repo, check=True, capture_output=True)
        return repo, bin_dir

    def test_dryer_high_score_yields_ran_with_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, bin_dir = self._mock_repo_with_tools(
                tmp,
                crapper_body=_EMPTY_CRAP,
                dryer_body="""#!/usr/bin/env bash
mkdir -p .metrics
cat > .metrics/dry.edn <<'EDN'
{:candidates [
 {:score 0.85
  :language "python"
  :left {:file "lib/a.py", :start-line 1, :end-line 2}
  :right {:file "lib/a.py", :start-line 1, :end-line 2}}
]}
EDN
exit 0
""",
                mutator_body="#!/usr/bin/env bash\nexit 0\n",
            )
            proc = self._run_in_repo(
                repo,
                self._empty_spans(
                    repo,
                    {
                        "UB_GATES_ADVISORY": "1",
                        "UB_GATES_BASE_REF": "main",
                        "PATH": f"{bin_dir}:/usr/bin:/bin",
                    },
                ),
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")
            self.assertIn("outcome=ran_with_findings", outcome)
            self.assertIn("gates_ran=1", outcome)

    def test_dryer_exit_2_yields_tool_error_not_ran_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, bin_dir = self._mock_repo_with_tools(
                tmp,
                crapper_body="#!/usr/bin/env bash\nexit 0\n",
                dryer_body="#!/usr/bin/env bash\nexit 2\n",
                mutator_body="#!/usr/bin/env bash\nexit 0\n",
            )
            proc = self._run_in_repo(
                repo,
                {
                    "UB_GATES_ADVISORY": "1",
                    "UB_GATES_BASE_REF": "main",
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                    "GITHUB_ACTIONS": "true",
                },
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("tool_error", proc.stdout + proc.stderr)
            outcome = (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")
            self.assertIn("outcome=tool_error", outcome)
            self.assertNotIn("outcome=ran_clean", outcome)
            self.assertIn("gate_miss=1", outcome)

    def test_missing_dry_edn_after_dryer_yields_tool_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, bin_dir = self._mock_repo_with_tools(
                tmp,
                crapper_body="#!/usr/bin/env bash\nexit 0\n",
                dryer_body="#!/usr/bin/env bash\nexit 0\n",
                mutator_body="#!/usr/bin/env bash\nexit 0\n",
            )
            proc = self._run_in_repo(
                repo,
                {
                    "UB_GATES_ADVISORY": "1",
                    "UB_GATES_BASE_REF": "main",
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                },
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")
            self.assertIn("outcome=tool_error", outcome)

    def test_mutator_exit_2_yields_tool_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, bin_dir = self._mock_repo_with_tools(
                tmp,
                crapper_body="#!/usr/bin/env bash\nexit 0\n",
                dryer_body="""#!/usr/bin/env bash
mkdir -p .metrics
echo '{:candidates []}' > .metrics/dry.edn
exit 0
""",
                mutator_body="#!/usr/bin/env bash\nexit 2\n",
            )
            proc = self._run_in_repo(
                repo,
                {
                    "UB_GATES_ADVISORY": "1",
                    "UB_GATES_BASE_REF": "main",
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                },
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")
            self.assertIn("outcome=tool_error", outcome)
            self.assertIn("mutator_exit=2", outcome)

    def test_report_wrapper_exits_zero_when_ci_exits_one_not_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            outcome = repo / ".metrics" / "ub-gates-outcome.txt"
            proc = subprocess.run(
                ["/bin/bash", str(REPORT_SCRIPT)],
                cwd=repo,
                env={
                    "UB_GATES_OUTCOME_FILE": str(outcome),
                    "PATH": "/usr/bin:/bin",
                },
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            text = outcome.read_text(encoding="utf-8")
            self.assertIn("outcome=skipped_not_git", text)

    def test_report_wrapper_exits_zero_when_no_merge_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
            (repo / "a.py").write_text("x=1\n", encoding="utf-8")
            subprocess.run(["git", "add", "a.py"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "only"], cwd=repo, check=True, capture_output=True)
            outcome = repo / ".metrics" / "ub-gates-outcome.txt"
            proc = subprocess.run(
                ["/bin/bash", str(REPORT_SCRIPT)],
                cwd=repo,
                env={
                    "UB_GATES_OUTCOME_FILE": str(outcome),
                    "UB_GATES_BASE_REF": "origin/main",
                    "PATH": "/usr/bin:/bin",
                },
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            text = outcome.read_text(encoding="utf-8")
            self.assertIn("outcome=skipped_no_base_ref", text)

    def test_cursor_agent_without_github_actions_skips_mutator(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "mutator-ran.log"
            repo, bin_dir = self._mock_repo_with_tools(
                tmp,
                crapper_body=_EMPTY_CRAP,
                dryer_body="""#!/usr/bin/env bash
mkdir -p .metrics
echo '{:candidates []}' > .metrics/dry.edn
exit 0
""",
                mutator_body=f"""#!/usr/bin/env bash
echo ran >> "{log}"
exit 0
""",
            )
            proc = self._run_in_repo(
                repo,
                self._empty_spans(
                    repo,
                    {
                        "UB_GATES_ADVISORY": "1",
                        "UB_GATES_BASE_REF": "main",
                        "PATH": f"{bin_dir}:/usr/bin:/bin",
                        "CURSOR_AGENT": "1",
                    },
                ),
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")
            self.assertIn("outcome=skipped_mutator", outcome)
            self.assertNotIn("outcome=ran_clean", outcome)
            self.assertIn("mutator_skipped=1", outcome)
            self.assertIn("gate_miss=1", outcome)
            self.assertFalse(log.exists())

    def test_cursor_agent_with_github_actions_runs_mutator(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, bin_dir = self._mock_repo_with_tools(
                tmp,
                crapper_body=_EMPTY_CRAP,
                dryer_body="""#!/usr/bin/env bash
mkdir -p .metrics
echo '{:candidates []}' > .metrics/dry.edn
exit 0
""",
                mutator_body=f"""#!/usr/bin/env bash
echo ran >> "{Path(tmp) / "mutator-ran.log"}"
exit 0
""",
            )
            log = Path(tmp) / "mutator-ran.log"
            mutator = bin_dir / "mutator"
            mutator.write_text(
                f"""#!/usr/bin/env bash
echo ran >> "{log}"
exit 0
""",
                encoding="utf-8",
            )
            mutator.chmod(0o755)
            proc = self._run_in_repo(
                repo,
                self._empty_spans(
                    repo,
                    {
                        "UB_GATES_ADVISORY": "1",
                        "UB_GATES_BASE_REF": "main",
                        "PATH": f"{bin_dir}:/usr/bin:/bin",
                        "CURSOR_AGENT": "1",
                        "GITHUB_ACTIONS": "true",
                    },
                ),
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")
            self.assertIn("mutator_exit=0", outcome)
            self.assertNotIn("mutator_skipped=1", outcome)
            self.assertTrue(log.read_text(encoding="utf-8").strip() == "ran")

    def _init_repo(self, repo: Path) -> None:
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)

    def _commit_all(self, repo: Path, message: str) -> None:
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True, capture_output=True)

    def _tool(self, bin_dir: Path, name: str, body: str) -> None:
        path = bin_dir / name
        path.write_text(body, encoding="utf-8")
        path.chmod(0o755)

    def _block_env(self, bin_dir: Path) -> dict[str, str]:
        return {
            "UB_GATES_ADVISORY": "0",
            "UB_GATES_BASE_REF": "main",
            "PATH": f"{bin_dir}:/usr/bin:/bin",
        }

    def _two_file_repo(self, repo: Path) -> None:
        self._init_repo(repo)
        lib = repo / "lib"
        lib.mkdir()
        (lib / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        (lib / "b.py").write_text("def g():\n    return 1\n", encoding="utf-8")
        self._commit_all(repo, "base")
        subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
        (lib / "a.py").write_text("def f():\n    return 2\n", encoding="utf-8")
        (lib / "b.py").write_text("def g():\n    return 2\n", encoding="utf-8")
        self._commit_all(repo, "change")

    def _gate_outcome(self, repo: Path) -> str:
        return (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")

    def _empty_spans(self, repo: Path, env: dict[str, str]) -> dict[str, str]:
        spec = repo / "fns.json"
        spec.write_text("[]", encoding="utf-8")
        env["UB_SCOPE_FUNCTIONS_JSON"] = str(spec)
        return env

    def _plant(self, repo: Path, rels: tuple[str, ...], text: str) -> None:
        for rel in rels:
            path = repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def test_blocking_tools_missing_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._init_repo(repo)
            (repo / "scripts").mkdir()
            (repo / "scripts" / "foo.py").write_text("x = 1\n", encoding="utf-8")
            self._commit_all(repo, "base")
            subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
            (repo / "scripts" / "foo.py").write_text("x = 2\n", encoding="utf-8")
            self._commit_all(repo, "change")
            proc = self._run_in_repo(
                repo,
                {
                    "UB_GATES_ADVISORY": "0",
                    "UB_GATES_BASE_REF": "main",
                    "GITHUB_ACTIONS": "true",
                    "PATH": "/usr/bin:/bin",
                },
            )
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("outcome=skipped_tools_missing", self._gate_outcome(repo))

    def test_blocking_no_base_ref_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._init_repo(repo)
            (repo / "a.py").write_text("x = 1\n", encoding="utf-8")
            self._commit_all(repo, "only")
            proc = self._run_in_repo(
                repo,
                {"UB_GATES_ADVISORY": "0", "UB_GATES_BASE_REF": "origin/missing", "PATH": "/usr/bin:/bin"},
            )
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("outcome=skipped_no_base_ref", self._gate_outcome(repo))

    def test_blocking_no_merge_base_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._init_repo(repo)
            (repo / "a.py").write_text("x = 1\n", encoding="utf-8")
            self._commit_all(repo, "mainline")
            subprocess.run(["git", "checkout", "--orphan", "other"], cwd=repo, check=True, capture_output=True)
            (repo / "a.py").write_text("y = 2\n", encoding="utf-8")
            self._commit_all(repo, "other")
            proc = self._run_in_repo(
                repo,
                {"UB_GATES_ADVISORY": "0", "UB_GATES_BASE_REF": "main", "PATH": "/usr/bin:/bin"},
            )
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("outcome=tool_error", self._gate_outcome(repo))
            self.assertNotIn("outcome=skipped_no_merge_base", self._gate_outcome(repo))

    def test_blocking_not_git_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            proc = self._run_in_repo(repo, {"UB_GATES_ADVISORY": "0", "PATH": "/usr/bin:/bin"})
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("outcome=skipped_not_git", self._gate_outcome(repo))

    def test_advisory_not_git_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            proc = self._run_in_repo(repo, {"UB_GATES_ADVISORY": "1", "PATH": "/usr/bin:/bin"})
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("outcome=skipped_not_git", self._gate_outcome(repo))

    def test_blocking_no_scope_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._init_repo(repo)
            (repo / "README.md").write_text("a\n", encoding="utf-8")
            self._commit_all(repo, "base")
            subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
            (repo / "README.md").write_text("b\n", encoding="utf-8")
            self._commit_all(repo, "change")
            proc = self._run_in_repo(
                repo,
                {"UB_GATES_ADVISORY": "0", "UB_GATES_BASE_REF": "main", "PATH": "/usr/bin:/bin"},
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("outcome=skipped_no_scope", self._gate_outcome(repo))

    def _install_quiet_tools(self, repo: Path, bin_dir: Path, crapper: str, dryer: str, mutator: str) -> None:
        bin_dir.mkdir()
        self._tool(bin_dir, "crapper", crapper)
        self._tool(bin_dir, "dryer", dryer)
        self._tool(bin_dir, "mutator", mutator)

    def test_blocking_clean_passes_lines_and_existing_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            crapper_log = repo / "crapper.log"
            mutator_log = repo / "mutator.log"
            self._install_quiet_tools(
                repo,
                bin_dir,
                f'#!/usr/bin/env bash\necho "$@" >> "{crapper_log}"\nmkdir -p .metrics\necho \'{{:entries []}}\' > .metrics/crap.edn\nexit 0\n',
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                f'#!/usr/bin/env bash\necho "$@" >> "{mutator_log}"\nexit 0\n',
            )
            env = self._empty_spans(repo, self._block_env(bin_dir))
            env["UB_GATES_COVERAGE_CMD"] = "mkdir -p target/coverage/python && echo TN: > target/coverage/python/lcov.info"
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("outcome=ran_clean", self._gate_outcome(repo))
            crapper_args = crapper_log.read_text(encoding="utf-8")
            mutator_args = mutator_log.read_text(encoding="utf-8")
            self.assertIn("--use-existing-coverage", crapper_args)
            self.assertIn("lib/a.py", crapper_args)
            self.assertNotIn("--changed", crapper_args)
            self.assertIn("--lines 2", mutator_args)
            self.assertIn("lib/a.py", mutator_args)
            self.assertIn("--lines 2", mutator_args)
            self.assertIn("lib/b.py", mutator_args)
            self.assertIn("--use-existing-coverage", mutator_args)

    def test_blocking_crapper_finding_in_changed_function_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            spec = repo / "fns.json"
            spec.write_text(
                '[{"namespace":"lib.a","name":"f","start_line":1,"end_line":2,"path":"lib/a.py"}]',
                encoding="utf-8",
            )
            crapper = "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "mkdir -p .metrics",
                    "cat > .metrics/crap.edn <<'EDN'",
                    "{:entries [",
                    '  {:name "f", :namespace "lib.a", :complexity 4, :coverage 0.0, :crap 40.0}',
                    "]}",
                    "EDN",
                    "exit 0",
                    "",
                ]
            )
            self._install_quiet_tools(
                repo,
                bin_dir,
                crapper,
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 0\n",
            )
            env = self._block_env(bin_dir)
            env["UB_SCOPE_FUNCTIONS_JSON"] = str(spec)
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=ran_with_findings", outcome)
            self.assertIn("crapper_findings=1", outcome)

    def test_blocking_crapper_debt_only_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            spec = repo / "fns.json"
            spec.write_text(
                "["
                '{"namespace":"lib.a","name":"f","start_line":1,"end_line":2,"path":"lib/a.py"},'
                '{"namespace":"lib.a","name":"old","start_line":10,"end_line":12,"path":"lib/a.py"}'
                "]",
                encoding="utf-8",
            )
            crapper = "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "mkdir -p .metrics",
                    "cat > .metrics/crap.edn <<'EDN'",
                    "{:entries [",
                    '  {:name "f", :namespace "lib.a", :complexity 1, :coverage 0.0, :crap 2.0}',
                    '  {:name "old", :namespace "lib.a", :complexity 4, :coverage 0.0, :crap 40.0}',
                    "]}",
                    "EDN",
                    "exit 0",
                    "",
                ]
            )
            self._install_quiet_tools(
                repo,
                bin_dir,
                crapper,
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 0\n",
            )
            env = self._block_env(bin_dir)
            env["UB_SCOPE_FUNCTIONS_JSON"] = str(spec)
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=ran_clean", outcome)
            self.assertIn("crapper_findings=0", outcome)
            self.assertIn("crapper_debt=1", outcome)

    def test_blocking_dryer_debt_only_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            dryer = "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "mkdir -p .metrics",
                    "cat > .metrics/dry.edn <<'EDN'",
                    "{:candidates [",
                    " {:score 0.95",
                    '  :language "python"',
                    '  :left {:file "lib/a.py", :start-line 10, :end-line 12}',
                    '  :right {:file "lib/b.py", :start-line 10, :end-line 12}',
                    "  :left-nodes 4",
                    "  :right-nodes 4}}",
                    "]}",
                    "EDN",
                    "exit 0",
                    "",
                ]
            )
            self._install_quiet_tools(
                repo,
                bin_dir,
                _EMPTY_CRAP,
                dryer,
                "#!/usr/bin/env bash\nexit 0\n",
            )
            proc = self._run_in_repo(repo, self._empty_spans(repo, self._block_env(bin_dir)))
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=ran_clean", outcome)
            self.assertIn("dryer_findings=0", outcome)
            self.assertIn("dryer_debt=1", outcome)

    def test_blocking_mutator_survivor_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            self._install_quiet_tools(
                repo,
                bin_dir,
                _EMPTY_CRAP,
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 3\n",
            )
            proc = self._run_in_repo(repo, self._empty_spans(repo, self._block_env(bin_dir)))
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=ran_with_findings", outcome)
            self.assertIn("mutator_exit=3", outcome)

    def test_blocking_mutator_baseline_failure_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            self._install_quiet_tools(
                repo,
                bin_dir,
                _EMPTY_CRAP,
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 2\n",
            )
            proc = self._run_in_repo(repo, self._empty_spans(repo, self._block_env(bin_dir)))
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=tool_error", outcome)
            self.assertIn("mutator_exit=2", outcome)

    def test_blocking_mutator_budget_exhausted_does_not_fail(self) -> None:
        # A 1-second wall clock can end inside the scope-lines process, before
        # the mutator creates its log. The stub returns 124 only after that
        # log exists, and the budget stays large enough to reach the first file.
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            mutator_log = repo / "mutator.log"
            self._install_quiet_tools(
                repo,
                bin_dir,
                _EMPTY_CRAP,
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                f'#!/usr/bin/env bash\necho "$@" >> "{mutator_log}"\nsleep 30\nexit 0\n',
            )
            self._tool(
                bin_dir,
                "timeout",
                "\n".join(
                    [
                        "#!/usr/bin/env python3",
                        "import os, signal, subprocess, sys, time",
                        "cmd = sys.argv[2:]",
                        f"log = {str(mutator_log)!r}",
                        "proc = subprocess.Popen(cmd, start_new_session=True)",
                        "deadline = time.time() + 15",
                        "while time.time() < deadline:",
                        "    if os.path.isfile(log) and os.path.getsize(log) > 0:",
                        "        break",
                        "    if proc.poll() is not None:",
                        "        break",
                        "    time.sleep(0.05)",
                        "try:",
                        "    os.killpg(proc.pid, signal.SIGTERM)",
                        "except ProcessLookupError:",
                        "    pass",
                        "proc.wait()",
                        "if not (os.path.isfile(log) and os.path.getsize(log) > 0):",
                        "    sys.stderr.write('mutator log missing\\n')",
                        "    sys.exit(2)",
                        "sys.exit(124)",
                        "",
                    ]
                ),
            )
            env = self._empty_spans(repo, self._block_env(bin_dir))
            env["UB_GATES_MUTATOR_BUDGET_SECS"] = "60"
            summary = repo / "step-summary.md"
            env["GITHUB_STEP_SUMMARY"] = str(summary)
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("mutator_timeout=1", outcome)
            self.assertNotIn("outcome=tool_error", outcome)
            self.assertIn("outcome=ran_clean", outcome)
            first = summary.read_text(encoding="utf-8").splitlines()[0]
            self.assertIn("timeout", first.lower())
            self.assertIn("budget", proc.stdout + proc.stderr)
            self.assertIn("non-blocking", proc.stdout + proc.stderr)
            ran = mutator_log.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(ran), 1)
            self.assertIn("--lines", ran[0])

    def test_blocking_coverage_command_failure_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            crapper_log = repo / "crapper.log"
            self._install_quiet_tools(
                repo,
                bin_dir,
                f'#!/usr/bin/env bash\necho ran >> "{crapper_log}"\nexit 0\n',
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 0\n",
            )
            env = self._block_env(bin_dir)
            env["UB_GATES_COVERAGE_CMD"] = "exit 1"
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("outcome=tool_error", self._gate_outcome(repo))
            self.assertFalse(crapper_log.exists())

    def test_blocking_stale_dry_edn_is_removed_before_dryer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            metrics = repo / ".metrics"
            metrics.mkdir()
            (metrics / "dry.edn").write_text(
                "\n".join(
                    [
                        "{:candidates [",
                        " {:score 0.99",
                        '  :language "python"',
                        '  :left {:file "lib/a.py", :start-line 1, :end-line 2}',
                        '  :right {:file "lib/b.py", :start-line 1, :end-line 2}',
                        "  :left-nodes 4",
                        "  :right-nodes 4}}",
                        "]}",
                    ]
                ),
                encoding="utf-8",
            )
            bin_dir = repo / "bin"
            seen = repo / "dryer-saw.log"
            dryer = "\n".join(
                [
                    "#!/usr/bin/env bash",
                    f'if [[ -f .metrics/dry.edn ]]; then echo PRESENT >> "{seen}"; fi',
                    "mkdir -p .metrics",
                    "echo '{:candidates []}' > .metrics/dry.edn",
                    "exit 0",
                    "",
                ]
            )
            self._install_quiet_tools(
                repo,
                bin_dir,
                _EMPTY_CRAP,
                dryer,
                "#!/usr/bin/env bash\nexit 0\n",
            )
            proc = self._run_in_repo(repo, self._empty_spans(repo, self._block_env(bin_dir)))
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse(seen.exists())
            self.assertIn("outcome=ran_clean", self._gate_outcome(repo))
            self.assertIn("dryer_findings=0", self._gate_outcome(repo))

    def test_blocking_scope_keeps_source_and_skips_test_paths(self) -> None:
        included = (
            "lib/app.py",
            "src/widget.tsx",
            "pkg/main.go",
            "java/Main.java",
            "rust/lib.rs",
            "src/latest.py",
            "src/test.py",
        )
        excluded = (
            "tests/test_app.py",
            "pkg/tests/util.py",
            "src/test/helper.py",
            "spec/demo.ts",
            "specs/demo.js",
            "testdata/sample.go",
            "web/__tests__/widget.tsx",
            "pkg/fixtures/sample.py",
            "lib/test_mod.py",
            "lib/mod_test.py",
            "pkg/foo_test.go",
            "web/view.test.ts",
            "web/view.test.tsx",
            "web/view.test.js",
            "web/view.test.jsx",
            "web/view.test.mts",
            "web/view.test.cts",
            "web/view.spec.ts",
            "web/view.spec.tsx",
            "web/view.spec.js",
            "web/view.spec.jsx",
            "web/view.spec.mts",
            "web/view.spec.cts",
            "web/view.spec.mjs",
            "web/view.spec.cjs",
            "web/view.test.mjs",
            "web/view.test.cjs",
            "java/FooTest.java",
            "rust/foo_test.rs",
            "lib/api.pyi",
            "web/types.d.ts",
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._init_repo(repo)
            paths = included + excluded
            self._plant(repo, paths, "v1\n")
            self._commit_all(repo, "base")
            subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
            self._plant(repo, paths, "v2\n")
            self._commit_all(repo, "change")
            bin_dir = repo / "bin"
            crapper_log = repo / "crapper.log"
            self._install_quiet_tools(
                repo,
                bin_dir,
                f'#!/usr/bin/env bash\necho "$@" >> "{crapper_log}"\nmkdir -p .metrics\necho \'{{:entries []}}\' > .metrics/crap.edn\nexit 0\n',
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 0\n",
            )
            proc = self._run_in_repo(repo, self._empty_spans(repo, self._block_env(bin_dir)))
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=ran_clean", outcome)
            self.assertIn(f"scope_files={len(included)}", outcome)
            tokens = crapper_log.read_text(encoding="utf-8").split()
            for rel in included:
                self.assertIn(rel, tokens)
            for rel in excluded:
                self.assertNotIn(rel, tokens)

    def test_blocking_only_test_paths_exit_as_no_scope(self) -> None:
        rels = ("tests/test_app.py", "src/test/helper.py", "lib/mod_test.py")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._init_repo(repo)
            self._plant(repo, rels, "v1\n")
            self._commit_all(repo, "base")
            subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
            self._plant(repo, rels, "v2\n")
            self._commit_all(repo, "change")
            proc = self._run_in_repo(
                repo,
                {"UB_GATES_ADVISORY": "0", "UB_GATES_BASE_REF": "main", "PATH": "/usr/bin:/bin"},
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=skipped_no_scope", outcome)
            self.assertIn("scope_files=0", outcome)

    def test_blocking_missing_lcov_after_coverage_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            crapper_log = repo / "crapper.log"
            self._install_quiet_tools(
                repo,
                bin_dir,
                f'#!/usr/bin/env bash\necho ran >> "{crapper_log}"\nmkdir -p .metrics\necho \'{{:entries []}}\' > .metrics/crap.edn\nexit 0\n',
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 0\n",
            )
            env = self._block_env(bin_dir)
            env["UB_GATES_COVERAGE_CMD"] = "exit 0"
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("outcome=tool_error", self._gate_outcome(repo))
            self.assertFalse(crapper_log.exists())

    def test_blocking_empty_lcov_after_coverage_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            crapper_log = repo / "crapper.log"
            self._install_quiet_tools(
                repo,
                bin_dir,
                f'#!/usr/bin/env bash\necho ran >> "{crapper_log}"\nmkdir -p .metrics\necho \'{{:entries []}}\' > .metrics/crap.edn\nexit 0\n',
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 0\n",
            )
            env = self._block_env(bin_dir)
            env["UB_GATES_COVERAGE_CMD"] = "mkdir -p target/coverage/python && : > target/coverage/python/lcov.info"
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("outcome=tool_error", self._gate_outcome(repo))
            self.assertFalse(crapper_log.exists())

    def test_blocking_nil_crap_on_changed_function_with_coverage_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            spec = repo / "fns.json"
            spec.write_text(
                '[{"namespace":"lib.a","name":"f","start_line":1,"end_line":2,"path":"lib/a.py"}]',
                encoding="utf-8",
            )
            crapper = "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "mkdir -p .metrics",
                    "cat > .metrics/crap.edn <<'EDN'",
                    "{:entries [",
                    '  {:name "f", :namespace "lib.a", :complexity 1, :coverage nil, :crap nil}',
                    "]}",
                    "EDN",
                    "exit 0",
                    "",
                ]
            )
            self._install_quiet_tools(
                repo,
                bin_dir,
                crapper,
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 0\n",
            )
            env = self._block_env(bin_dir)
            env["UB_SCOPE_FUNCTIONS_JSON"] = str(spec)
            env["UB_GATES_COVERAGE_CMD"] = "mkdir -p target/coverage/python && echo TN: > target/coverage/python/lcov.info"
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("outcome=tool_error", self._gate_outcome(repo))

    def test_blocking_unjoined_crap_row_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            spec = repo / "fns.json"
            spec.write_text("[]", encoding="utf-8")
            crapper = "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "mkdir -p .metrics",
                    "cat > .metrics/crap.edn <<'EDN'",
                    "{:entries [",
                    '  {:name "f", :namespace "lib.a", :complexity 4, :coverage 0.0, :crap 40.0}',
                    "]}",
                    "EDN",
                    "exit 2",
                    "",
                ]
            )
            self._install_quiet_tools(
                repo,
                bin_dir,
                crapper,
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 0\n",
            )
            env = self._block_env(bin_dir)
            env["UB_SCOPE_FUNCTIONS_JSON"] = str(spec)
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=tool_error", outcome)
            self.assertNotIn("outcome=ran_clean", outcome)

    def test_blocking_crapper_exit_0_without_edn_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            self._install_quiet_tools(
                repo,
                bin_dir,
                "#!/usr/bin/env bash\nexit 0\n",
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 0\n",
            )
            proc = self._run_in_repo(repo, self._block_env(bin_dir))
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("outcome=tool_error", self._gate_outcome(repo))

    def test_blocking_dryer_unexpected_exit_without_edn_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            self._install_quiet_tools(
                repo,
                bin_dir,
                _EMPTY_CRAP,
                "#!/usr/bin/env bash\nexit 9\n",
                "#!/usr/bin/env bash\nexit 0\n",
            )
            proc = self._run_in_repo(repo, self._empty_spans(repo, self._block_env(bin_dir)))
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=tool_error", outcome)
            self.assertIn("dryer_exit=9", outcome)

    def test_direct_call_defaults_to_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._init_repo(repo)
            (repo / "lib").mkdir()
            (repo / "lib" / "a.py").write_text("x = 1\n", encoding="utf-8")
            self._commit_all(repo, "base")
            subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
            (repo / "lib" / "a.py").write_text("x = 2\n", encoding="utf-8")
            self._commit_all(repo, "change")
            proc = self._run_in_repo(repo, {"UB_GATES_BASE_REF": "main", "PATH": "/usr/bin:/bin"})
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("outcome=skipped_tools_missing", self._gate_outcome(repo))
            self.assertIn("advisory=0", self._gate_outcome(repo))

    def test_blocking_skip_mutator_is_not_ran_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            self._install_quiet_tools(
                repo,
                bin_dir,
                _EMPTY_CRAP,
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\necho ran >&2\nexit 0\n",
            )
            env = self._empty_spans(repo, self._block_env(bin_dir))
            env["UB_GATES_SKIP_MUTATOR"] = "1"
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=skipped_mutator", outcome)
            self.assertNotIn("outcome=ran_clean", outcome)
            self.assertIn("mutator_skipped=1", outcome)

    def test_blocking_cursor_agent_skip_is_not_ran_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            self._install_quiet_tools(
                repo,
                bin_dir,
                _EMPTY_CRAP,
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\necho ran >&2\nexit 0\n",
            )
            env = self._empty_spans(repo, self._block_env(bin_dir))
            env["CURSOR_AGENT"] = "1"
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=skipped_mutator", outcome)
            self.assertNotIn("outcome=ran_clean", outcome)

    def test_advisory_skip_mutator_is_skipped_mutator_and_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            self._install_quiet_tools(
                repo,
                bin_dir,
                _EMPTY_CRAP,
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\necho ran >&2\nexit 0\n",
            )
            env = self._empty_spans(repo, self._block_env(bin_dir))
            env["UB_GATES_ADVISORY"] = "1"
            env["UB_GATES_SKIP_MUTATOR"] = "1"
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=skipped_mutator", outcome)
            self.assertNotIn("outcome=ran_clean", outcome)
            self.assertIn("mutator_skipped=1", outcome)
            self.assertIn("advisory=1", outcome)
            self.assertIn("gate_miss=1", outcome)

    def test_blocking_name_only_diff_failure_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            real_git = shutil.which("git")
            self.assertIsNotNone(real_git)
            wrapper = bin_dir / "git"
            bin_dir.mkdir()
            wrapper.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        'if [[ "$1" == "diff" ]]; then',
                        '  for arg in "$@"; do',
                        '    if [[ "${arg}" == "--name-only" ]]; then',
                        "      echo name-only-failed >&2",
                        "      exit 1",
                        "    fi",
                        "  done",
                        "fi",
                        f'exec {real_git} "$@"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            wrapper.chmod(0o755)
            proc = self._run_in_repo(
                repo,
                {"UB_GATES_ADVISORY": "0", "UB_GATES_BASE_REF": "main", "PATH": f"{bin_dir}:/usr/bin:/bin"},
            )
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=tool_error", outcome)
            self.assertNotIn("outcome=skipped_no_scope", outcome)

    def test_blocking_shallow_fetch_uses_base_ref_without_depth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            origin = Path(tmp) / "origin"
            origin.mkdir()
            self._init_repo(origin)
            lib = origin / "lib"
            lib.mkdir()
            (lib / "a.py").write_text("v1\n", encoding="utf-8")
            self._commit_all(origin, "base")
            (lib / "a.py").write_text("v2\n", encoding="utf-8")
            self._commit_all(origin, "main tip")
            subprocess.run(
                ["git", "checkout", "-b", "feat", "HEAD~1"],
                cwd=origin,
                check=True,
                capture_output=True,
            )
            (lib / "a.py").write_text("v3\n", encoding="utf-8")
            self._commit_all(origin, "feat")
            clone = Path(tmp) / "clone"
            subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", "feat", origin.as_uri(), str(clone)],
                check=True,
                capture_output=True,
            )
            log = clone / "git-args.log"
            bin_dir = clone / "bin"
            bin_dir.mkdir()
            real_git = shutil.which("git")
            (bin_dir / "git").write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        f'printf "%s\\n" "$*" >> "{log}"',
                        f'exec {real_git} "$@"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            (bin_dir / "git").chmod(0o755)
            proc = self._run_in_repo(
                clone,
                {
                    "UB_GATES_ADVISORY": "0",
                    "UB_GATES_BASE_REF": "origin/main",
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                },
            )
            fetched = log.read_text(encoding="utf-8")
            self.assertNotIn("--depth", fetched)
            self.assertIn("main", fetched)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(clone)
            self.assertIn("outcome=skipped_tools_missing", outcome)
            self.assertNotIn("outcome=skipped_no_merge_base", outcome)
            self.assertNotIn("outcome=skipped_no_scope", outcome)

    def test_base_ref_fetch_source_has_no_depth_limit(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("--depth=1", text)
        self.assertNotIn("--depth 1", text)
        self.assertIn("UB_GATES_BASE_REF", text)

    def test_blocking_dryer_unexpected_exit_with_edn_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            dryer = "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "mkdir -p .metrics",
                    "echo '{:candidates []}' > .metrics/dry.edn",
                    "exit 9",
                    "",
                ]
            )
            self._install_quiet_tools(repo, bin_dir, _EMPTY_CRAP, dryer, "#!/usr/bin/env bash\nexit 0\n")
            proc = self._run_in_repo(repo, self._empty_spans(repo, self._block_env(bin_dir)))
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=tool_error", outcome)
            self.assertIn("dryer_exit=9", outcome)

    def test_blocking_dryer_overlap_on_changed_line_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            dryer = "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "mkdir -p .metrics",
                    "cat > .metrics/dry.edn <<'EDN'",
                    "{:candidates [",
                    " {:score 0.91",
                    '  :language "python"',
                    '  :left {:file "lib/a.py", :start-line 1, :end-line 2}',
                    '  :right {:file "lib/b.py", :start-line 40, :end-line 44}',
                    "  :left-nodes 4",
                    "  :right-nodes 4}}",
                    "]}",
                    "EDN",
                    "exit 0",
                    "",
                ]
            )
            self._install_quiet_tools(repo, bin_dir, _EMPTY_CRAP, dryer, "#!/usr/bin/env bash\nexit 0\n")
            proc = self._run_in_repo(repo, self._empty_spans(repo, self._block_env(bin_dir)))
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=ran_with_findings", outcome)
            self.assertIn("dryer_findings=1", outcome)

    def test_blocking_crapper_exit_2_debt_only_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            spec = repo / "fns.json"
            spec.write_text(
                "["
                '{"namespace":"lib.a","name":"f","start_line":1,"end_line":2,"path":"lib/a.py"},'
                '{"namespace":"lib.a","name":"old","start_line":10,"end_line":12,"path":"lib/a.py"}'
                "]",
                encoding="utf-8",
            )
            crapper = "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "mkdir -p .metrics",
                    "cat > .metrics/crap.edn <<'EDN'",
                    "{:entries [",
                    '  {:name "f", :namespace "lib.a", :complexity 1, :coverage 0.0, :crap 2.0}',
                    '  {:name "old", :namespace "lib.a", :complexity 4, :coverage 0.0, :crap 40.0}',
                    "]}",
                    "EDN",
                    "exit 2",
                    "",
                ]
            )
            self._install_quiet_tools(
                repo,
                bin_dir,
                crapper,
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 0\n",
            )
            env = self._block_env(bin_dir)
            env["UB_SCOPE_FUNCTIONS_JSON"] = str(spec)
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=ran_clean", outcome)
            self.assertIn("crapper_findings=0", outcome)
            self.assertIn("crapper_debt=1", outcome)
            self.assertIn("crapper_exit=2", outcome)

    def test_blocking_unparsed_dryer_row_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            dryer = "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "mkdir -p .metrics",
                    "cat > .metrics/dry.edn <<'EDN'",
                    '{:candidates [{:score 0.91 :language "python" :left {:file "lib/a.py"} :right {:file "lib/b.py"}}]}',
                    "EDN",
                    "exit 0",
                    "",
                ]
            )
            self._install_quiet_tools(repo, bin_dir, _EMPTY_CRAP, dryer, "#!/usr/bin/env bash\nexit 0\n")
            proc = self._run_in_repo(repo, self._empty_spans(repo, self._block_env(bin_dir)))
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("outcome=tool_error", self._gate_outcome(repo))

    def test_blocking_one_sided_dryer_row_at_threshold_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            dryer = "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "mkdir -p .metrics",
                    "cat > .metrics/dry.edn <<'EDN'",
                    "{:candidates [",
                    " {:score 0.8",
                    '  :language "python"',
                    '  :left {:file "lib/a.py", :start-line 10, :end-line 12}',
                    '  :right {:file "lib/b.py"}',
                    "  :left-nodes 4",
                    "  :right-nodes 4}}",
                    "]}",
                    "EDN",
                    "exit 0",
                    "",
                ]
            )
            self._install_quiet_tools(repo, bin_dir, _EMPTY_CRAP, dryer, "#!/usr/bin/env bash\nexit 0\n")
            proc = self._run_in_repo(repo, self._empty_spans(repo, self._block_env(bin_dir)))
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=tool_error", outcome)
            self.assertNotIn("outcome=ran_clean", outcome)
            self.assertNotIn("dryer_debt=1", outcome)

    def test_blocking_unjoined_nil_crap_with_coverage_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            spec = repo / "fns.json"
            spec.write_text("[]", encoding="utf-8")
            crapper = "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "mkdir -p .metrics",
                    "cat > .metrics/crap.edn <<'EDN'",
                    "{:entries [",
                    '  {:name "f", :namespace "lib.a", :complexity 1, :coverage nil, :crap nil}',
                    "]}",
                    "EDN",
                    "exit 0",
                    "",
                ]
            )
            self._install_quiet_tools(
                repo,
                bin_dir,
                crapper,
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 0\n",
            )
            env = self._block_env(bin_dir)
            env["UB_SCOPE_FUNCTIONS_JSON"] = str(spec)
            env["UB_GATES_COVERAGE_CMD"] = "mkdir -p target/coverage/python && echo TN: > target/coverage/python/lcov.info"
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("outcome=tool_error", self._gate_outcome(repo))

    def test_declaration_files_are_outside_gate_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._init_repo(repo)
            self._plant(repo, ("lib/api.pyi", "web/types.d.ts"), "v1\n")
            self._commit_all(repo, "base")
            subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
            self._plant(repo, ("lib/api.pyi", "web/types.d.ts"), "v2\n")
            self._commit_all(repo, "change")
            proc = self._run_in_repo(
                repo,
                {"UB_GATES_ADVISORY": "0", "UB_GATES_BASE_REF": "main", "PATH": "/usr/bin:/bin"},
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=skipped_no_scope", outcome)
            self.assertIn("scope_files=0", outcome)

    def _advisory_repo(self, tmp: str) -> tuple[Path, Path]:
        repo = Path(tmp)
        self._init_repo(repo)
        lib = repo / "lib"
        lib.mkdir()
        (lib / "a.py").write_text(
            "def changed():\n    return 1\n\ndef old():\n    return 0\n",
            encoding="utf-8",
        )
        self._commit_all(repo, "base")
        subprocess.run(["git", "checkout", "-b", "feat"], cwd=repo, check=True, capture_output=True)
        (lib / "a.py").write_text(
            "def changed():\n    return 2\n\ndef old():\n    return 0\n",
            encoding="utf-8",
        )
        self._commit_all(repo, "change")
        bin_dir = repo / "bin"
        bin_dir.mkdir()
        return repo, bin_dir

    def _advisory_tools(self, repo: Path, bin_dir: Path, mutator: str, dry: str) -> dict[str, str]:
        spans = repo / "spans.json"
        spans.write_text(
            "["
            '{"namespace":"pkg","name":"changed","start_line":1,"end_line":2,"path":"lib/a.py"},'
            '{"namespace":"pkg","name":"old","start_line":4,"end_line":5,"path":"lib/a.py"}'
            "]",
            encoding="utf-8",
        )
        crapper = "\n".join(
            [
                "#!/usr/bin/env bash",
                "mkdir -p .metrics",
                "cat > .metrics/crap.edn <<'EDN'",
                "{:entries [",
                '  {:name "changed", :namespace "pkg", :complexity 1, :coverage 0.0, :crap 2.0}',
                '  {:name "old", :namespace "pkg", :complexity 4, :coverage 0.0, :crap 30.0}',
                "]}",
                "EDN",
                "exit 0",
                "",
            ]
        )
        dryer = "\n".join(
            [
                "#!/usr/bin/env bash",
                "mkdir -p .metrics",
                "cat > .metrics/dry.edn <<'EDN'",
                dry,
                "EDN",
                "exit 0",
                "",
            ]
        )
        self._tool(bin_dir, "crapper", crapper)
        self._tool(bin_dir, "dryer", dryer)
        self._tool(bin_dir, "mutator", mutator)
        env = {
            "UB_GATES_ADVISORY": "1",
            "UB_GATES_BASE_REF": "main",
            "UB_GATES_MUTATOR_BUDGET_SECS": "1200",
            "UB_GATES_MUTATOR_TEST_CMD": "python -m unittest tests.test_ub_changed_scope",
            "UB_SCOPE_FUNCTIONS_JSON": str(spans),
            "PATH": f"{bin_dir}:/usr/bin:/bin",
        }
        return env

    def test_advisory_joins_scope_and_budgets_mutator(self) -> None:
        dry = "\n".join(
            [
                "{:candidates [",
                " {:score 0.91",
                '  :language "python"',
                '  :left {:file "lib/a.py", :start-line 4, :end-line 5}',
                '  :right {:file "lib/a.py", :start-line 4, :end-line 5}}',
                "]}",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo, bin_dir = self._advisory_repo(tmp)
            log = repo / "mutator.log"
            env = self._advisory_tools(
                repo,
                bin_dir,
                f'#!/usr/bin/env bash\necho "$@" >> "{log}"\nexit 0\n',
                dry,
            )
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            text = proc.stdout + proc.stderr
            self.assertIn("scope join crap findings=0 debt=1", text)
            self.assertIn("scope join dry findings=0 debt=1", text)
            self.assertIn("mutator budget 1200s", text)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=ran_clean", outcome)
            self.assertIn("advisory=1", outcome)
            self.assertIn("crapper_debt=1", outcome)
            self.assertIn("dryer_debt=1", outcome)
            self.assertIn("crapper_findings=0", outcome)
            self.assertIn("dryer_findings=0", outcome)
            self.assertIn("mutator_budget_secs=1200", outcome)
            logged = log.read_text(encoding="utf-8")
            self.assertIn("--lines", logged)
            self.assertIn("--test-command", logged)
            self.assertIn("lib/a.py", logged)
            self.assertNotIn("--lines 4", logged)

    def test_advisory_changed_line_finding_exits_zero(self) -> None:
        dry = "\n".join(
            [
                "{:candidates [",
                " {:score 0.91",
                '  :language "python"',
                '  :left {:file "lib/a.py", :start-line 1, :end-line 2}',
                '  :right {:file "lib/a.py", :start-line 1, :end-line 2}}',
                "]}",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo, bin_dir = self._advisory_repo(tmp)
            log = repo / "mutator.log"
            env = self._advisory_tools(
                repo,
                bin_dir,
                f'#!/usr/bin/env bash\necho "$@" >> "{log}"\nexit 0\n',
                dry,
            )
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=ran_with_findings", outcome)
            self.assertIn("dryer_findings=1", outcome)

    def test_advisory_mutator_exit_one_is_tool_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, bin_dir = self._advisory_repo(tmp)
            env = self._advisory_tools(
                repo,
                bin_dir,
                "#!/usr/bin/env bash\nexit 1\n",
                "{:candidates []}\n",
            )
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=tool_error", outcome)
            self.assertIn("mutator_exit=1", outcome)
            self.assertIn("tool_error=1", outcome)
            env["UB_GATES_ADVISORY"] = "0"
            blocking = self._run_in_repo(repo, env)
            self.assertEqual(blocking.returncode, 1, blocking.stdout + blocking.stderr)
            blocked = self._gate_outcome(repo)
            self.assertIn("outcome=tool_error", blocked)
            self.assertIn("mutator_exit=1", blocked)

    def test_scope_lines_failure_records_tool_error(self) -> None:
        wrapper = "\n".join(
            [
                "#!/usr/bin/env bash",
                'if [[ "${2:-}" == "lines" ]]; then',
                "  echo 'scope lines failed' >&2",
                "  exit 9",
                "fi",
                "exec /usr/bin/python3 \"$@\"",
                "",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo, bin_dir = self._advisory_repo(tmp)
            env = self._advisory_tools(
                repo,
                bin_dir,
                "#!/usr/bin/env bash\nexit 0\n",
                "{:candidates []}\n",
            )
            self._tool(bin_dir, "python3", wrapper)
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=tool_error", outcome)
            self.assertIn("tool_error=1", outcome)
            self.assertNotEqual(proc.returncode, 9)
            env["UB_GATES_ADVISORY"] = "0"
            blocking = self._run_in_repo(repo, env)
            self.assertEqual(blocking.returncode, 1, blocking.stdout + blocking.stderr)
            self.assertIn("outcome=tool_error", self._gate_outcome(repo))


if __name__ == "__main__":
    unittest.main()
