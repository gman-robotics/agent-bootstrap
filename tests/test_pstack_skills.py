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

    def test_figure_it_out_never_block_carve_out_cites_article_1(self) -> None:
        text = (REPO_ROOT / "skills" / "figure-it-out" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("never-block-on-the-human", text)
        self.assertIn("Article 1", text)
        self.assertIn("literal **Approve**", text)
        self.assertIn("does not operationalize past a gate", text)

    def test_architect_phase_c_defaults_to_spec_gate(self) -> None:
        text = (REPO_ROOT / "skills" / "architect" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("spec-gate card", text)
        self.assertNotIn("No human checkpoint", text)
        self.assertNotIn("Default: proceed directly to implementation", text)

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

    def test_validator_rejects_run_in_background_leftover(self) -> None:
        skill_md = REPO_ROOT / "skills" / "arena" / "SKILL.md"
        original = skill_md.read_text(encoding="utf-8")
        poisoned = original + "\nrun_in_background: true\n"
        skill_md.write_text(poisoned, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "arena"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("run_in_background", result.stderr)
        finally:
            skill_md.write_text(original, encoding="utf-8")

    def test_validator_rejects_cloud_base_branch_override_leftover(self) -> None:
        skill_md = REPO_ROOT / "skills" / "swarm" / "SKILL.md"
        original = skill_md.read_text(encoding="utf-8")
        poisoned = original + "\nbase branch override for cloud subagents\n"
        skill_md.write_text(poisoned, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "swarm"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("cloud subagent base-branch override", result.stderr)
        finally:
            skill_md.write_text(original, encoding="utf-8")

    def test_show_me_companion_points_at_show_me_your_work(self) -> None:
        text = (REPO_ROOT / "skills" / "show-me" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("**Do not use for**", text)
        self.assertIn("show-me-your-work", text)
        self.assertIn("## Companions", text)
        companions_section = text.split("## Companions", 1)[1].split("##", 1)[0]
        self.assertIn("show-me-your-work", companions_section)

    def test_expert_pr_review_companion_points_at_interrogate(self) -> None:
        text = (REPO_ROOT / "skills" / "expert-pr-review" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("**Do not use for**", text)
        self.assertIn("interrogate", text)
        self.assertIn("## Companions", text)
        companions_section = text.split("## Companions", 1)[1].split("##", 1)[0]
        self.assertIn("interrogate", companions_section)

    def test_companion_reverse_pointers_via_validator(self) -> None:
        from scripts.validate_pstack_skill import validate_companion_reverse_pointers

        errors = validate_companion_reverse_pointers()
        self.assertEqual(errors, [])

    def test_companion_validator_cli_runs_for_show_me(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "show-me"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_companion_validator_cli_runs_for_expert_pr_review(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "expert-pr-review"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_security_audit_companion_points_at_expert_pr_review(self) -> None:
        """GMA-56: security-audit <-> expert-pr-review reverse companion pointer."""
        text = (REPO_ROOT / "skills" / "security-audit" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("**Do not use for**", text)
        self.assertIn("expert-pr-review", text)
        self.assertIn("## Companions", text)
        companions_section = text.split("## Companions", 1)[1].split("##", 1)[0]
        self.assertIn("expert-pr-review", companions_section)

    def test_security_audit_companion_points_at_blast_radius(self) -> None:
        """GMA-56: security-audit <-> blast-radius reverse companion pointer."""
        text = (REPO_ROOT / "skills" / "security-audit" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("**Do not use for**", text)
        self.assertIn("blast-radius", text)
        self.assertIn("## Companions", text)
        companions_section = text.split("## Companions", 1)[1].split("##", 1)[0]
        self.assertIn("blast-radius", companions_section)

    def test_companion_validator_cli_runs_for_security_audit(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "security-audit"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_security_audit_vendor_structure_validator_cli_runs(self) -> None:
        """GMA-56: the standalone security-audit vendor validator (not a pstack port)."""
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "validate_security_audit_vendor.py"), "security-audit"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_companion_validator_rejects_stripped_show_me_companion_row(self) -> None:
        skill_md = REPO_ROOT / "skills" / "show-me" / "SKILL.md"
        original = skill_md.read_text(encoding="utf-8")
        poisoned = original.replace(
            "| `show-me-your-work` | Decision log for long-running work; this skill owns per-reply shape visuals only |\n",
            "",
        )
        skill_md.write_text(poisoned, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "show-me"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Companions must point at show-me-your-work", result.stderr)
        finally:
            skill_md.write_text(original, encoding="utf-8")

    def test_companion_validator_rejects_stripped_show_me_your_work_companion_row(self) -> None:
        skill_md = REPO_ROOT / "skills" / "show-me-your-work" / "SKILL.md"
        original = skill_md.read_text(encoding="utf-8")
        poisoned = original.replace(
            "| `show-me` | Shape visuals in status replies; this skill owns the decision log format |\n",
            "",
        )
        skill_md.write_text(poisoned, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "show-me-your-work"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Companions must point at show-me", result.stderr)
        finally:
            skill_md.write_text(original, encoding="utf-8")

    def test_companion_validator_rejects_stripped_expert_pr_review_companion_row(self) -> None:
        skill_md = REPO_ROOT / "skills" / "expert-pr-review" / "SKILL.md"
        original = skill_md.read_text(encoding="utf-8")
        poisoned = original.replace(
            "| `interrogate` | Multi-model stress-test on a diff or branch when there is no open PR workflow |\n",
            "",
        )
        skill_md.write_text(poisoned, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "expert-pr-review"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Companions must point at interrogate", result.stderr)
        finally:
            skill_md.write_text(original, encoding="utf-8")

    def test_companion_validator_rejects_stripped_interrogate_companion_row(self) -> None:
        skill_md = REPO_ROOT / "skills" / "interrogate" / "SKILL.md"
        original = skill_md.read_text(encoding="utf-8")
        poisoned = original.replace(
            "| `expert-pr-review` | When the target is a GitHub PR with threads, build/test, and posting gates |\n",
            "",
        )
        skill_md.write_text(poisoned, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "interrogate"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Companions must point at expert-pr-review", result.stderr)
        finally:
            skill_md.write_text(original, encoding="utf-8")

    def test_companion_validator_rejects_stripped_do_not_use_citation(self) -> None:
        skill_md = REPO_ROOT / "skills" / "show-me" / "SKILL.md"
        original = skill_md.read_text(encoding="utf-8")
        poisoned = original.replace(
            "- A reviewable TSV decision trail for long-running or unattended work — that is `show-me-your-work`.\n",
            "",
        )
        skill_md.write_text(poisoned, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "show-me"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Do not use for must cite companion show-me-your-work", result.stderr)
        finally:
            skill_md.write_text(original, encoding="utf-8")

    def test_grok_architect_reference_files_dual_homed(self) -> None:
        for name in ("runner-prompt.md", "design-red-flags.md", "rationale-template.md"):
            grok_ref = (
                REPO_ROOT / ".grok" / "skills" / "architect" / "references" / name
            )
            canonical = REPO_ROOT / "skills" / "architect" / "references" / name
            self.assertTrue(grok_ref.is_file(), f"missing dual-homed {grok_ref}")
            self.assertTrue(canonical.is_file())
            self.assertEqual(
                grok_ref.read_text(encoding="utf-8"),
                canonical.read_text(encoding="utf-8"),
            )

    def test_grok_why_epistemics_dual_homed(self) -> None:
        grok_ref = REPO_ROOT / ".grok" / "skills" / "why" / "references" / "epistemics.md"
        canonical = REPO_ROOT / "skills" / "why" / "references" / "epistemics.md"
        self.assertTrue(grok_ref.is_file())
        self.assertTrue(canonical.is_file())
        self.assertEqual(
            grok_ref.read_text(encoding="utf-8"),
            canonical.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
