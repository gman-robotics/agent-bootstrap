# ub-mode practice (hub)

Use **`/ub-mode`** or load `skills/ub-mode/SKILL.md` when you want the reduced loop: Make it Work, Make it Right, Practice. It complements `plan-code-review-workflow` and does not replace TDD (`write-tests`).

## Advisory vs blocking

**Advisory (hub default — GMA-410 rollout):** Run gates in the implementer pre-PR dev flow and in CI on every `push` and `pull_request`; report honest measured results on the PR **`Gates:`** line. Gate **findings** **do not** block QA **APPROVE** and **do not** count as review rounds until Tom explicitly approves **blocking mode**. Roll out on **systemone** and **packet** first; measure review rounds per PR before and after. No blocking mode until Tom OKs.

**Gate miss:** When **`ub-gates`** is **red/missing** for infrastructure errors, the reviewer hands the PR back to the implementer (**not** a review round). **`scripts/run_ub_gates_ci.sh` defaults to blocking** (`UB_GATES_ADVISORY=0`). In that mode **`skipped_tools_missing`**, **`tool_error`**, **`skipped_mutator`**, and findings exit **1**. **`skipped_no_scope`** exits **0**. **`run_ub_gates_report.sh` sets `UB_GATES_ADVISORY=1`** and still exits 0. A blocking mutator skip (`UB_GATES_SKIP_MUTATOR=1` or `CURSOR_AGENT` without `GITHUB_ACTIONS`) is **`skipped_mutator`**, not **`ran_clean`**. A mutator budget timeout stays non-blocking, and the step summary's first line states the timeout. **`outcome=tool_error`** means the tools did not run correctly (dryer exit other than `0`, including `1` and `2`, even when `.metrics/dry.edn` exists; missing `.metrics/dry.edn` after dryer exit `0`; mutator exit `2`; failed `git diff --name-only`; missing merge base) — **not** `ran_clean`. `.pyi` and `.d.ts` are outside gate scope. In advisory mode (`UB_GATES_ADVISORY=1`) those same outcomes are reported and the process exits 0.

## When to use

| Situation | Use ub-mode |
| --- | --- |
| Implementing a feature or fix in a supported language | Yes — phases 1–3 |
| PR review | Confirm CI `ub-gates` outcome at head SHA only (do not re-run tools) |
| Docs-only or Markdown hub skill edit | Phase 1 judgment only; `Gates: N/A (hub Markdown)` |
| Whole-repo audit | No — use `codebase-simplification-audit` |

## PR body header (hub PRs)

**Canonical template:** `docs/shared/hub-pull-request-template.md` (GitHub copy: `.github/PULL_REQUEST_TEMPLATE.md`). Do not maintain a second header order elsewhere.

Required top-of-body order (GMA-412 / arm rule): `Tier:`, `Models:`, `Linear:` (`https://linear.app/...` or `N/A` only), `Summary:`, `Gates:`, then **pstack (Poteto) principles cited**, then verification evidence/checklist.

Use `Linear: N/A` when there is no tracking issue. Tier meanings: see **Tier scale** in `docs/shared/repo-standards-practice.md` (T0 small/docs/check-only through T3 infra/migration/new service).

**Linear line:** Must be an `https://linear.app/...` issue URL, or `N/A`. Never use a Cursor store path, box path, or sketch link. Do not use angle-bracket placeholders in committed examples.

For hub Markdown-only PRs, use `Gates: N/A (hub Markdown)`.

Workflow skills point here: `skills/technical-writing/SKILL.md`, `skills/lfg/SKILL.md`, `skills/multi-harness-coordination/SKILL.md`, `skills/split-branch-for-pr/SKILL.md`, `skills/adversarial-coordination-workflow/SKILL.md`, `skills/create-repo-standards/SKILL.md`, `skills/maintain-repo-standards/SKILL.md`.

## Prerequisites (repo / CI)

Before ub-gates can run in CI or locally:

| Prerequisite | Why |
| --- | --- |
| **Coverage in CI** | **crapper** and **mutator** need an LCOV or coverage profile (e.g. `pytest --cov` / `pytest-cov`, JaCoCo, `go test -coverprofile`, per `skills/ub-mode/references/gates-by-language.md`) |
| **Explicit scope paths** | Upstream `--changed` uses **`git status`** (uncommitted adds/edits), not the PR diff. For committed branches and CI, pass the merge-base file list (see below). Do not claim “git diff selection” for `--changed`. |
| **crapper, dryer, mutator on PATH** | Or project-root `./crapper` wrappers; **mutator** expects **crapper** beside it per upstream README |

Hub CI: workflow job **`ub-gates`** runs the composite action, which calls `bash scripts/run_ub_gates_ci.sh` with advisory **0**, on every **`push`** and **`pull_request`**. Checkout uses **`fetch-depth: 0`**. The script also fetches **`UB_GATES_BASE_REF`** with no depth limit and unshallows a shallow clone. It writes `.metrics/ub-gates-outcome.txt` and a GitHub step summary (plus **`::warning`** when tools are missing). **`skipped_tools_missing`** exits **1** in this blocking default (`gates_ran=0`, not a pass). **`UB_GATES_ADVISORY=1`** is report-only and is set by `run_ub_gates_report.sh`, not by a direct call.

The **`verify-hub`** job uses default checkout (**depth 1**) and runs `verify-hub-ci` (doctor, drives, optional local `run_ub_gates_report.sh`). **Reviewers confirm ub-mode gates from the `ub-gates` job at head SHA**, not from `verify-hub` (shallow checkout may skip or skew merge-base scope).

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
3. **`tool_error`**: tool failure or missing dryer snapshot — not clean, not a quality finding; handback; **not** a review round.
4. **`skipped_no_scope`**: OK when the PR has no gate-relevant sources.
5. **`skipped_tools_missing`** (`gates_ran=0`): gates did **not** run — not a pass; note or handback; **not** a review round. Red/missing check for other failures: gate miss.

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

Summarize on the PR **`Gates:`** line. In advisory mode, gate debt on the **`Gates:`** line is not an APPROVE blocker. **`skipped_tools_missing`** must be called out explicitly (not “gates green”).
