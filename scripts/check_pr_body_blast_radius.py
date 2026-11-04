#!/usr/bin/env python3
"""Blocking PR body blast-radius section check (GMA-509)."""

from __future__ import annotations

import os
import re
import sys

_HEADING = "## blast radius"
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_UNCHECKED_BOX = re.compile(r"^\s*[-*]\s*\[ \]")

MISSING = "Missing `## Blast radius` section (hub template, GMA-509)"
EMPTY = (
    "`## Blast radius` section is empty: describe the blast radius, "
    "tick the checkbox, or write `N/A (docs-only)`"
)


def section_text(body: str) -> str | None:
    """Return the body of the first `## Blast radius` section, or None if absent."""
    lines = body.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if line.strip().lower() == _HEADING:
            start = index
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## ") or lines[index].startswith("# "):
            end = index
            break
    return "\n".join(lines[start + 1 : end])


def meaningful(text: str) -> str:
    """Drop HTML comments and unchecked boxes; return the remaining text."""
    without_comments = _COMMENT.sub("", text)
    kept = [line for line in without_comments.splitlines() if not _UNCHECKED_BOX.match(line)]
    return "\n".join(kept).strip()


def check_body(body: str) -> list[str]:
    text = section_text(body)
    if text is None:
        return [MISSING]
    if not meaningful(text):
        return [EMPTY]
    return []


def main() -> int:
    body = os.environ.get("PR_BODY", "")
    if not body and not sys.stdin.isatty():
        body = sys.stdin.read()
    errors = check_body(body)
    for msg in errors:
        print(f"::error title=PR body blast radius::{msg}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
