#!/usr/bin/env python3
"""Report-only PR body format check (GMA-410). Emits GitHub ::warning lines; never fails the job."""

from __future__ import annotations

import os
import re
import sys

REQUIRED_LINES = ("Tier:", "Models:", "Linear:", "Summary:", "Gates:")
LINEAR_OK = re.compile(r"Linear:\s*(https://linear\.app/|N\/A\b)", re.I)
TIER_LINE = re.compile(r"^Tier:\s*(\S+)", re.M)


def _policy_tiers() -> list[str]:
    try:
        from scripts.review_policy import load_policy
    except ImportError:  # run as `python3 scripts/advisory_pr_body_format.py`
        from review_policy import load_policy

    return sorted(load_policy()["review"]["caps"])


def _tier_warnings(body: str) -> list[str]:
    try:
        tiers = _policy_tiers()
    except (OSError, ValueError, KeyError, TypeError) as err:
        return [f"Review policy unreadable, tier not checked: {err}"]
    tier = TIER_LINE.search(body)
    if tier and tier.group(1) not in tiers:
        return [f"Tier: {tier.group(1)} is not a policy tier {tiers} (docs/shared/policy/review-autonomy.json)"]
    return []


def check_body(body: str) -> list[str]:
    warnings: list[str] = []
    if not body.strip():
        warnings.append("PR body is empty")
        return warnings
    for field in REQUIRED_LINES:
        if field not in body:
            warnings.append(f"Missing `{field}` header (see docs/shared/hub-pull-request-template.md)")
    warnings.extend(_tier_warnings(body))
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
