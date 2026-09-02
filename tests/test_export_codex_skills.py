import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.export_codex_skills import SKILL_CONFIGS, export_skills


REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "skills"

# REPEAT fixture (see skills/triage-review-feedback/fixtures/repeat-exporter-dropped-references/
# README.md): same failure class was called NEW then REPEATed twice in memory-bank/progress.md
# (2026-08-22 swarm-forge session, PR #9 revision pass 1, PR #9 revision pass 2) with no
# mechanical check until this test.
REPEAT_FIXTURE = (
    SOURCE_DIR
    / "triage-review-feedback"
    / "fixtures"
    / "repeat-exporter-dropped-references"
    / "hand-added-reference.md"
)


class ExportCodexSkillsTests(unittest.TestCase):
    def test_export_creates_expected_skill_folders(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            exported = export_skills(SOURCE_DIR, output_dir)

            self.assertEqual(len(exported), len(SKILL_CONFIGS))
            self.assertIn("task-loop-7-phase", SKILL_CONFIGS)
            self.assertIn("reply-contract", SKILL_CONFIGS)
            self.assertIn("codebase-simplification-audit", SKILL_CONFIGS)
            self.assertIn("grill-with-docs", SKILL_CONFIGS)
            self.assertIn("black-box-agent-qa", SKILL_CONFIGS)
            self.assertIn("show-me", SKILL_CONFIGS)
            self.assertIn("evidence-packet-protocol", SKILL_CONFIGS)
            self.assertIn("preservation-gate", SKILL_CONFIGS)
            for skill_name in SKILL_CONFIGS:
                skill_dir = output_dir / skill_name
                self.assertTrue(skill_dir.is_dir(), skill_name)
                self.assertTrue((skill_dir / "SKILL.md").is_file(), skill_name)
                self.assertTrue((skill_dir / "references" / "source.md").is_file(), skill_name)

    def test_reply_contract_quick_start_points_at_the_real_show_me_path(self) -> None:
        """NEW blocker from adversarial review of PR #13: the exporter's own
        reply-contract SkillConfig.quick_start still said pathless 'Pair with show-me' after the
        canonical skills/reply-contract/SKILL.md was fixed to load the real
        skills/show-me/SKILL.md path -- so every Grok/Codex user loading
        .grok/skills/reply-contract/SKILL.md (generated straight from this quick_start,
        not from the canonical source) still saw the old fiction. Pin the fix at the
        source of truth so a future edit can't silently reintroduce it without also
        breaking this test.
        """
        quick_start_text = " ".join(SKILL_CONFIGS["reply-contract"].quick_start)
        self.assertIn(
            "skills/show-me/SKILL.md",
            quick_start_text,
            "reply-contract's exporter quick_start must name the real show-me path",
        )
        self.assertNotIn(
            "Pair with show-me",
            quick_start_text,
            "old pathless 'Pair with show-me' phrasing must be gone from the exporter config",
        )

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

    def test_force_reexport_preserves_hand_added_reference_files(self) -> None:
        """REPEAT-lock mechanical check.

        Fixture: skills/triage-review-feedback/fixtures/repeat-exporter-dropped-references/
        hand-added-reference.md. This reproduces the exact failure class called NEW then
        REPEATed twice (memory-bank/progress.md, 2026-08-22) before any mechanical check
        existed: `export_skills(..., force=True)` used to `shutil.rmtree` the whole skill
        directory and drop any hand-added `references/` file that was not the generated
        `source.md` (e.g. `grill-with-docs/references/adr-format.md`), never regenerating it.

        Before the preserve-extra-files fix in `scripts/export_codex_skills.py`, this test
        fails red because the fixture file below does not survive the second export.
        """
        self.assertTrue(REPEAT_FIXTURE.is_file(), "REPEAT fixture file must exist in-tree")
        fixture_content = REPEAT_FIXTURE.read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            export_skills(SOURCE_DIR, output_dir)

            extra_file = output_dir / "grill-with-docs" / "references" / "hand-added-reference.md"
            extra_file.write_text(fixture_content, encoding="utf-8")

            export_skills(SOURCE_DIR, output_dir, force=True)

            self.assertTrue(
                extra_file.is_file(),
                "force re-export dropped a hand-added references/ file (REPEAT regression: "
                "same failure class called NEW then REPEATed twice with no mechanical check "
                "in memory-bank/progress.md 2026-08-22)",
            )
            self.assertEqual(extra_file.read_text(encoding="utf-8"), fixture_content)


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
            local_skills = Path(tmp) / ".grok" / "skills"
            self.assertTrue(
                local_skills.is_dir(),
                "--local refreshes project .grok/skills, not plugin-root skills/",
            )
            self.assertGreaterEqual(len(list(local_skills.glob("*/SKILL.md"))), 10)

    def test_install_grok_user_mode_creates_expected_structure(self) -> None:
        """User/plugin install should create plugin-root skills + Grok-frontmatter agents.

        Grok plugin discovery scans <plugin>/skills/ and <plugin>/agents/, not
        a nested .grok/ tree. See ~/.grok/docs/user-guide/09-plugins.md.
        """
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

            skills_dir = target / "skills"
            self.assertTrue(skills_dir.is_dir(), "plugin skills live at <plugin>/skills/")
            self.assertFalse(
                (target / ".grok" / "skills").is_dir(),
                "plugin mode must not nest skills under .grok/",
            )
            skill_files = list(skills_dir.glob("*/SKILL.md"))
            self.assertGreaterEqual(len(skill_files), 10, "Should have most or all skills exported")
            self.assertTrue(
                (skills_dir / "grill-with-docs" / "references" / "adr-format.md").is_file(),
                "exporter --force deletes extra skill references; installer must restore them",
            )

            agents_dir = target / "agents"
            self.assertTrue(agents_dir.is_dir(), "plugin agents live at <plugin>/agents/")
            architect = agents_dir / "software-architect.md"
            self.assertTrue(architect.is_file())
            content = architect.read_text(encoding="utf-8")
            self.assertIn("model: sonnet", content)
            self.assertIn("tools:", content)
            self.assertIn("software-architect", content.lower())

            manifest = target / ".grok-plugin" / "plugin.json"
            self.assertTrue(manifest.is_file(), "Grok plugin manifest")
            text = manifest.read_text(encoding="utf-8")
            self.assertIn('"name": "agent-bootstrap"', text)

    def test_install_grok_equivalent_repo_paths_do_not_select_plugin_layout(self) -> None:
        """TARGET that *is* the hub must not use plugin layout.

        A raw string compare misses trailing slashes, `.`, and symlink spellings.
        Plugin layout would export into committed skills/ (FileExistsError without
        --force; rmtree of source with --force). Discriminator: exporter path
        `<repo>/skills/` vs `<repo>/.grok/skills/`.
        """
        script = REPO_ROOT / "scripts" / "install-grok.sh"
        index_before = (REPO_ROOT / "skills" / "INDEX.md").read_bytes()
        plugin_skills_prefix = str(REPO_ROOT / "skills") + os.sep
        cases = [
            str(REPO_ROOT) + "/",
            ".",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "hub-link"
            link.symlink_to(REPO_ROOT)
            cases.append(str(link))
            for target in cases:
                with self.subTest(target=target):
                    result = subprocess.run(
                        ["bash", str(script), "--target", target],
                        cwd=REPO_ROOT,
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                    combined = result.stdout + result.stderr
                    self.assertEqual(
                        (REPO_ROOT / "skills" / "INDEX.md").read_bytes(),
                        index_before,
                        "canonical skills/INDEX.md must not change",
                    )
                    self.assertFalse(
                        (REPO_ROOT / ".claude-plugin").exists(),
                        "plugin-mode side dir must not appear in the hub",
                    )
                    self.assertNotIn(
                        plugin_skills_prefix,
                        combined,
                        f"--target {target!r} selected plugin layout:\n{combined[-800:]}",
                    )


class InstallAgentsScriptTests(unittest.TestCase):
    """TDD for scripts/install-agents.sh — it must symlink every agent, not just the first."""

    def test_install_agents_symlinks_all_agent_files(self) -> None:
        script = REPO_ROOT / "scripts" / "install-agents.sh"
        agent_sources = sorted((REPO_ROOT / "agents").glob("*.md"))
        self.assertGreater(len(agent_sources), 1, "expected multiple agent files to symlink")

        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "HOME": tmp}
            result = subprocess.run(
                ["bash", str(script)],
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
            )
            self.assertEqual(
                result.returncode, 0,
                f"install-agents.sh failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}",
            )

            installed_dir = Path(tmp) / ".claude" / "agents"
            installed = sorted(installed_dir.glob("*.md"))
            self.assertEqual(
                {p.name for p in installed},
                {p.name for p in agent_sources},
                "every agent file must be symlinked",
            )
            for link in installed:
                self.assertTrue(link.is_symlink(), f"{link.name} should be a symlink")


if __name__ == "__main__":
    unittest.main()
