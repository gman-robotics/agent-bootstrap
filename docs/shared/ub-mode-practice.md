# ub-mode practice (hub)

Use **`/ub-mode`** or load `skills/ub-mode/SKILL.md` when you want the reduced loop: Make it Work, Make it Right, Practice. It complements `plan-code-review-workflow` and does not replace TDD (`write-tests`).

## Advisory vs blocking

**Advisory (hub default — GMA-410 rollout):** Run gates in the implementer pre-PR dev flow and in CI on every `push` and `pull_request`; report honest measured results on the PR **`Gates:`** line. Gate **findings** **do not** block QA **APPROVE** and **do not** count as review rounds until Tom explicitly approves **blocking mode**. Roll out on **systemone** and **packet** first; measure review rounds per PR before and after. No blocking mode until Tom OKs.

**Gate miss (advisory):** When the **`ub-gates`** CI check is **red** or **missing** at the PR head SHA — including **`skipped_tools_missing`** or other infrastructure skips when gate-relevant files changed — the reviewer hands the PR back to the implementer. That handback is **not** a review round. A **green** `ub-gates` with **`skipped_no_scope`** is OK for docs-only PRs. A **green** `ub-gates` with **`ran_with_findings`** means tools ran; findings are advisory until blocking mode.

## When to use

| Situation | Use ub-mode |
| --- | --- |
| Implementing a feature or fix in a supported language | Yes — phases 1–3 |
| PR review | Confirm CI `ub-gates` outcome at head SHA only (do not re-run tools) |
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
| **Explicit scope paths** | Upstream `--changed` uses **`git status`** (uncommitted adds/edits), not the PR diff. For committed branches and CI, pass the merge-base file list (see below). Do not claim “git diff selection” for `--changed`. |
| **crapper, dryer, mutator on PATH** | Or project-root `./crapper` wrappers; **mutator** expects **crapper** beside it per upstream README |

Hub CI: workflow job **`ub-gates`** runs `bash scripts/run_ub_gates_ci.sh` on every **`push`** and **`pull_request`**. The script writes `.metrics/ub-gates-outcome.txt` and a GitHub step summary. **`skipped_tools_missing`** fails the job (gate miss). Advisory mode still allows **`ran_with_findings`** to exit 0.

## Scope file list (committed diff)

```bash
BASE="$(git merge-base HEAD origin/main)"
# Add only paths that exist and match your stack (see gates-by-language.md)
mapfile -t SCOPE < <(git diff --name-only --diff-filter=ACMRT "${BASE}" HEAD)
```

Hub CI uses the same merge-base → `HEAD` list (gate-relevant extensions only). Pass those paths to the tools:

```bash
crapper --threshold 10 "${SCOPE[@]}"
rm -f .metrics/dry.edn && dryer --threshold 0.8 "${SCOPE[@]}"
mutator "${SCOPE[@]}"
```

## Pre-PR dev flow (implementer)

Before opening a PR (`plan-code-review-workflow` Phase 2.75, `lfg` step 3.4–3.5):

1. Tests green for the scoped change.
2. Build **SCOPE** (above) or use **`--changed`** only while you still have **uncommitted** gate-relevant edits (`git status`).
3. `crapper --threshold 10` on SCOPE — **fix** anything it flags before you open the PR.
4. `rm -f .metrics/dry.edn` then `dryer --threshold 0.8` on SCOPE — **fix** candidates ≥ 0.8 (read `.metrics/dry.edn`; dryer exit `0` is not “clean”).
5. **`mutator`** on SCOPE on a **laptop** or in **CI** only — **never** in a cloud agent. Upstream **`--changed`** selects **changed source files** from `git status`; use **`--since-last-run`** for function-level reruns after the first pass.
6. Record measured exits, dryer candidates, and `.metrics/ub-gates-outcome.txt` / CI outcome on the PR **`Gates:`** line.

Cloud agents may run steps 3–4 when tools are on PATH; skip mutator and rely on CI for step 5.

## Reviewer (CI confirmation only)

In `expert-pr-review` Step 3.5 and `plan-code-review-workflow` Phase 3:

1. At the PR **head SHA**, read CI check **`ub-gates`** and the job log / step summary / `.metrics/ub-gates-outcome.txt` (`outcome=...`). **Do not** re-run crapper, dryer, or mutator locally.
2. **`ran_clean`** or **`ran_with_findings`**: tools executed; advisory findings do not block APPROVE.
3. **`skipped_no_scope`**: OK when the PR has no gate-relevant sources.
4. **`skipped_tools_missing`**, red check, or missing check: gate miss → implementer handback; **not** a review round.

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
3. **dryer**: delete `.metrics/dry.edn` before run (GMA-411); parse `.metrics/dry.edn` for `:score` ≥ 0.8.
4. **mutator**: exit `0` / `2` / `3` (survivors) and `.metrics/mutate/` (laptop or CI only).
5. **CI outcome** line from `ub-gates` when present (`outcome=`, `gate_miss=`).

Summarize on the PR **`Gates:`** line. In advisory mode, gate debt on the **`Gates:`** line is not an APPROVE blocker; a **red/missing `ub-gates`** or **`skipped_tools_missing`** is a gate miss for handback.
