Tier: T1
<!-- T0 small/docs/check-only; T1 module fix/feature; T2 cross-cutting; T3 infra/migration. Full table: docs/shared/repo-standards-practice.md -->

Models: composer-2.5 implementer
<!-- Planner/reviewer/implementer models used on this PR -->

Linear: https://linear.app/gman-personal-projects/issue/GMA-000
<!-- Must be https://linear.app/... issue URL or `N/A` — never a Cursor store/box/sketch path -->

Summary:
<!-- One short paragraph: what changed and why -->

Gates:
<!-- Advisory ub-mode: crapper/dryer/mutator results, verify-ci outcome, or `N/A (hub Markdown)`; cite CI `ub-gates` at head SHA when applicable -->

## pstack (Poteto) principles cited

<!-- Name headings from skills/pstack-principles/SKILL.md (example: prove-it-works, sequence-verifiable-units). At least one for non-trivial PRs. -->

- prove-it-works:

## Verification evidence

<!-- Commands + exit codes; link heavy logs instead of pasting -->

- `python3 -m unittest discover -s tests` — exit 0

## Checklist

- [ ] Tests or verify skill run recorded above
- [ ] Blast radius considered (`skills/blast-radius/SKILL.md`) for non-docs diffs
- [ ] PR body matches `standards-<repo>` when that skill exists in this repo

<!-- Canonical source: docs/shared/hub-pull-request-template.md — edit there first, then copy to this file. -->
