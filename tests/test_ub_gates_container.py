"""Static checks for scripts/ub_gates_container.sh. These tests do not run docker."""

import subprocess
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


if __name__ == "__main__":
    unittest.main()
