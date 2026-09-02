#!/usr/bin/env python3
"""Check that a planner/development-document template reads the H-1 path convention.

H-1: the next planner must read the same `E_t.json` on disk before planning the next
iteration -- mem0/activeContext.md is explicitly not a substitute (the paper's own
Planner prompt template reads the prior evidence bundle directly, not a summarized
memory note). This check looks for the exact `evidence/E_t.json` path convention in a
plan-template markdown file.

Usage:
    python3 scripts/check_planner_reads_et.py <plan-template.md>

Exit codes: 0 = the required pointer is present, 1 = missing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REQUIRED_POINTER = "evidence/E_t.json"


def check_planner_reads_et(text: str) -> list[str]:
    """Return one violation message if the required H-1 pointer is missing."""
    if REQUIRED_POINTER not in text:
        return [
            f"missing required pointer: {REQUIRED_POINTER} "
            "(H-1: the next planner must read the same E_t.json on disk, "
            "not a mem0/activeContext.md summary)"
        ]
    return []


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", help="path to the plan/development-document template markdown file")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    text = Path(args.path).read_text(encoding="utf-8")
    violations = check_planner_reads_et(text)
    if violations:
        for violation in violations:
            print(violation)
        return 1
    print(f"ok: planner template reads {REQUIRED_POINTER} before planning (H-1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
