#!/usr/bin/env python3
"""Bind `skills/INDEX.md` listings to the black-box-agent-qa live gate.

`skills/close-out/SKILL.md` Step 9 and `skills/INDEX.md` "Adding a New Skill" both require
a skill to pass `scripts/check_skill_live.py` before it is listed anywhere (INDEX.md,
AGENTS.md, the session-start trigger tables). Until this module existed, nothing enforced
that automatically: `check_skill_live.py` worked correctly when typed by hand, but no test,
CI job, or hook ever ran it against the real listing — a skill could sit in INDEX.md
indefinitely with no run record and nothing would catch it. This is the same failure class
as blocker #4 in the prior revision (a mechanism defined in prose/scripts but never bound to
anything that actually runs). `tests/test_index_live_binding.py` is the binding: it calls
`find_ungated_entries()` against the real `skills/INDEX.md` on every test run.

Usage (module):
    from scripts.index_skills import find_ungated_entries
    failures = find_ungated_entries(index_path, skills_dir)

Usage (CLI), from the repo root, no PYTHONPATH needed:
    python3 scripts/index_skills.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# `python3 scripts/index_skills.py` puts this file's own directory (scripts/) on
# sys.path[0], not the repo root - so `import scripts.check_skill_live` fails with
# ModuleNotFoundError unless the repo root is added first. Guard the insert so importing
# this module normally (e.g. `from scripts.index_skills import ...`, where the repo root
# is already on sys.path) doesn't create a duplicate entry.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_skill_live import check_skill_live  # noqa: E402

INDEX_ENTRY_PATTERN = re.compile(r"^### (.+)$")

# Skills listed in skills/INDEX.md before the black-box-agent-qa live gate existed (added
# 2026-08-26, PR #11 "Bootstrap three locks"). Grandfathered here BY NAME, not silently
# exempted: each one still needs its own run record before it can be dropped from this set,
# and dropping one without capturing a pass first will fail `find_ungated_entries` for it.
#
# Do not add a *new* skill's name here just to dodge a gate failure — that is itself a
# REPEAT of the exact failure class this module exists to close (a listing with no run
# record, nothing catching it). New skills gate at write time per
# `skills/INDEX.md §Adding a New Skill` step 2; they never belong in this allowlist.
GRANDFATHERED_SKILLS: frozenset[str] = frozenset(
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


def list_index_skill_names(index_path: Path) -> list[str]:
    """Return every `### <name>` skill entry in skills/INDEX.md, in file order.

    Deliberately matches only `###` (skill entries) and not `##` (section headers like
    "Adding a New Skill"), so the parse cannot accidentally include non-skill headings.
    """
    names = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        match = INDEX_ENTRY_PATTERN.match(line)
        if match:
            names.append(match.group(1).strip())
    return names


def find_ungated_entries(
    index_path: Path,
    skills_dir: Path,
    allowlist: frozenset[str] = GRANDFATHERED_SKILLS,
) -> list[str]:
    """Return one message per listed skill that is not live-eligible and not grandfathered.

    An empty list means every non-grandfathered entry in `index_path` currently has a
    passing, current black-box-agent-qa run record per `scripts/check_skill_live.py`. A
    non-empty list is exactly the bug this module closes: an INDEX.md listing with no
    current pass that nothing was catching before this function existed.
    """
    failures = []
    for name in list_index_skill_names(index_path):
        if name in allowlist:
            continue
        live, message = check_skill_live(skills_dir / name)
        if not live:
            failures.append(f"{name}: {message}")
    return failures


def main() -> int:
    index_path = REPO_ROOT / "skills" / "INDEX.md"
    skills_dir = REPO_ROOT / "skills"
    failures = find_ungated_entries(index_path, skills_dir)
    if failures:
        print("INDEX.md lists skills with no current black-box-agent-qa pass:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("Every non-grandfathered INDEX.md entry is live-eligible.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
