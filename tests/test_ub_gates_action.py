"""Text checks for .github/actions/ub-gates/action.yml."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTION = REPO_ROOT / ".github" / "actions" / "ub-gates" / "action.yml"
_UPLOAD_PIN = re.compile(r"actions/upload-artifact@([0-9a-f]{40})\s+#\s+v4\.\d+\.\d+")


class UbGatesActionTests(unittest.TestCase):
    def test_lock_checkout_verifies_head_and_uploads_metrics(self) -> None:
        text = ACTION.read_text(encoding="utf-8")
        self.assertIn("git rev-parse HEAD", text)
        pin = _UPLOAD_PIN.search(text)
        self.assertIsNotNone(pin, "upload-artifact must be pinned to a 40-hex SHA")
        self.assertEqual(len(pin.group(1)), 40)
        self.assertEqual(pin.group(1), "ea165f8d65b6e75b540449e92b4886f43607fa02")
        self.assertNotIn("actions/upload-artifact@v", text)
        self.assertIn("if: always()", text)
        self.assertIn(".metrics/", text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("UB_GATES_HUB_PATH: ${{ inputs.hub-path }}", text)
        runs = text.split("runs:", 1)[1]
        for part in runs.split("run: |")[1:]:
            script = part.split("\n    - ")[0]
            self.assertNotIn("inputs.hub-path", script)
        checkout = text.split("git -C", 1)[1]
        verify_at = checkout.find("rev-parse HEAD")
        self.assertGreater(verify_at, checkout.find("checkout --detach"))


if __name__ == "__main__":
    unittest.main()
