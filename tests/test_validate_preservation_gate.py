"""TDD for scripts/validate_preservation_gate.py — the GB-2 Dt heading check.

Checks that a development-document markdown (`Dt`) contains the exact required
`## Preservation Gate` heading (skills/preservation-gate/SKILL.md), distinct from
REPEAT, with at least one bullet naming a previously verified claim to preserve.

Written before scripts/validate_preservation_gate.py existed — first run is
ModuleNotFoundError (red).
"""
import unittest
from pathlib import Path

from scripts.validate_preservation_gate import check_preservation_gate

REPO_ROOT = Path(__file__).parent.parent
FIXTURE_PATH = (
    REPO_ROOT
    / "skills"
    / "preservation-gate"
    / "fixtures"
    / "dt-missing-preservation-gate"
    / "Dt.sample.md"
)


class PreservationGateCheckTests(unittest.TestCase):
    def test_missing_heading_is_flagged_and_names_the_heading(self):
        text = "# Iteration 2 Plan\n\n## Summary\nNothing preserved here.\n"
        violations = check_preservation_gate(text)
        self.assertTrue(violations)
        self.assertTrue(any("Preservation Gate" in v for v in violations))

    def test_heading_present_with_a_bullet_is_valid(self):
        text = (
            "# Iteration 2 Plan\n\n"
            "## Preservation Gate\n\n"
            "- Player input changes avatar motion (`player_control`, verified iteration 1).\n\n"
            "## Update Targets\n"
        )
        self.assertEqual(check_preservation_gate(text), [])

    def test_heading_present_with_no_bullets_is_flagged(self):
        text = "## Preservation Gate\n\nNothing bulleted yet.\n\n## Update Targets\n"
        violations = check_preservation_gate(text)
        self.assertTrue(violations)
        self.assertTrue(any("Preservation Gate" in v for v in violations))

    def test_similarly_worded_heading_does_not_satisfy_the_exact_heading_requirement(self):
        """Distinct from REPEAT: only the exact heading counts, not a paraphrase."""
        text = "## Preserved Behaviors\n\n- Something works.\n"
        violations = check_preservation_gate(text)
        self.assertTrue(violations)

    def test_real_missing_fixture_is_invalid_red(self):
        self.assertTrue(FIXTURE_PATH.exists(), "fixture sample must exist")
        text = FIXTURE_PATH.read_text(encoding="utf-8")
        violations = check_preservation_gate(text)
        self.assertTrue(any("Preservation Gate" in v for v in violations), violations)


if __name__ == "__main__":
    unittest.main()
