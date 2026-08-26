import os
import subprocess
import sys
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

    def test_grandfathered_skills_is_frozen_at_the_original_twenty(self) -> None:
        """Pass-3 should-fix: GRANDFATHERED_SKILLS must be a frozenset, not a plain
        mutable set, so it cannot grow silently - a `.add()` call is a hard AttributeError,
        not a quiet allowlist expansion. This test also pins the count to exactly the 20
        names grandfathered when the gate was added (2026-08-26, PR #11): adding an
        entry requires touching this test in the same diff, which makes the change a
        visible, deliberate review point instead of a one-line addition nobody notices.
        """
        self.assertIsInstance(
            GRANDFATHERED_SKILLS,
            frozenset,
            "GRANDFATHERED_SKILLS must be an immutable frozenset so the grandfather "
            "list cannot grow silently",
        )
        self.assertEqual(
            len(GRANDFATHERED_SKILLS),
            20,
            "GRANDFATHERED_SKILLS count drifted from the original 20 names grandfathered "
            "in PR #11 - if this is a deliberate addition, update this test's expected "
            "count in the same diff so the change is a visible review point, not silent "
            "growth",
        )

    def test_bare_cli_invocation_works_from_repo_root_with_no_pythonpath(self) -> None:
        """Pass-3 should-fix: `skills/INDEX.md` step 3 and the module's own docstring both
        document `python3 scripts/index_skills.py` as the CLI usage, but the module used
        to hard-fail with ModuleNotFoundError unless PYTHONPATH included the repo root
        (the script's own directory, not the repo root, lands on sys.path[0]). Runs the
        literal documented command as a real subprocess, with PYTHONPATH deliberately
        unset, so a regression here is caught the same way a user would hit it.
        """
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        result = subprocess.run(
            [sys.executable, "scripts/index_skills.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            env=env,
        )

        self.assertEqual(
            result.returncode,
            0,
            f"bare `python3 scripts/index_skills.py` failed with no PYTHONPATH:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}",
        )
        self.assertNotIn("ModuleNotFoundError", result.stderr)


if __name__ == "__main__":
    unittest.main()
