#!/usr/bin/env python3
"""Check that an evidence/INDEX.md is progressive disclosure, not a full dump (H-5).

Modeled on this hub's own skills/INDEX.md convention: each iteration gets a short
summary line plus a pointer to its `evidence/E_<n>.json` (or `evidence/E_t.json`) file,
never the packet's own fields pasted inline. Two structural checks:

1. None of the raw E_t field names (`execution_records`, `claim_id`,
   `planner_handoff`, `verified_records`, `gap_records`) appear in the index -- their
   presence means someone pasted packet content instead of summarizing it.
2. At least one `evidence/E_<n>.json` or `evidence/E_t.json` pointer is present, so the
   index actually links to the underlying files it is progressively disclosing.

Usage:
    python3 scripts/check_evidence_index_is_progressive.py <INDEX.md>

Exit codes: 0 = progressive, 1 = not progressive (full dump and/or no pointer).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FULL_DUMP_MARKERS = (
    "execution_records",
    "claim_id",
    "planner_handoff",
    "verified_records",
    "gap_records",
)
POINTER_RE = re.compile(r"evidence/E_(t|\d+)\.json")


def check_progressive(text: str) -> list[str]:
    """Return one violation message per problem; empty list means the index is progressive."""
    violations = []
    for marker in FULL_DUMP_MARKERS:
        if marker in text:
            violations.append(
                f"index is not progressive: contains raw E_t field {marker!r} -- "
                "link to the file instead of pasting its contents (H-5)"
            )
    if not POINTER_RE.search(text):
        violations.append(
            "index is not progressive: no evidence/E_<n>.json (or evidence/E_t.json) "
            "pointer found (H-5)"
        )
    return violations


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", help="path to the evidence/INDEX.md file")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    text = Path(args.path).read_text(encoding="utf-8")
    violations = check_progressive(text)
    if violations:
        for violation in violations:
            print(violation)
        return 1
    print("progressive: index links to evidence files instead of dumping their contents (H-5)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
