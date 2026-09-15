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

    def test_validator_rejects_invalid_yaml_frontmatter(self) -> None:
        skill_md = REPO_ROOT / "skills" / "how" / "SKILL.md"
        original = skill_md.read_text(encoding="utf-8")
        broken = original.replace(
            "description: >-",
            "description: [unclosed",
            1,
        )
        skill_md.write_text(broken, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "how"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid YAML frontmatter", result.stderr)
        finally:
            skill_md.write_text(original, encoding="utf-8")

    def test_validator_rejects_cursor_leftover_tokens(self) -> None:
        skill_md = REPO_ROOT / "skills" / "swarm" / "SKILL.md"
        original = skill_md.read_text(encoding="utf-8")
        poisoned = original + "\n.cursor/skills/test\n"
        skill_md.write_text(poisoned, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "swarm"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn(".cursor/skills", result.stderr)
        finally:
            skill_md.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
