---
name: lfg
description: "Use to run the agreed loop hands-off: route, implement, simplify the diff, review against the plan, compound, push a PR, watch CI. Do not merge unless the human granted it."
version: 1.0.5
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
3.4. Pre-PR dev flow: `crapper --threshold 10` and `dryer --threshold 0.8` on merge-base scope (`rm -f .metrics/dry.edn` first) per `docs/shared/ub-mode-practice.md`; **fix** what they flag before the PR.
3.5. `mutator` on merge-base **scope** — **laptop or CI only**; never in a cloud agent. Push so CI **`ub-gates`** runs the same scope; report results on the PR **`Gates:`** line in step 8. `skipped_tools_missing` (`gates_ran=0`) is not a gate pass; red/missing for other failures → implementer; not a review round. Advisory until Tom approves blocking mode.
3.6. If the target project has `standards-<repo>/SKILL.md`, align the PR description with it (`Tier:`, `Models:`, `Linear:`, `Summary:`, `Gates:`) before review (`docs/shared/repo-standards-practice.md`).
4. Review against the plan with `expert-pr-review` (reviewer confirms **`ub-gates`** at head SHA only — no local gate re-run). A finding that invalidates a settled decision stops the pipeline.
5. Apply fixes. Put unapplied findings in the PR body.
6. Call `compound`. Honor its skip rule.
7. Run the stack's check (`black-box-agent-qa` for a skill, the project's tests otherwise).
8. Commit, push, open a PR. PR body must follow hub header order (`Tier:`, `Models:`, `Linear:`, `Summary:`, **`Gates:`**, then evidence — see `docs/shared/ub-mode-practice.md`). Watch CI with `pr-shepherd`.
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
