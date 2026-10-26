# ub-mode practice (hub)

Use **`/ub-mode`** or load `skills/ub-mode/SKILL.md` when you want the reduced loop: Make it Work, Make it Right, Practice. It complements `plan-code-review-workflow` and does not replace TDD (`write-tests`).

## Advisory vs blocking

**Advisory (hub default — GMA-410 rollout):** Run gates on every push in CI and in the implementer pre-PR dev flow; report honest measured results on the PR **`Gates:`** line. Gate findings **do not** block QA **APPROVE** and **do not** count as review rounds until Tom explicitly approves **blocking mode**. Roll out on **systemone** and **packet** first; measure review rounds per PR before and after. No blocking mode until Tom OKs.

**Gate miss (advisory):** When the **`ub-gates`** CI check is **missing** or **red** at the PR head SHA, the reviewer hands the PR back to the implementer. That handback is **not** a review round and must **not** use **REQUEST_CHANGES** for code-quality findings.

## When to use

| Situation | Use ub-mode |
| --- | --- |
| Implementing a feature or fix in a supported language | Yes — phases 1–3 |
| PR review | Confirm CI ub-gates at head SHA only (do not re-run tools) |
| Docs-only or Markdown hub skill edit | Phase 1 judgment only; `Gates: N/A (hub Markdown)` |
| Whole-repo audit | No — use `codebase-simplification-audit` |

## PR body header (hub PRs)

When the hub defines PR body fields, use this **order** at the top of the description (adapt values per PR):

```text
Tier: T0
Models: composer-2.5
Linear: https://linear.app/gman-personal-projects/issue/GMA-412
Summary: one short paragraph
Gates: crapper/dryer/mutator advisory results or skip reason
```

Use `Linear: N/A` when there is no tracking issue. Tier meanings: see **Tier scale** in `docs/shared/repo-standards-practice.md` (T0 small/docs/check-only through T3 infra/migration/new service).

Then add verification evidence (commands + exit codes) and any checklist aligned with CI.

**Linear line:** Must be an `https://linear.app/...` issue URL, or `N/A`. Never use a Cursor store path, box path, or sketch link. Do not use angle-bracket placeholders in committed examples.

For hub Markdown-only PRs, use `Gates: N/A (hub Markdown)`.

The same stanza appears in `skills/technical-writing/SKILL.md`, `skills/lfg/SKILL.md`, `skills/multi-harness-coordination/SKILL.md`, `skills/split-branch-for-pr/SKILL.md`, and `skills/adversarial-coordination-workflow/SKILL.md`.

## Prerequisites (repo / CI)

Before ub-gates can run in CI or locally:

| Prerequisite | Why |
| --- | --- |
| **Coverage in CI** | **crapper** and **mutator** need an LCOV or coverage profile (e.g. `pytest --cov` / `pytest-cov`, JaCoCo, `go test -coverprofile`, per `skills/ub-mode/references/gates-by-language.md`) |
| **`dryer --changed`** | Upstream [unclebob/dryer](https://github.com/unclebob/dryer) must support `--changed` (git diff selection). If a pinned dryer build has no `--changed`, document that as a prerequisite — do not invent a substitute |
| **crapper, dryer, mutator on PATH** | Or project-root `./crapper` wrappers; **mutator** expects **crapper** beside it per upstream README |

Hub CI: workflow job **`ub-gates`** runs `bash scripts/run_ub_gates_ci.sh` on every push (advisory: `continue-on-error: true` until blocking mode).

## Pre-PR dev flow (implementer)

Before opening a PR (`plan-code-review-workflow` Phase 2.75, `lfg` step 3.4–3.5):

1. Tests green for the scoped change.
2. `crapper --changed --threshold 10` — fix anything it flags before you open the PR.
3. `rm -f .metrics/dry.edn` then `dryer --changed --threshold 0.8` — fix duplication candidates ≥ 0.8 before you open the PR.
4. **`mutator --changed`** on **changed functions only** — run on a **laptop** or in **CI** only. **Never** run mutator in a **cloud agent** harness.
5. Record measured exits and paths on the PR **`Gates:`** line.

Cloud agents may run steps 2–3 when tools are on PATH; skip mutator and rely on CI for step 4.

## Reviewer (CI confirmation only)

In `expert-pr-review` Step 3.5 and `plan-code-review-workflow` Phase 3:

1. At the PR **head SHA**, confirm the **`ub-gates`** CI check completed (green preferred; red = gate miss).
2. **Do not** re-run crapper, dryer, or mutator locally or in the reviewer harness.
3. On gate miss, ask the implementer to fix and re-push; do **not** count that as a review round.

## How tools pair with principles

| Tool | Enforces (principle names) |
| --- | --- |
| **write-tests** + your test runner | test-behavior-not-implementation, prove-it-works |
| **crapper** | fix-root-causes on complexity risk; sequence-verifiable-units per function |
| **dryer** | subtract-before-you-add on duplicate structure |
| **mutator** | test-behavior-not-implementation; prove-it-works on surviving mutants |
| **uml-viewer** | Optional picture of `.metrics/` for humans |

Definitions of principle names live only in `skills/pstack-principles/SKILL.md`.

## Evidence to report (advisory)

1. Test command and exit code.
2. **crapper**: worst CRAP ≤ 10 or the exceeding value (`.metrics/crap.edn` or stdout).
3. **dryer**: delete `.metrics/dry.edn` before run (GMA-411); if file missing after `--changed` with no selection, say **no selection/skipped**; else list `:candidates` with `:score` ≥ 0.8.
4. **mutator**: exit `0` / `2` / `3` (survivors) and `.metrics/mutate/` (laptop or CI only).
5. Skip reasons when a tool is not installed.

Summarize on the PR **`Gates:`** line. In advisory mode, gate debt on the **`Gates:`** line is not an APPROVE blocker; a **red/missing `ub-gates` CI check** at head SHA is still a gate miss for handback.
