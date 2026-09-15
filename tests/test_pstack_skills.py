"""Mechanical checks for GMA-48 ported pstack skills."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validate_pstack_skill.py"

PSTACK_SKILLS = (
    "architect",
    "arena",
    "swarm",
    "blast-radius",
    "interrogate",
    "figure-it-out",
    "show-me-your-work",
    "create-verification-skill",
    "maintain-verification-skill",
    "how",
    "why",
    "teach",
    "technical-writing",
    "unslop",
    "reflect",
    "automate-me",
    "pstack-principles",
)


class PstackSkillsTests(unittest.TestCase):
    def test_validator_script_exists(self) -> None:
        self.assertTrue(VALIDATOR.is_file())

    def test_all_pstack_skills_pass_structure_validation(self) -> None:
        for name in PSTACK_SKILLS:
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), name],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                result.returncode,
                0,
                f"{name}: {result.stderr or result.stdout}",
            )

    def test_pstack_principles_carve_out_blocks_gate_bypass_language(self) -> None:
        text = (REPO_ROOT / "skills" / "pstack-principles" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("never-block-on-the-human", text)
        self.assertIn("Approve", text)
        self.assertIn("Reject", text)
        self.assertIn("does NOT override", text)


if __name__ == "__main__":
    unittest.main()
