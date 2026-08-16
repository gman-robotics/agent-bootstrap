import subprocess
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
            self.assertIn("task-loop-7-phase", SKILL_CONFIGS)
            self.assertIn("reply-contract", SKILL_CONFIGS)
            self.assertIn("codebase-simplification-audit", SKILL_CONFIGS)
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


class InstallGrokScriptTests(unittest.TestCase):
    """TDD for scripts/install-grok.sh — adapted to the post-PR#1 structure."""

    def test_install_grok_script_exists_and_has_help(self) -> None:
        script = REPO_ROOT / "scripts" / "install-grok.sh"
        self.assertTrue(script.is_file(), "install-grok.sh must exist")
        result = subprocess.run(
            ["bash", str(script), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("install-grok", result.stdout.lower())

    def test_install_grok_local_runs_without_error(self) -> None:
        """--local should succeed on the current repo (even if it is a no-op or refresh)."""
        script = REPO_ROOT / "scripts" / "install-grok.sh"
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["bash", str(script), "--local", "--target", tmp, "--force"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(
                result.returncode, 0,
                f"install-grok.sh --local failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
            )

    def test_install_grok_user_mode_creates_expected_structure(self) -> None:
        """User/plugin install should create skills + Grok-frontmatter agents."""
        script = REPO_ROOT / "scripts" / "install-grok.sh"
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "plugin-install"
            result = subprocess.run(
                ["bash", str(script), "--target", str(target), "--force"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            # Skills
            skills_dir = target / ".grok" / "skills"
            self.assertTrue(skills_dir.is_dir())
            skill_files = list(skills_dir.glob("*/SKILL.md"))
            self.assertGreaterEqual(len(skill_files), 10, "Should have most or all skills exported")

            # Agents should have Grok-native frontmatter (model: sonnet, tools list)
            agents_dir = target / ".grok" / "agents"
            self.assertTrue(agents_dir.is_dir())
            architect = agents_dir / "software-architect.md"
            self.assertTrue(architect.is_file())
            content = architect.read_text(encoding="utf-8")
            self.assertIn("model: sonnet", content)
            self.assertIn("tools:", content)
            self.assertIn("software-architect", content.lower())


if __name__ == "__main__":
    unittest.main()
