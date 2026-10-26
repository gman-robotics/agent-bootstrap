"""Tests for scripts/run_ub_gates_ci.sh (merge-base scope, tool-missing gate miss)."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "run_ub_gates_ci.sh"


class RunUbGatesCiTests(unittest.TestCase):
    def _run_in_repo(self, repo: Path, env: dict | None = None) -> subprocess.CompletedProcess:
        run_env = os.environ.copy()
        run_env["UB_GATES_OUTCOME_FILE"] = str(repo / ".metrics" / "ub-gates-outcome.txt")
        if env:
            run_env.update(env)
        return subprocess.run(
            ["/bin/bash", str(SCRIPT)],
            cwd=repo,
            env=run_env,
            capture_output=True,
            text=True,
        )

    def test_tools_missing_with_python_scope_is_gate_miss(self):
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

            proc = self._run_in_repo(repo, {"UB_GATES_BASE_REF": "main"})
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            outcome = (repo / ".metrics" / "ub-gates-outcome.txt").read_text(encoding="utf-8")
            self.assertIn("outcome=skipped_tools_missing", outcome)
            self.assertIn("gate_miss=1", outcome)

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


if __name__ == "__main__":
    unittest.main()
