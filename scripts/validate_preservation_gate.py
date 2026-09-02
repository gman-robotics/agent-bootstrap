#!/usr/bin/env python3
"""Validator for the Preservation Gate markdown field (GB-2).

Checks that a development-document markdown (`Dt`) contains the exact required
heading defined in skills/preservation-gate/SKILL.md -- `## Preservation Gate` -- with
at least one bullet naming a previously verified claim the current iteration's
Developer must not regress. This is distinct from REPEAT (see
skills/preservation-gate/SKILL.md's comparison table): Preservation Gate tracks
verified-good behavior to protect, REPEAT tracks a recurring failure class to block.

Usage:
    python3 scripts/validate_preservation_gate.py <Dt.md>

Exit codes: 0 = heading present with at least one bullet, 1 = missing or empty.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_HEADING = "## Preservation Gate"

_SECTION_RE = re.compile(re.escape(REQUIRED_HEADING) + r".*?(?=\n## |\Z)", re.DOTALL)


def _extract_section(text: str) -> str | None:
    match = _SECTION_RE.search(text)
    return match.group(0) if match else None


def check_preservation_gate(text: str) -> list[str]:
    """Return one violation message per problem; empty list means the section is valid."""
    section = _extract_section(text)
    if section is None:
        return [
            f"missing required heading: {REQUIRED_HEADING} "
            "(see skills/preservation-gate/SKILL.md -- distinct from REPEAT)"
        ]
    bullets = [line for line in section.splitlines() if line.strip().startswith("-")]
    if not bullets:
        return [
            f"{REQUIRED_HEADING} section has no bullets naming a previously verified "
            "claim to preserve"
        ]
    return []


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", help="path to the Dt development-document markdown file")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    text = Path(args.path).read_text(encoding="utf-8")
    violations = check_preservation_gate(text)
    if violations:
        for violation in violations:
            print(violation)
        return 1
    bullet_count = len([line for line in _extract_section(text).splitlines() if line.strip().startswith("-")])
    print(f"valid: {REQUIRED_HEADING} present with {bullet_count} bullet(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
