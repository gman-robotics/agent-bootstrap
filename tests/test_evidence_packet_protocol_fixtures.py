"""Attack-12 mechanical fixture-IO check: `attack-12-fixture-io`.

Named per the task instructions: every one of the nine evidence-packet-protocol /
preservation-gate black-box fixtures must actually run its literal `input.command`
argv and produce its literal `expected.exit_code` + `expected.stdout_contains` — not
just describe them in a case.json someone reads. This test module IS the mechanical
check: a future REPEAT on any of these fixtures (the validator silently regressing,
someone editing a case.json's expectations to paper over a real failure, etc.) closes
only when this test (or an extension of it) goes red-then-green against the real
argv/exit/stdout, per skills/evidence-packet-protocol/SKILL.md and
skills/preservation-gate/SKILL.md Common Mistakes — never with a comment alone.

Reuses scripts/run_black_box_fixture.py's own `load_case`/`run_case` (the same code
scripts/run_black_box_fixture.py uses to capture skills/<name>/black-box-run.json), so
this is the real system under test, not a reimplementation of it.
"""
import unittest
from pathlib import Path

from scripts.run_black_box_fixture import load_case, run_case

REPO_ROOT = Path(__file__).parent.parent

EVIDENCE_PACKET_FIXTURES_DIR = REPO_ROOT / "skills" / "evidence-packet-protocol" / "fixtures"
PRESERVATION_GATE_FIXTURES_DIR = REPO_ROOT / "skills" / "preservation-gate" / "fixtures"

REQUIRED_FIXTURE_NAMES = frozenset(
    {
        "et-schema-valid",
        "et-status-not-verified-or-gap",
        "et-missing-execution-record",
        "et-living-pii",
        "freeze-sha-mismatch",
        "schema-retry-then-escalate",
        "next-planner-reads-et",
        "evidence-index-not-full-dump",
        "dt-missing-preservation-gate",
    }
)


def _fixture_dirs():
    dirs = []
    if EVIDENCE_PACKET_FIXTURES_DIR.is_dir():
        dirs.extend(sorted(p for p in EVIDENCE_PACKET_FIXTURES_DIR.iterdir() if p.is_dir()))
    if PRESERVATION_GATE_FIXTURES_DIR.is_dir():
        dirs.extend(sorted(p for p in PRESERVATION_GATE_FIXTURES_DIR.iterdir() if p.is_dir()))
    return dirs


class AttackTwelveFixtureIoTests(unittest.TestCase):
    def test_all_nine_named_fixtures_exist_on_disk(self):
        found_names = {fixture_dir.name for fixture_dir in _fixture_dirs()}
        missing = REQUIRED_FIXTURE_NAMES - found_names
        self.assertFalse(missing, f"missing named fixtures: {sorted(missing)}")

    def test_every_fixture_case_json_actually_runs_and_matches_its_literal_expectation(self):
        fixture_dirs = _fixture_dirs()
        self.assertTrue(fixture_dirs, "expected at least one fixture directory")
        for fixture_dir in fixture_dirs:
            if fixture_dir.name not in REQUIRED_FIXTURE_NAMES:
                continue
            with self.subTest(fixture=fixture_dir.name):
                case = load_case(fixture_dir)
                outcome = run_case(case, repo_root=REPO_ROOT)
                self.assertEqual(
                    outcome.get("verdict"),
                    "pass",
                    f"{fixture_dir.name}: expected verdict 'pass', got {outcome}",
                )

    def test_fixture_argv_contains_no_angle_bracket_placeholders(self):
        """Blair pass 2 should-fix: freeze-sha-mismatch (and every other fixture) must
        ship a copy-paste-literal argv, never a <placeholder> someone has to fill in."""
        for fixture_dir in _fixture_dirs():
            if fixture_dir.name not in REQUIRED_FIXTURE_NAMES:
                continue
            with self.subTest(fixture=fixture_dir.name):
                case = load_case(fixture_dir)
                command = case["input"]["command"]
                for arg in command:
                    self.assertNotIn("<", arg, f"{fixture_dir.name}: argv has a placeholder: {arg!r}")
                    self.assertNotIn(">", arg, f"{fixture_dir.name}: argv has a placeholder: {arg!r}")

    def test_every_fixture_readme_names_the_attack_12_repeat_closure_class(self):
        """Task instruction: put the class name in each fixture README."""
        for fixture_dir in _fixture_dirs():
            if fixture_dir.name not in REQUIRED_FIXTURE_NAMES:
                continue
            readme_path = fixture_dir / "README.md"
            with self.subTest(fixture=fixture_dir.name):
                self.assertTrue(readme_path.is_file(), f"{fixture_dir.name} has no README.md")
                text = readme_path.read_text(encoding="utf-8")
                self.assertIn("attack-12-fixture-io", text)


if __name__ == "__main__":
    unittest.main()
