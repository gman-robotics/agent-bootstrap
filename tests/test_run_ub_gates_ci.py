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


class RunUbGatesCiTests(unittest.TestCase):
    def _run_in_repo(self, repo: Path, env: dict | None = None) -> subprocess.CompletedProcess:
        run_env = os.environ.copy()
        run_env["UB_GATES_OUTCOME_FILE"] = str(repo / ".metrics" / "ub-gates-outcome.txt")
        run_env.pop("GITHUB_STEP_SUMMARY", None)
        preserve_cursor_agent = env is not None and "CURSOR_AGENT" in env
        if env:
            run_env.update(env)
        if not preserve_cursor_agent:
            run_env.pop("CURSOR_AGENT", None)
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
                {"UB_GATES_BASE_REF": "main", "PATH": f"{bin_dir}:/usr/bin:/bin"},
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
                crapper_body="#!/usr/bin/env bash\nexit 0\n",
                dryer_body="""#!/usr/bin/env bash
mkdir -p .metrics
cat > .metrics/dry.edn <<'EDN'
{:candidates [{:score 0.85 :language "python"}]}
EDN
exit 0
""",
                mutator_body="#!/usr/bin/env bash\nexit 0\n",
            )
            proc = self._run_in_repo(
                repo,
                {"UB_GATES_BASE_REF": "main", "PATH": f"{bin_dir}:/usr/bin:/bin"},
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
                {"UB_GATES_BASE_REF": "main", "PATH": f"{bin_dir}:/usr/bin:/bin"},
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
                {"UB_GATES_BASE_REF": "main", "PATH": f"{bin_dir}:/usr/bin:/bin"},
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
                crapper_body="#!/usr/bin/env bash\nexit 0\n",
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
                {
                    "UB_GATES_BASE_REF": "main",
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                    "CURSOR_AGENT": "1",
                },
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")
            self.assertIn("mutator_skipped=1", outcome)
            self.assertFalse(log.exists())

    def test_cursor_agent_with_github_actions_runs_mutator(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, bin_dir = self._mock_repo_with_tools(
                tmp,
                crapper_body="#!/usr/bin/env bash\nexit 0\n",
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
                {
                    "UB_GATES_BASE_REF": "main",
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                    "CURSOR_AGENT": "1",
                    "GITHUB_ACTIONS": "true",
                },
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")
            self.assertIn("mutator_exit=0", outcome)
            self.assertNotIn("mutator_skipped=1", outcome)
            self.assertTrue(log.read_text(encoding="utf-8").strip() == "ran")


if __name__ == "__main__":
    unittest.main()
