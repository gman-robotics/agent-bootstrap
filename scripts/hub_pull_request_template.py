#!/usr/bin/env python3
"""Shared helpers for hub PR template body (GMA-410). Body starts at the first `Tier:` line."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_DOC = REPO_ROOT / "docs" / "shared" / "hub-pull-request-template.md"
GITHUB_TEMPLATE = REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"

GITHUB_CANONICAL_SOURCE_PREFIX = "<!-- Canonical source:"


def body_from_canonical_markdown(text: str) -> str:
    """Extract GitHub template body: from first line starting with `Tier:` through EOF."""
    lines = text.splitlines()
    out: list[str] = []
    found = False
    for line in lines:
        if line.startswith("Tier:"):
            found = True
        if found:
            out.append(line)
    if not out:
        raise ValueError("canonical markdown has no Tier: line")
    return "\n".join(out).rstrip() + "\n"


def normalize_github_pr_template(text: str) -> str:
    """Drop the optional trailing Canonical source HTML comment before compare."""
    lines = [
        line
        for line in text.splitlines()
        if not line.strip().startswith(GITHUB_CANONICAL_SOURCE_PREFIX)
    ]
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines).rstrip() + "\n"


def read_canonical_github_body() -> str:
    return body_from_canonical_markdown(CANONICAL_DOC.read_text(encoding="utf-8"))


def read_committed_github_body() -> str:
    return normalize_github_pr_template(GITHUB_TEMPLATE.read_text(encoding="utf-8"))
