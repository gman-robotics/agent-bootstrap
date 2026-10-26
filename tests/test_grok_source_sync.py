"""Committed .grok/skills/*/references/source.md must match canonical skills/*/SKILL.md."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts.export_codex_skills import SKILL_CONFIGS, strip_trailing_footer

REPO_ROOT = Path(__file__).resolve().parent.parent
GROK_SKILLS = REPO_ROOT / ".grok" / "skills"
CANONICAL_SKILLS = REPO_ROOT / "skills"

WHOLE_FILE_CP_FORBIDDEN = re.compile(
    r"cp\s+[^\n]*hub-pull-request-template\.md",
    re.I,
)


class GrokSourceSyncTests(unittest.TestCase):
    def test_every_exported_skill_has_grok_source_md(self) -> None:
        missing: list[str] = []
        for skill_name in sorted(SKILL_CONFIGS):
            grok_source = GROK_SKILLS / skill_name / "references" / "source.md"
            if not grok_source.is_file():
                missing.append(skill_name)
        self.assertEqual(
            missing,
            [],
            "missing .grok/skills/*/references/source.md for exported skills — re-run "
            "`python3 scripts/export_codex_skills.py --output-dir .grok/skills --force`: "
            + ", ".join(missing),
        )

    def test_every_grok_source_md_matches_canonical_skill_md(self) -> None:
        mismatches: list[str] = []
        for source_md in sorted(GROK_SKILLS.glob("*/references/source.md")):
            skill_name = source_md.parent.parent.name
            canonical = CANONICAL_SKILLS / skill_name / "SKILL.md"
            self.assertTrue(canonical.is_file(), f"missing canonical {canonical}")
            expected = strip_trailing_footer(canonical.read_text(encoding="utf-8"))
            actual = source_md.read_text(encoding="utf-8")
            if actual != expected:
                mismatches.append(skill_name)
        self.assertEqual(
            mismatches,
            [],
            "stale .grok references/source.md (re-run "
            "`python3 scripts/export_codex_skills.py --output-dir .grok/skills --force`): "
            + ", ".join(mismatches),
        )

    def test_skill_tree_reference_source_md_mirrors_skill_md_when_present(self) -> None:
        """skills/<name>/references/source.md is a mirror of SKILL.md (maintain-repo-standards today)."""
        mismatches: list[str] = []
        for source_md in sorted(CANONICAL_SKILLS.glob("*/references/source.md")):
            skill_name = source_md.parent.parent.name
            canonical = CANONICAL_SKILLS / skill_name / "SKILL.md"
            expected = strip_trailing_footer(canonical.read_text(encoding="utf-8"))
            actual = source_md.read_text(encoding="utf-8")
            if actual != expected:
                mismatches.append(str(source_md.relative_to(REPO_ROOT)))
        self.assertEqual(mismatches, [], "stale skills/*/references/source.md: " + ", ".join(mismatches))


class HubPrTemplateCommandDocsTests(unittest.TestCase):
    COPY_MARKER = "hub_pull_request_template.py copy --out .github/PULL_REQUEST_TEMPLATE.md"
    CHECK_MARKER = "hub_pull_request_template.py check --file .github/PULL_REQUEST_TEMPLATE.md"

    PATHS = (
        REPO_ROOT / "skills/create-verification-skill/SKILL.md",
        REPO_ROOT / "skills/maintain-verification-skill/SKILL.md",
        REPO_ROOT / "skills/create-repo-standards/SKILL.md",
        REPO_ROOT / "skills/maintain-repo-standards/SKILL.md",
        REPO_ROOT / "docs/shared/hub-pull-request-template.md",
        REPO_ROOT / "docs/shared/repo-standards-practice.md",
    )

    def test_four_skills_and_two_docs_use_hub_pull_request_template_cli(self) -> None:
        for path in self.PATHS:
            text = path.read_text(encoding="utf-8")
            self.assertIn(
                self.COPY_MARKER,
                text,
                f"{path.relative_to(REPO_ROOT)} must document hub_pull_request_template.py copy",
            )
            self.assertIn(
                self.CHECK_MARKER,
                text,
                f"{path.relative_to(REPO_ROOT)} must document hub_pull_request_template.py check",
            )
            self.assertIsNone(
                WHOLE_FILE_CP_FORBIDDEN.search(text),
                f"{path.relative_to(REPO_ROOT)} must not recommend whole-file cp of hub-pull-request-template.md",
            )


if __name__ == "__main__":
    unittest.main()
