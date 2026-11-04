# Review cap and autonomy tiers (v1)

The numbers and action names live in one file:
`docs/shared/policy/review-autonomy.json`. This page explains them and does
not repeat them. `scripts/review_policy.py` is the only code that reads the
file. Change the JSON, not this page, when a rule changes.

## Review cap

- Each review round is a fresh session at the policy model.
- The cap comes from the PR `Tier:` (T0–T3, see **Tier scale** in
  `docs/shared/repo-standards-practice.md`). A PR is "small" when it is a
  small tier or carries a small label; a small PR uses the small cap.
- No new round on an unchanged head SHA.
- One round past the cap is allowed only on a small PR, and only with the
  approver named in `review.cap_plus_one_approver`.
- The verdict comment's first line is
  `Verdict: APPROVE|REVISE @sha (round N/cap, model)`.

```bash
python3 scripts/review_policy.py cap --tier T1 [--label small]
python3 scripts/review_policy.py check-round --tier T1 --pr 123   # exit 0 ok, 3 stop
python3 scripts/review_policy.py format-verdict APPROVE <sha> 1 --tier T1
python3 scripts/review_policy.py lint-verdict "Verdict: ..."
```

`check-round` reads the PR head and its verdict comments with `gh pr view`
and prints `ok`, `unchanged_sha`, `cap_reached`, or
`cap_plus_one_needs_<approver>`. Anything but `ok` means stop and ask.
Several verdicts on one SHA count as one round. After the approver OKs the
extra round, rerun with `--morgan-ok`.

Docs PRs are T0 on the tier scale, so they are small. A docs PR filed at a
higher tier needs the `small` label to get the small cap and the extra round.

Merges: `merge_approver` reads the JSON. A must-fix blocks every merge. An
APPROVE merges by `merge-approved-pr` (or `merge-greenfield-poc-no-ci`). A
REVISE merges only when the PR is docs-only and the verdict used the last
allowed round.

## Autonomy tiers

Each action name in the JSON maps to one approver:

| Approver | Meaning |
| --- | --- |
| `self` | Tier 1. The agent acts, then tells the coordinator. |
| `morgan` | Tier 2. The coordinator (chief-of-staff agent) approves first. |
| `tom` | The owner keeps it. Only the owner's own words approve it. |

An action that is not in the JSON goes to the owner.

```bash
python3 scripts/review_policy.py approver system-install-pinned
```

## CI

Advisory only. `scripts/advisory_pr_body_format.py` warns when the PR
`Tier:` value is not a policy tier. It never fails the job.
