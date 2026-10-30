---
name: lfg
description: "Use to run the agreed loop hands-off: route, implement, simplify the diff, review against the plan, compound, push a PR, watch CI. Do not merge unless the human granted it."
version: 1.0.6
---

# lfg — Run the loop, do not merge

**Purpose**
Compose skills that already exist. Do not reimplement them. The pipeline stops on a settled decision that the review invalidates. Merge stays with the human unless they granted it.

**Trigger**
"lfg", "run the loop", "ship this hands-off", after a plan or a bug report that should become a PR.

**Do not use for**
- Direction not chosen and a human is here → `ideate` then `grill-with-docs`
- A whole-repo simplification audit → `codebase-simplification-audit`
- Merge → human, or an explicit grant recorded in the ticket

## Steps
1. Route. Failing behavior → `debug-investigation`. Unsettled product shape with a human present → `grill-with-docs`. Unsettled judgment → `interrogate`. A costly shape still open → `arena`. Otherwise require an implementation-ready plan from `plan-code-review-workflow` Phase 1.
2. Implement on an isolated branch with `write-tests`. Do not call an open PR shipped.
3. Simplify the fresh diff before review. Behavior stays. This is not `codebase-simplification-audit`.
3.4. Pre-PR dev flow: before the PR, run dryer, crapper, and mutator on the new code (`bash scripts/ub_gates_container.sh`; no host installs; `UB_GATES_ADVISORY=0`). Usage: `Usage: bash scripts/ub_gates_container.sh [--help] [--worktree PATH] [--main-git PATH] [--metrics-dir PATH]`. Scope is changed functions (crapper `--threshold 10`) and changed lines (dryer `--threshold 0.8` after `rm -f .metrics/dry.edn`, mutator). Test paths, `.pyi`, and `.d.ts` are out of scope. See `docs/shared/ub-mode-practice.md`.
3.5. Act on the results before the PR. Fix blocking findings on changed code, or escalate them to the CoS. There is no waiver. Debt in untouched old functions does not block. Mutator budget is 20 minutes per PR; a timeout is reported, leads the summary, and does not block. A mutator skip is `skipped_mutator` and fails. The cloud-agent auto-skip (`CURSOR_AGENT` without `GITHUB_ACTIONS`) is the same failure: never in a cloud agent is not a pass. Run the container instead. Push so CI **`ub-gates`** runs (`scripts/run_ub_gates_ci.sh` defaults to blocking) and report results on the PR **`Gates:`** line in step 8 (real exits, findings, debt, and timeout). `skipped_tools_missing` (`gates_ran=0`) is not a gate pass; **`tool_error`** is not `ran_clean` (hand back); red/missing → implementer; not a review round. Advisory mode is only `scripts/run_ub_gates_report.sh` or `UB_GATES_ADVISORY=1`.
3.6. If the target project has `standards-<repo>/SKILL.md`, align the PR description with it and the hub template (`docs/shared/repo-standards-practice.md`, `docs/shared/hub-pull-request-template.md`).
3.7. Before review on non-docs PRs, run `skills/blast-radius/SKILL.md` on the merge-base changed surface (or spawn a worker with that skill); record top risks in the PR body or review handback.
4. Review against the plan with `expert-pr-review` (reviewer confirms **`ub-gates`** at head SHA only — no local gate re-run). A finding that invalidates a settled decision stops the pipeline.
5. Apply fixes. Put unapplied findings in the PR body.
6. Call `compound`. Honor its skip rule.
7. Run the stack's check (`black-box-agent-qa` for a skill, the project's tests otherwise).
8. Commit, push, open a PR. PR body must follow `docs/shared/hub-pull-request-template.md` (header order + Poteto section — see `docs/shared/ub-mode-practice.md`). Watch CI with `pr-shepherd`.
9. Do not merge, force-push, or delete data. Report DONE only when CI has decided and residuals are in the PR body.

## Companions

| Skill | Role here |
|---|---|
| `project-carry-through` | Ask the human only for a new decision or a manual action |
| `plan-code-review-workflow` | Plan, implement, simplify-the-diff, review |
| `ub-mode` | Implementer pre-PR dev flow (steps 3.4–3.5); reviewer reads CI outcome only |
| `compound` | Durable learning after verified work |
| `pr-shepherd` | CI and reviewer blockers after the PR exists |

## Provenance
Adapted from EveryInc/compound-engineering-plugin `lfg` (MIT, Copyright (c) 2025 Every). Independent rewrite. Children are hub skills. No plugin tree copied.

Last updated: 2026-10-30
