"""Text checks for .github/actions/ub-gates/action.yml."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTION = REPO_ROOT / ".github" / "actions" / "ub-gates" / "action.yml"


class UbGatesActionTests(unittest.TestCase):
    def test_lock_checkout_verifies_head_and_uploads_metrics(self) -> None:
        text = ACTION.read_text(encoding="utf-8")
        self.assertIn("git rev-parse HEAD", text)
        self.assertIn("actions/upload-artifact@", text)
        self.assertIn("if: always()", text)
        self.assertIn(".metrics/", text)
        checkout = text.split("git -C", 1)[1]
        verify_at = checkout.find("rev-parse HEAD")
        self.assertGreater(verify_at, checkout.find("checkout --detach"))


if __name__ == "__main__":
    unittest.main()
