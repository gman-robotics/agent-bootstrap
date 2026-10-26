"""Committed .grok/skills/*/references/source.md must match canonical skills/*/SKILL.md."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.export_codex_skills import strip_trailing_footer

REPO_ROOT = Path(__file__).resolve().parent.parent
GROK_SKILLS = REPO_ROOT / ".grok" / "skills"
CANONICAL_SKILLS = REPO_ROOT / "skills"


class GrokSourceSyncTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
