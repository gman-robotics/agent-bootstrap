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

# Independent pin of the exact 20 names grandfathered when the black-box-agent-qa gate
# was added (2026-08-26, PR #11). Deliberately a second, hand-maintained copy - not derived
# from scripts.index_skills.GRANDFATHERED_SKILLS - so this test can detect *any* drift in
# the production set, including a same-length swap (one name removed, a different one
# added) that a bare `isinstance(frozenset)` + `len() == 20` check cannot distinguish from
# the untouched original. Adding a skill to the real allowlist later requires updating this
# copy in the same diff - that edit is the visible review point.
ORIGINAL_GRANDFATHERED_SKILLS = frozenset(
    {
        "agent-orchestration-roles",
        "adversarial-coordination-workflow",
        "plan-code-review-workflow",
        "expert-pr-review",
        "pr-shepherd",
        "reply-contract",
        "codebase-simplification-audit",
        "grill-with-docs",
        "end-of-day-review",
        "multi-harness-coordination",
        "task-loop-7-phase",
        "write-tests",
        "debug-investigation",
        "performance-profiling",
        "feature-flag-lifecycle",
        "cherry-pick-to-release-branch",
        "memory-bank-protocol",
        "docs-protocol",
        "subagent-routing",
        "delegation-patterns",
    }
)


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
            "it. GRANDFATHERED_SKILLS in scripts/index_skills.py is closed — it is pinned "
            "by exact equality (test_grandfathered_skills_is_frozen_at_the_original_twenty) "
            "to the 20 names that predated the gate, and is not a route around a failing "
            "new skill:\n" + "\n".join(failures),
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
        """Pass-3 revision (must-fix): GRANDFATHERED_SKILLS must be a frozenset, not a
        plain mutable set, so it cannot grow silently - a `.add()` call is a hard
        AttributeError, not a quiet allowlist expansion. It must also equal the exact 20
        names grandfathered when the gate was added (2026-08-26, PR #11) - `frozenset` +
        `len() == 20` alone is not enough: swapping one grandfathered name for a
        brand-new one keeps both of those checks green (see
        `test_swapping_one_grandfathered_name_for_a_new_one_is_caught` below for the
        fixture proving that gap and this fix closing it). Any deliberate addition,
        removal, or rename requires updating `ORIGINAL_GRANDFATHERED_SKILLS` above in the
        same diff - that edit is the visible review point.
        """
        self.assertIsInstance(
            GRANDFATHERED_SKILLS,
            frozenset,
            "GRANDFATHERED_SKILLS must be an immutable frozenset so the grandfather "
            "list cannot grow silently",
        )
        self.assertEqual(
            GRANDFATHERED_SKILLS,
            ORIGINAL_GRANDFATHERED_SKILLS,
            "GRANDFATHERED_SKILLS no longer equals the exact 20 names grandfathered in "
            "PR #11 - if this is a deliberate, reviewed change, update "
            "ORIGINAL_GRANDFATHERED_SKILLS in this test file in the same diff; "
            "GRANDFATHERED_SKILLS is otherwise closed to edits, not a route around a "
            "failing new skill. Symmetric difference: "
            f"{GRANDFATHERED_SKILLS ^ ORIGINAL_GRANDFATHERED_SKILLS}",
        )

    def test_swapping_one_grandfathered_name_for_a_new_one_is_caught(self) -> None:
        """Pass-3 revision (must-fix) fixture: adversary review found that swapping one
        grandfathered name for a brand-new one - while keeping the set a frozenset of
        length 20 - passed both the type check and the count check the prior revision
        relied on, and (when the swap is mirrored in `skills/INDEX.md`: the old entry's
        `### <name>` heading removed, a new one added in its place) also made
        `find_ungated_entries` return `[]` for the swapped-in name, since an allowlisted
        entry is skipped before `check_skill_live` ever runs on it - exactly the
        no-run-record-and-nothing-catches-it failure class this whole module exists to
        close, hidden behind the allowlist mechanism itself. Reproduced live against the
        real production set and the real `skills/INDEX.md` before writing this fix:
        swapping `delegation-patterns` for a fake `a-totally-new-example-skill` name in
        both places left all 26 prior-revision tests green. This fixture proves the same
        swap on a copy of the real set: (a) still satisfies the weaker frozenset+len==20
        invariant - confirming that check alone was insufficient - and (b) fails the
        exact-equality pin this revision adds.
        """
        swapped = (GRANDFATHERED_SKILLS - {"delegation-patterns"}) | {
            "a-totally-new-example-skill"
        }

        self.assertIsInstance(swapped, frozenset)
        self.assertEqual(
            len(swapped),
            20,
            "fixture setup error: the swap must preserve length 20 to reproduce the "
            "reported gap",
        )

        self.assertNotEqual(
            swapped,
            ORIGINAL_GRANDFATHERED_SKILLS,
            "swap-one-name fixture regression: a same-length swap must be distinguishable "
            "from the exact original 20 names, or the equality pin above provides no more "
            "protection than the frozenset+len==20 check it replaces",
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
