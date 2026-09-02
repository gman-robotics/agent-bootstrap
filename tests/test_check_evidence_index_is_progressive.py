"""TDD for scripts/check_evidence_index_is_progressive.py — the H-5 progressive-disclosure
check for evidence/INDEX.md.

Checks that an evidence index summarizes each iteration with a pointer to its
`evidence/E_<n>.json` (or `evidence/E_t.json`) file rather than pasting the packet's
own fields (a full dump), modeled on this hub's own skills/INDEX.md convention.

Written before scripts/check_evidence_index_is_progressive.py existed — first run is
ModuleNotFoundError (red).
"""
import unittest
from pathlib import Path

from scripts.check_evidence_index_is_progressive import check_progressive

REPO_ROOT = Path(__file__).parent.parent
FIXTURE_PATH = (
    REPO_ROOT
    / "skills"
    / "evidence-packet-protocol"
    / "fixtures"
    / "evidence-index-not-full-dump"
    / "INDEX.sample.md"
)


class CheckEvidenceIndexIsProgressiveTests(unittest.TestCase):
    def test_full_dump_of_execution_records_is_flagged(self):
        text = (
            "# Evidence Index\n\n"
            "## Iteration 2\n"
            "```json\n"
            '{"execution_records": [{"type": "screenshot", "path": "x.png"}]}\n'
            "```\n"
        )
        violations = check_progressive(text)
        self.assertTrue(violations)
        self.assertTrue(any("progressive" in v for v in violations))

    def test_no_pointer_at_all_is_flagged(self):
        text = "# Evidence Index\n\nIteration 2: things are gap.\n"
        violations = check_progressive(text)
        self.assertTrue(violations)

    def test_short_summary_with_pointer_is_valid(self):
        text = (
            "# Evidence Index\n\n"
            "| Iteration | qa_status | Summary | File |\n"
            "|---|---|---|---|\n"
            "| 2 | gap | Completion screen still missing | `evidence/E_t.json` |\n"
            "| 1 | gap | Initial movement implemented | `evidence/E_1.json` |\n"
        )
        self.assertEqual(check_progressive(text), [])

    def test_real_fixture_sample_is_valid_green(self):
        self.assertTrue(FIXTURE_PATH.exists(), "fixture sample must exist")
        text = FIXTURE_PATH.read_text(encoding="utf-8")
        self.assertEqual(check_progressive(text), [])


if __name__ == "__main__":
    unittest.main()
