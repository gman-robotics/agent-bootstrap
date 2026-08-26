#!/usr/bin/env python3
"""Gate: may <skill> be listed live (INDEX.md / trigger tables / exporter config)?

A skill is live-eligible only if `<skill_dir>/black-box-run.json` exists with
`"verdict": "pass"` and a `skill_sha256` that matches the *current* content of
`<skill_dir>/SKILL.md`. That hash tie is the silent-refine guard: editing SKILL.md after
capturing a pass — including a well-intentioned "the run showed it works better this way"
trajectory refine — invalidates the record. A fresh `scripts/run_black_box_fixture.py` pass
is required before the edited skill can be treated as live again.

See `skills/close-out/SKILL.md` Step 9 and `skills/INDEX.md` "Adding a New Skill" for where
this gate is required, and `skills/black-box-agent-qa/SKILL.md` for how a run record is
captured in the first place.

Usage:
    python3 scripts/check_skill_live.py <skill-name>
    python3 scripts/check_skill_live.py --skill-dir path/to/skill

Exit code 0 = live-eligible, 1 = not live-eligible (message printed explains why).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_RECORD_FILENAME = "black-box-run.json"


def skill_sha256(skill_dir: Path) -> str | None:
    """sha256 of the skill's current SKILL.md, or None if it does not exist."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return None
    return hashlib.sha256(skill_md.read_bytes()).hexdigest()


def check_skill_live(skill_dir: Path) -> tuple[bool, str]:
    """Return (is_live_eligible, human-readable reason)."""
    run_record_path = skill_dir / RUN_RECORD_FILENAME
    if not run_record_path.is_file():
        return False, f"not live: no run record at {run_record_path}"

    try:
        record = json.loads(run_record_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"not live: {run_record_path} is not valid JSON ({exc})"

    verdict = record.get("verdict")
    if verdict != "pass":
        return False, f"not live: run record verdict is {verdict!r}, not 'pass'"

    current_sha = skill_sha256(skill_dir)
    recorded_sha = record.get("skill_sha256")
    if recorded_sha != current_sha:
        return False, (
            "not live: run record is stale — SKILL.md changed since the black-box-agent-qa "
            "pass was captured (skill_sha256 mismatch). Capture a fresh pass with "
            "scripts/run_black_box_fixture.py before shipping this edit; a silent trajectory "
            "refine does not carry the old pass forward."
        )

    return True, "live-eligible: run record verdict is pass and matches the current SKILL.md"


def resolve_skill_dir(args: argparse.Namespace) -> Path:
    if args.skill_dir:
        return Path(args.skill_dir)
    return REPO_ROOT / "skills" / args.skill_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "skill_name",
        nargs="?",
        help="Skill name under skills/ (ignored if --skill-dir is given).",
    )
    parser.add_argument(
        "--skill-dir",
        help="Explicit path to the skill directory (overrides skill_name).",
    )
    args = parser.parse_args()
    if not args.skill_name and not args.skill_dir:
        parser.error("either skill_name or --skill-dir is required")
    return args


def main() -> int:
    args = parse_args()
    skill_dir = resolve_skill_dir(args)
    live, message = check_skill_live(skill_dir)
    print(message)
    return 0 if live else 1


if __name__ == "__main__":
    raise SystemExit(main())
