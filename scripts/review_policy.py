#!/usr/bin/env python3
"""Review cap and autonomy tiers v1 (GMA-552).

The numbers and action names live in docs/shared/policy/review-autonomy.json.
This module only reads them. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

POLICY_PATH = Path(__file__).resolve().parent.parent / "docs" / "shared" / "policy" / "review-autonomy.json"
DECISIONS = ("APPROVE", "REVISE")
VERDICT_RE = re.compile(
    r"^Verdict: (?P<decision>APPROVE|REVISE) @(?P<sha>[0-9a-f]{7,40}) "
    r"\(round (?P<round>\d+)/(?P<cap>\d+), (?P<model>[^)]+)\)$"
)


@dataclass(frozen=True)
class Verdict:
    decision: str
    sha: str
    round: int
    cap: int
    model: str


def load_policy(path: Path | None = None) -> dict:
    return json.loads((path or POLICY_PATH).read_text(encoding="utf-8"))


def is_small(policy: dict, tier: str, labels: list[str] | tuple[str, ...] = ()) -> bool:
    review = policy["review"]
    return tier in review["small_tiers"] or any(label in review["small_labels"] for label in labels)


def cap_for(policy: dict, tier: str, labels: list[str] | tuple[str, ...] = ()) -> int:
    caps = policy["review"]["caps"]
    if tier not in caps:
        raise ValueError(f"unknown tier {tier!r}; expected one of {sorted(caps)}")
    if is_small(policy, tier, labels):
        return min(caps[tier], caps[policy["review"]["small_tiers"][0]])
    return caps[tier]


def parse_verdict(text: str) -> Verdict | None:
    first = text.strip().splitlines()[0] if text.strip() else ""
    match = VERDICT_RE.match(first.strip())
    if not match:
        return None
    return Verdict(match["decision"], match["sha"], int(match["round"]), int(match["cap"]), match["model"])


def format_verdict(decision: str, sha: str, round_no: int, cap: int, model: str) -> str:
    if decision not in DECISIONS:
        raise ValueError(f"decision must be one of {DECISIONS}")
    return f"Verdict: {decision} @{sha} (round {round_no}/{cap}, {model})"


def same_sha(a: str, b: str) -> bool:
    return a.startswith(b) or b.startswith(a)


def next_round(policy: dict, history: list[Verdict], head_sha: str, tier: str,
               labels: list[str] | tuple[str, ...] = ()) -> tuple[str, int]:
    """Return (status, round) for the next review round.

    status is ok, unchanged_sha, cap_reached, or cap_plus_one_needs_<approver>.
    """
    next_no = len(history) + 1
    if any(same_sha(v.sha, head_sha) for v in history):
        return "unchanged_sha", next_no
    cap = cap_for(policy, tier, labels)
    if next_no <= cap:
        return "ok", next_no
    if next_no == cap + 1 and is_small(policy, tier, labels):
        return f"cap_plus_one_needs_{policy['review']['cap_plus_one_approver']}", next_no
    return "cap_reached", next_no


def approver_for(policy: dict, action: str) -> str:
    return policy["actions"].get(action, policy["default_approver"])


def merge_approver(policy: dict, decision: str, must_fixes: int, docs_only: bool,
                   greenfield_no_ci: bool) -> str:
    """Who may merge. Returns an approver name or 'blocked'."""
    if greenfield_no_ci and decision == "APPROVE":
        return approver_for(policy, "merge-greenfield-poc-no-ci")
    if decision == "APPROVE":
        return "morgan"
    if docs_only and must_fixes == 0:
        return approver_for(policy, "merge-docs-only-final-revise-no-must-fix")
    return "blocked"


def lint_verdict(policy: dict, text: str) -> list[str]:
    verdict = parse_verdict(text)
    if verdict is None:
        return ["first line is not 'Verdict: APPROVE|REVISE @sha (round N/cap, model)'"]
    errors: list[str] = []
    caps = set(policy["review"]["caps"].values())
    if verdict.cap not in caps:
        errors.append(f"cap {verdict.cap} is not a policy cap {sorted(caps)}")
    if verdict.round < 1 or verdict.round > verdict.cap + 1:
        errors.append(f"round {verdict.round} is outside 1..{verdict.cap + 1}")
    if verdict.model != policy["review"]["model"]:
        errors.append(f"model {verdict.model!r} is not {policy['review']['model']!r}")
    return errors


def verdicts_from_comments(comments: list[dict]) -> list[Verdict]:
    found = (parse_verdict(c.get("body", "")) for c in comments)
    return [v for v in found if v is not None]


def _pr_view(pr: str) -> dict:
    out = subprocess.run(
        ["gh", "pr", "view", pr, "--json", "headRefOid,comments,labels"],
        check=True, capture_output=True, text=True,
    )
    return json.loads(out.stdout)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=None)
    sub = parser.add_subparsers(dest="cmd", required=True)
    cap = sub.add_parser("cap", help="print the round cap")
    cap.add_argument("--tier", required=True)
    cap.add_argument("--label", action="append", default=[])
    appr = sub.add_parser("approver", help="print who approves an action")
    appr.add_argument("action")
    lint = sub.add_parser("lint-verdict", help="check a verdict line")
    lint.add_argument("text")
    fmt = sub.add_parser("format-verdict", help="print a verdict line")
    fmt.add_argument("decision", choices=DECISIONS)
    fmt.add_argument("sha")
    fmt.add_argument("round", type=int)
    fmt.add_argument("--tier", required=True)
    fmt.add_argument("--label", action="append", default=[])
    chk = sub.add_parser("check-round", help="may the next review round run?")
    chk.add_argument("--tier", required=True)
    chk.add_argument("--label", action="append", default=[])
    src = chk.add_mutually_exclusive_group(required=True)
    src.add_argument("--pr", help="PR number or URL (reads gh pr view)")
    src.add_argument("--pr-json", type=Path, help="saved `gh pr view --json headRefOid,comments,labels`")
    return parser.parse_args(argv)


def _check_round(policy: dict, args: argparse.Namespace) -> int:
    data = json.loads(args.pr_json.read_text()) if args.pr_json else _pr_view(args.pr)
    labels = list(args.label) + [lab.get("name", "") for lab in data.get("labels", [])]
    history = verdicts_from_comments(data.get("comments", []))
    status, round_no = next_round(policy, history, data["headRefOid"], args.tier, labels)
    print(f"{status} round={round_no} cap={cap_for(policy, args.tier, labels)}")
    return 0 if status == "ok" else 3


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    policy = load_policy(args.policy)
    try:
        if args.cmd == "cap":
            print(cap_for(policy, args.tier, args.label))
            return 0
        if args.cmd == "approver":
            print(approver_for(policy, args.action))
            return 0
        if args.cmd == "format-verdict":
            cap = cap_for(policy, args.tier, args.label)
            print(format_verdict(args.decision, args.sha, args.round, cap, policy["review"]["model"]))
            return 0
        if args.cmd == "lint-verdict":
            errors = lint_verdict(policy, args.text)
            for err in errors:
                print(err, file=sys.stderr)
            return 1 if errors else 0
        return _check_round(policy, args)
    except ValueError as err:
        print(f"review_policy: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
