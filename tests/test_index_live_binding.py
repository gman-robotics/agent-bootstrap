import tempfile
import unittest
from pathlib import Path

from scripts.index_skills import GRANDFATHERED_SKILLS, find_ungated_entries, list_index_skill_names

REPO_ROOT = Path(__file__).parent.parent
INDEX_PATH = REPO_ROOT / "skills" / "INDEX.md"
SKILLS_DIR = REPO_ROOT / "skills"


class IndexLiveBindingTests(unittest.TestCase):
    def test_binding_catches_an_index_entry_with_no_run_record(self) -> None:
        """REPEAT-class fixture: an INDEX.md entry for a skill with no run record, not
        grandfathered. Before this module existed, `check_skill_live.py` could report this
        skill "not live" all day and nothing would ever call it - the skill would still be
        listed and would have been treated as available. This test runs the real
        `find_ungated_entries` production function (not a re-implementation) against an
        isolated, synthetic INDEX.md + skill directory so the fixture is fast and does not
        depend on the real repo's INDEX.md staying in any particular state.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            skill_dir = skills_dir / "ungated-example-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: ungated-example-skill\n---\nbody\n", encoding="utf-8"
            )
            # Deliberately no black-box-run.json written here - this is the fixture.

            index_path = skills_dir / "INDEX.md"
            index_path.write_text(
                "# INDEX\n\n## Skill Entries\n\n### ungated-example-skill\n"
                "**File**: `skills/ungated-example-skill/SKILL.md`\n\n"
                "## Adding a New Skill\n",
                encoding="utf-8",
            )

            failures = find_ungated_entries(index_path, skills_dir, allowlist=frozenset())

            self.assertTrue(
                any("ungated-example-skill" in failure for failure in failures),
                "fixture regression: an INDEX entry with no run record, and not "
                "grandfathered, must be caught - not silently treated as live",
            )

    def test_binding_ignores_a_grandfathered_entry_with_no_run_record(self) -> None:
        """The allowlist is how a pre-existing skill is grandfathered without pretending
        it has a run record it does not have."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            skill_dir = skills_dir / "legacy-example-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: legacy-example-skill\n---\nbody\n", encoding="utf-8"
            )
            index_path = skills_dir / "INDEX.md"
            index_path.write_text(
                "## Skill Entries\n\n### legacy-example-skill\n", encoding="utf-8"
            )

            failures = find_ungated_entries(
                index_path, skills_dir, allowlist=frozenset({"legacy-example-skill"})
            )

            self.assertEqual(failures, [])

    def test_every_non_grandfathered_index_entry_is_live(self) -> None:
        """The actual bind: run scripts/check_skill_live.py's logic against every ###
        entry in the real skills/INDEX.md. A skill not in GRANDFATHERED_SKILLS must have a
        passing, current black-box-agent-qa run record - this is what keeps INDEX.md from
        listing a skill live without a current pass, for real, every time this suite runs.
        """
        failures = find_ungated_entries(INDEX_PATH, SKILLS_DIR)

        self.assertEqual(
            failures,
            [],
            "skills/INDEX.md lists a skill with no current black-box-agent-qa pass; run "
            "scripts/run_black_box_fixture.py + scripts/check_skill_live.py before adding "
            "it, or add it to GRANDFATHERED_SKILLS in scripts/index_skills.py if it "
            "predates the gate:\n" + "\n".join(failures),
        )

    def test_grandfathered_allowlist_only_names_currently_listed_skills(self) -> None:
        """The allowlist must not drift ahead of INDEX.md - every grandfathered name has
        to still be listed, so a rename or removal is caught rather than silently kept."""
        listed = set(list_index_skill_names(INDEX_PATH))
        missing = GRANDFATHERED_SKILLS - listed

        self.assertEqual(
            missing,
            set(),
            f"grandfathered in scripts/index_skills.py but no longer in INDEX.md: {missing}",
        )


if __name__ == "__main__":
    unittest.main()
