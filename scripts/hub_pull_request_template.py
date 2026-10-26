#!/usr/bin/env python3
"""Shared helpers for hub PR template body (GMA-410). Body starts at the first `Tier:` line."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_DOC = REPO_ROOT / "docs" / "shared" / "hub-pull-request-template.md"
GITHUB_TEMPLATE = REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"

GITHUB_CANONICAL_SOURCE_PREFIX = "<!-- Canonical source:"

# Single copy/check invocations referenced by skills and docs (path placeholder only).
COPY_COMMAND = (
    "mkdir -p .github\n"
    "python3 /path/to/agent-bootstrap/scripts/hub_pull_request_template.py "
    "copy --out .github/PULL_REQUEST_TEMPLATE.md"
)
CHECK_COMMAND = (
    "python3 /path/to/agent-bootstrap/scripts/hub_pull_request_template.py "
    "check --file .github/PULL_REQUEST_TEMPLATE.md"
)


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


def hub_root_from_args(hub_root: Path | None) -> Path:
    return (hub_root or REPO_ROOT).resolve()


def read_canonical_github_body(hub_root: Path | None = None) -> str:
    doc = hub_root_from_args(hub_root) / "docs" / "shared" / "hub-pull-request-template.md"
    return body_from_canonical_markdown(doc.read_text(encoding="utf-8"))


def read_committed_github_body() -> str:
    return normalize_github_pr_template(GITHUB_TEMPLATE.read_text(encoding="utf-8"))


def check_pr_template_file(hub_root: Path, pr_template: Path) -> str | None:
    """Return None if match, else a short error message."""
    expected = read_canonical_github_body(hub_root)
    if not pr_template.is_file():
        return f"missing {pr_template}"
    actual = normalize_github_pr_template(pr_template.read_text(encoding="utf-8"))
    if actual != expected:
        return (
            f"{pr_template} body (from Tier:, canonical footer stripped) "
            "does not match hub docs/shared/hub-pull-request-template.md"
        )
    return None


def cmd_copy(hub_root: Path, out: Path) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    body = read_canonical_github_body(hub_root)
    out.write_text(body, encoding="utf-8")
    return 0


def cmd_check(hub_root: Path, pr_file: Path) -> int:
    err = check_pr_template_file(hub_root, pr_file)
    if err:
        print(err, file=sys.stderr)
        return 1
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hub-root",
        type=Path,
        default=None,
        help="agent-bootstrap root (default: parent of scripts/)",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    copy_p = sub.add_parser("copy", help="Write GitHub PR template body starting at Tier:")
    copy_p.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Destination .github/PULL_REQUEST_TEMPLATE.md path",
    )
    check_p = sub.add_parser("check", help="Verify PR template matches hub canonical Tier: body")
    check_p.add_argument(
        "--file",
        type=Path,
        required=True,
        help="Path to .github/PULL_REQUEST_TEMPLATE.md to verify",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    hub_root = hub_root_from_args(args.hub_root)
    if args.command == "copy":
        return cmd_copy(hub_root, args.out)
    if args.command == "check":
        return cmd_check(hub_root, args.file)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
