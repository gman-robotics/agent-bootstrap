"""TDD for scripts/check_planner_reads_et.py — the H-1 path-convention check.

Checks that a planner/development-document template instructs the reader to read the
prior evidence packet at the exact `evidence/E_t.json` path convention before planning
(H-1: "next planner must read it" — mem0/activeContext.md is not a substitute).

Written before scripts/check_planner_reads_et.py existed — first run is
ModuleNotFoundError (red).
"""
import unittest
from pathlib import Path

from scripts.check_planner_reads_et import check_planner_reads_et

REPO_ROOT = Path(__file__).parent.parent
FIXTURE_PATH = (
    REPO_ROOT
    / "skills"
    / "evidence-packet-protocol"
    / "fixtures"
    / "next-planner-reads-et"
    / "plan-template.sample.md"
)


class CheckPlannerReadsEtTests(unittest.TestCase):
    def test_missing_pointer_is_flagged(self):
        text = "# Plan Template\n\nStart by reviewing the backlog.\n"
        violations = check_planner_reads_et(text)
        self.assertTrue(violations)
        self.assertTrue(any("evidence/E_t.json" in v for v in violations))

    def test_pointer_present_is_valid(self):
        text = (
            "# Plan Template\n\n"
            "Before planning, read the prior evidence packet at `evidence/E_t.json` "
            "and `evidence/INDEX.md`.\n"
        )
        self.assertEqual(check_planner_reads_et(text), [])

    def test_summary_memory_mention_alone_is_not_a_substitute(self):
        """H-1: mem0/activeContext.md is explicitly not a substitute for reading E_t.json."""
        text = "# Plan Template\n\nCheck activeContext.md for prior context.\n"
        violations = check_planner_reads_et(text)
        self.assertTrue(violations)

    def test_real_fixture_sample_is_valid_green(self):
        self.assertTrue(FIXTURE_PATH.exists(), "fixture sample must exist")
        text = FIXTURE_PATH.read_text(encoding="utf-8")
        self.assertEqual(check_planner_reads_et(text), [])


if __name__ == "__main__":
    unittest.main()
