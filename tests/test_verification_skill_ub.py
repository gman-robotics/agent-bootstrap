"""GMA-410: create/maintain verification skills document ub gates in verify-ci."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class VerificationSkillUbTests(unittest.TestCase):
    def test_create_verification_skill_requires_ub_ci_bundle(self) -> None:
        text = (REPO_ROOT / "skills" / "create-verification-skill" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("verify-ci-ub-gates.sh", text)
        self.assertIn("ran_clean", text)
        self.assertIn("tool_error", text)
        self.assertIn("merge-base", text)
        ref = REPO_ROOT / "skills" / "create-verification-skill" / "references" / "verify-ci-ub-gates.sh"
        self.assertTrue(ref.is_file())
        ref_text = ref.read_text(encoding="utf-8")
        self.assertIn("run_ub_gates_report.sh", ref_text)
        self.assertNotIn("dryer --changed", ref_text)
        self.assertNotIn("crapper --changed", ref_text)

    def test_maintain_verification_skill_audits_ub_steps(self) -> None:
        text = (REPO_ROOT / "skills" / "maintain-verification-skill" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("ub-mode verify-ci hygiene", text)
        self.assertIn("tool_error", text)
        self.assertIn("merge-base", text)

    def test_run_ub_gates_report_wrapper_is_advisory(self) -> None:
        report = (REPO_ROOT / "scripts" / "run_ub_gates_report.sh").read_text(encoding="utf-8")
        self.assertIn("UB_GATES_ADVISORY=1", report)
        self.assertIn("run_ub_gates_ci.sh", report)


if __name__ == "__main__":
    unittest.main()
