"""Checks for scripts/ub_gates_container.sh. These tests do not run docker."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "ub_gates_container.sh"


class UbGatesContainerTests(unittest.TestCase):
    def test_bash_n_accepts_the_script(self) -> None:
        proc = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_help_describes_throwaway_container(self) -> None:
        proc = subprocess.run(["bash", str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Usage:", proc.stdout)
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("docker run", text)
        self.assertIn("--rm", text)
        self.assertIn("rust:1.83", text)
        self.assertIn(":ro", text)
        self.assertIn("uv venv", text)
        self.assertIn("UB_GATES_ADVISORY=0", text)

    def test_docker_stub_records_passthrough_mounts_and_safe_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stub_dir = root / "bin"
            stub_dir.mkdir()
            record = root / "docker-record"
            record.mkdir()
            stub = stub_dir / "docker"
            stub.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        f'printf "%s\\n" "$@" > "{record / "argv"}"',
                        f'cat > "{record / "stdin"}"',
                        "exit 0",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            stub.chmod(0o755)
            work = root / "work"
            work.mkdir()
            main_git = root / "main-git"
            main_git.mkdir()
            metrics = root / "metrics"
            env = os.environ.copy()
            env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
            env["UB_GATES_COVERAGE_CMD"] = "echo coverage marker"
            env["UB_GATES_MUTATOR_TEST_CMD"] = "echo mutator marker"
            env["UB_GATES_BASE_REF"] = "origin/release"
            proc = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    "--worktree",
                    str(work),
                    "--main-git",
                    str(main_git),
                    "--metrics-dir",
                    str(metrics),
                ],
                env=env,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            argv = (record / "argv").read_text(encoding="utf-8")
            stdin = (record / "stdin").read_text(encoding="utf-8")
            recorded = argv + "\n" + stdin
            self.assertIn("--rm", recorded)
            self.assertIn("rust:1.83", recorded)
            self.assertIn(f"{work}:/work:ro", recorded)
            self.assertIn(f"{main_git}:{main_git}:ro", recorded)
            self.assertIn("UB_GATES_ADVISORY=0", recorded)
            self.assertIn("UB_GATES_BASE_REF=origin/release", recorded)
            self.assertIn("UB_GATES_COVERAGE_CMD=echo coverage marker", recorded)
            self.assertIn("UB_GATES_MUTATOR_TEST_CMD=echo mutator marker", recorded)
            self.assertIn("git config --global --add safe.directory", recorded)


if __name__ == "__main__":
    unittest.main()
