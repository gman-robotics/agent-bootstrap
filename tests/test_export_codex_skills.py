import tempfile
import unittest
from pathlib import Path

from scripts.export_codex_skills import SKILL_CONFIGS, export_skills


REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "skills"


class ExportCodexSkillsTests(unittest.TestCase):
    def test_export_creates_expected_skill_folders(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            exported = export_skills(SOURCE_DIR, output_dir)

            self.assertEqual(len(exported), len(SKILL_CONFIGS))
            for skill_name in SKILL_CONFIGS:
                skill_dir = output_dir / skill_name
                self.assertTrue(skill_dir.is_dir(), skill_name)
                self.assertTrue((skill_dir / "SKILL.md").is_file(), skill_name)
                self.assertTrue((skill_dir / "references" / "source.md").is_file(), skill_name)

    def test_exported_skill_contains_frontmatter_and_reference_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            export_skills(SOURCE_DIR, output_dir)

            skill_text = (output_dir / "expert-pr-review" / "SKILL.md").read_text(encoding="utf-8")

            self.assertTrue(skill_text.startswith("---\nname: expert-pr-review\n"))
            self.assertIn("references/source.md", skill_text)
            self.assertIn("review-only constraints", skill_text)

    def test_source_reference_preserves_original_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            export_skills(SOURCE_DIR, output_dir)

            source_text = (output_dir / "write-tests" / "references" / "source.md").read_text(
                encoding="utf-8"
            )

            self.assertIn("# write-tests.md — Test Writing Skill", source_text)
            self.assertIn("## Step 1: Orient", source_text)
            self.assertNotIn("Last updated:", source_text.splitlines()[-1])


if __name__ == "__main__":
    unittest.main()
