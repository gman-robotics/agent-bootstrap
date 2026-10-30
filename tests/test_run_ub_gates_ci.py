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
            self.assertIn("outcome=skipped_no_merge_base", self._gate_outcome(repo))

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
                f'#!/usr/bin/env bash\necho "$@" >> "{crapper_log}"\nexit 0\n',
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                f'#!/usr/bin/env bash\necho "$@" >> "{mutator_log}"\nexit 0\n',
            )
            env = self._block_env(bin_dir)
            env["UB_GATES_COVERAGE_CMD"] = "exit 0"
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
                "#!/usr/bin/env bash\nexit 0\n",
                dryer,
                "#!/usr/bin/env bash\nexit 0\n",
            )
            proc = self._run_in_repo(repo, self._block_env(bin_dir))
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
                "#!/usr/bin/env bash\nexit 0\n",
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 3\n",
            )
            proc = self._run_in_repo(repo, self._block_env(bin_dir))
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
                "#!/usr/bin/env bash\nexit 0\n",
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                "#!/usr/bin/env bash\nexit 2\n",
            )
            proc = self._run_in_repo(repo, self._block_env(bin_dir))
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("outcome=tool_error", outcome)
            self.assertIn("mutator_exit=2", outcome)

    def test_blocking_mutator_budget_exhausted_does_not_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._two_file_repo(repo)
            bin_dir = repo / "bin"
            mutator_log = repo / "mutator.log"
            self._install_quiet_tools(
                repo,
                bin_dir,
                "#!/usr/bin/env bash\nexit 0\n",
                "#!/usr/bin/env bash\nmkdir -p .metrics\necho '{:candidates []}' > .metrics/dry.edn\nexit 0\n",
                f'#!/usr/bin/env bash\necho "$@" >> "{mutator_log}"\nsleep 30\nexit 0\n',
            )
            env = self._block_env(bin_dir)
            env["UB_GATES_MUTATOR_BUDGET_SECS"] = "1"
            proc = self._run_in_repo(repo, env)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            outcome = self._gate_outcome(repo)
            self.assertIn("mutator_timeout=1", outcome)
            self.assertNotIn("outcome=tool_error", outcome)
            self.assertIn("budget", proc.stdout + proc.stderr)
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
                "#!/usr/bin/env bash\nexit 0\n",
                dryer,
                "#!/usr/bin/env bash\nexit 0\n",
            )
            proc = self._run_in_repo(repo, self._block_env(bin_dir))
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse(seen.exists())
            self.assertIn("outcome=ran_clean", self._gate_outcome(repo))
            self.assertIn("dryer_findings=0", self._gate_outcome(repo))


if __name__ == "__main__":
    unittest.main()
