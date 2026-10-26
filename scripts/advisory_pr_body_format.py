#!/usr/bin/env python3
"""Report-only PR body format check (GMA-410). Emits GitHub ::warning lines; never fails the job."""

from __future__ import annotations

import os
import re
import sys

REQUIRED_LINES = ("Tier:", "Models:", "Linear:", "Summary:", "Gates:")
LINEAR_OK = re.compile(r"Linear:\s*(https://linear\.app/|N\/A\b)", re.I)


def check_body(body: str) -> list[str]:
    warnings: list[str] = []
    if not body.strip():
        warnings.append("PR body is empty")
        return warnings
    for field in REQUIRED_LINES:
        if field not in body:
            warnings.append(f"Missing `{field}` header (see docs/shared/hub-pull-request-template.md)")
    if not LINEAR_OK.search(body):
        warnings.append(
            "Linear: must be https://linear.app/... issue URL or N/A (arm rule)"
        )
    if "pstack (Poteto) principles cited" not in body and "Poteto" not in body:
        warnings.append(
            "Missing pstack (Poteto) principles cited section (hub template)"
        )
    return warnings


def main() -> int:
    body = os.environ.get("PR_BODY", "")
    if not body and not sys.stdin.isatty():
        body = sys.stdin.read()
    for msg in check_body(body):
        print(f"::warning title=PR body format::{msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
