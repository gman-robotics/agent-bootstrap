import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SHOW_ME_SKILL_MD = REPO_ROOT / "skills" / "show-me" / "SKILL.md"
REPLY_CONTRACT_SKILL_MD = REPO_ROOT / "skills" / "reply-contract" / "SKILL.md"
PHOTON_SHOW_ME_MD = REPO_ROOT / "skills" / "reply-contract" / "references" / "photon-show-me.md"
GROK_SHOW_ME_SKILL_MD = REPO_ROOT / ".grok" / "skills" / "show-me" / "SKILL.md"

REAL_PATH_TOKEN = "skills/show-me/SKILL.md"
FICTIONAL_PAIRING_LINE = "Pair with **show-me** (trees / stacks / diffs)."


class ShowMeSkillTests(unittest.TestCase):
    """Mechanical check that show-me exists and reply-contract's pairing line
    points at the real skill path, not a fictional name.

    This is the black-box-agent-qa evidence for this skill: the task requirement
    ("reply-contract keeps voice ... it LOADS skills/show-me/SKILL.md for the one
    visual. Change the pairing line from fiction to a real path.") is a literal,
    checkable fact about the committed files, not a description of intent.
    """

    def test_show_me_skill_file_exists(self) -> None:
        self.assertTrue(
            SHOW_ME_SKILL_MD.is_file(), f"missing {SHOW_ME_SKILL_MD}"
        )

    def test_show_me_frontmatter_declares_the_skill_name_and_version(self) -> None:
        text = SHOW_ME_SKILL_MD.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: show-me\n"))
        self.assertIn("version: 1.0.0", text)

    def test_reply_contract_pairing_line_points_at_the_real_show_me_path(self) -> None:
        text = REPLY_CONTRACT_SKILL_MD.read_text(encoding="utf-8")
        self.assertIn(
            REAL_PATH_TOKEN,
            text,
            "reply-contract must reference the real skills/show-me/SKILL.md path",
        )
        self.assertNotIn(
            FICTIONAL_PAIRING_LINE,
            text,
            "old fictional pairing line (no real path) must be gone",
        )

    def test_reply_contract_loads_show_me_rather_than_reimplementing_it(self) -> None:
        text = REPLY_CONTRACT_SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("Load `skills/show-me/SKILL.md`", text)

    def test_photon_show_me_reference_points_at_the_real_skill_path(self) -> None:
        text = PHOTON_SHOW_ME_MD.read_text(encoding="utf-8")
        self.assertIn(REAL_PATH_TOKEN, text)

    def test_show_me_is_exported_to_the_grok_dual_tree(self) -> None:
        self.assertTrue(
            GROK_SHOW_ME_SKILL_MD.is_file(),
            f"missing {GROK_SHOW_ME_SKILL_MD} — run "
            "scripts/export_codex_skills.py --output-dir .grok/skills --force",
        )
        grok_text = GROK_SHOW_ME_SKILL_MD.read_text(encoding="utf-8")
        self.assertTrue(grok_text.startswith("---\nname: show-me\n"))

    def test_show_me_owns_the_visual_recipes_not_reply_contract(self) -> None:
        """show-me is a fold of recipes only — it is not a rewrite of reply-contract's
        voice/marks/leftover-vs-bug/spec-gate/clarify/task-name machinery."""
        show_me_text = SHOW_ME_SKILL_MD.read_text(encoding="utf-8")
        reply_contract_text = REPLY_CONTRACT_SKILL_MD.read_text(encoding="utf-8")

        for recipe_marker in ("## Recipe: call tree", "## Recipe: file/screen tree", "## Recipe: stack"):
            self.assertIn(recipe_marker, show_me_text)

        for reply_contract_only_marker in ("## Voice", "## Task name", "### Spec-gate card"):
            self.assertIn(reply_contract_only_marker, reply_contract_text)
            self.assertNotIn(reply_contract_only_marker, show_me_text)


if __name__ == "__main__":
    unittest.main()
