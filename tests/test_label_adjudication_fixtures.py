"""Mechanical black-box fixture I/O for skills/label-adjudication.

Every fixture under skills/label-adjudication/fixtures/ must run its literal
`input.command` and match `expected` via scripts/run_black_box_fixture.run_case.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from scripts.run_black_box_fixture import load_case, run_case

REPO_ROOT = Path(__file__).parent.parent
FIXTURES_DIR = REPO_ROOT / "skills" / "label-adjudication" / "fixtures"

REQUIRED_FIXTURE_NAMES = frozenset(
    {
        "merge-agree-and-adjudicated",
        "merge-unresolved-disagreement",
    }
)


class LabelAdjudicationFixtureIoTests(unittest.TestCase):
    def test_all_named_fixtures_exist_on_disk(self):
        found = {p.name for p in FIXTURES_DIR.iterdir() if p.is_dir()}
        missing = REQUIRED_FIXTURE_NAMES - found
        self.assertFalse(missing, f"missing named fixtures: {sorted(missing)}")

    def test_every_fixture_case_json_runs_and_matches_expectation(self):
        for name in sorted(REQUIRED_FIXTURE_NAMES):
            fixture_dir = FIXTURES_DIR / name
            with self.subTest(fixture=name):
                case = load_case(fixture_dir)
                outcome = run_case(case, repo_root=REPO_ROOT)
                self.assertEqual(
                    outcome.get("verdict"),
                    "pass",
                    f"{name}: expected verdict 'pass', got {outcome}",
                )

    def test_grok_packaged_skill_has_prompt_reference_files(self):
        grok_refs = REPO_ROOT / ".grok" / "skills" / "label-adjudication" / "references"
        for filename in ("labeler-prompt.md", "adjudicator-prompt.md", "source.md"):
            self.assertTrue(
                (grok_refs / filename).is_file(),
                f"missing .grok packaged reference {filename}",
            )


if __name__ == "__main__":
    unittest.main()
