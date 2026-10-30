# ub-mode practice (hub)

Use **`/ub-mode`** or load `skills/ub-mode/SKILL.md` when you want the reduced loop: Make it Work, Make it Right, Practice. It complements `plan-code-review-workflow` and does not replace TDD (`write-tests`).

## Blocking by default

Dryer, crapper, and mutator (**ub-gates**) are **blocking** by default.

- `scripts/run_ub_gates_ci.sh` defaults to `UB_GATES_ADVISORY=0`.
- `.github/actions/ub-gates/action.yml` defaults input `advisory` to `"0"`.
- Advisory mode is only `scripts/run_ub_gates_report.sh`, or an explicit `UB_GATES_ADVISORY=1`. The report wrapper sets `UB_GATES_ADVISORY=1` and exits 0. A direct call of `run_ub_gates_ci.sh` does not.

In blocking mode these outcomes exit **1**: findings on changed code (`ran_with_findings`), `tool_error`, `skipped_tools_missing`, and `skipped_mutator`. `skipped_no_scope` and `ran_clean` exit **0**.

A mutator skip in blocking mode (`UB_GATES_SKIP_MUTATOR=1`, or `CURSOR_AGENT` without `GITHUB_ACTIONS`) is **`skipped_mutator`**. It fails. It is not **`ran_clean`**.

Mutator has a **20-minute** per-PR budget (`UB_GATES_MUTATOR_BUDGET_SECS` default `1200`). A timeout is reported. The step summary's first line states the timeout. A timeout does not block.

**`outcome=tool_error`** means the tools did not run correctly (dryer exit other than `0`, including `1` and `2`, even when `.metrics/dry.edn` exists; missing `.metrics/dry.edn` after dryer exit `0`; mutator exit `2`; failed `git diff --name-only`; missing merge base).

There is **no waiver**. Blocking findings on changed code are fixed, or escalated to the CoS.

**Gate miss:** When **`ub-gates`** is red or missing, the reviewer hands the PR back to the implementer. That handback is not a review round.

## Scope

Scope is **changed functions** for crapper and **changed lines** for dryer and mutator (`scripts/ub_changed_scope.py`).

The file list is the merge-base diff (`git diff --name-only` from the merge base to `HEAD`). The script then drops test paths, `.pyi`, and `.d.ts`. Those paths are out of scope.

Findings and debt in untouched old functions do not block. The outcome file records them as `crapper_debt` and `dryer_debt`. Only findings on changed scope fail the blocking job.

## When to use

| Situation | Use ub-mode |
| --- | --- |
| Implementing a feature or fix in a supported language | Yes — phases 1–3, then the pre-PR gates below |
| PR review | Confirm CI `ub-gates` outcome at head SHA only (do not re-run tools) |
| Docs-only or Markdown hub skill edit | Phase 1 judgment only; `Gates: N/A (hub Markdown)`; expect `skipped_no_scope` |
| Whole-repo audit | No — use `codebase-simplification-audit` |

## PR body header (hub PRs)

**Canonical template:** `docs/shared/hub-pull-request-template.md` (GitHub copy: `.github/PULL_REQUEST_TEMPLATE.md`). Do not maintain a second header order elsewhere.

Required top-of-body order (GMA-412 / arm rule): `Tier:`, `Models:`, `Linear:` (`https://linear.app/...` or `N/A` only), `Summary:`, `Gates:`, then **pstack (Poteto) principles cited**, then verification evidence/checklist.

Use `Linear: N/A` when there is no tracking issue. Tier meanings: see **Tier scale** in `docs/shared/repo-standards-practice.md` (T0 small/docs/check-only through T3 infra/migration/new service).

**Linear line:** Must be an `https://linear.app/...` issue URL, or `N/A`. Never use a Cursor store path, box path, or sketch link. Do not use angle-bracket placeholders in committed examples.

For hub Markdown-only PRs, use `Gates: N/A (hub Markdown)`.

The **`Gates:`** section reports the real dryer, crapper, and mutator results (exits, findings on changed scope, debt counts, mutator timeout, and the CI `outcome=` line).

Workflow skills point here: `skills/technical-writing/SKILL.md`, `skills/lfg/SKILL.md`, `skills/multi-harness-coordination/SKILL.md`, `skills/split-branch-for-pr/SKILL.md`, `skills/adversarial-coordination-workflow/SKILL.md`, `skills/create-repo-standards/SKILL.md`, `skills/maintain-repo-standards/SKILL.md`.

## Prerequisites (repo / CI)

Before ub-gates can run in CI or locally:

| Prerequisite | Why |
| --- | --- |
| **Coverage in CI** | **crapper** and **mutator** need an LCOV or coverage profile (e.g. `pytest --cov` / `pytest-cov`, JaCoCo, `go test -coverprofile`, per `skills/ub-mode/references/gates-by-language.md`) |
| **Changed-line scope** | Upstream `--changed` uses **`git status`** (uncommitted adds/edits), not the PR diff. CI and the container use the merge-base file list, then changed functions (crapper) and changed lines (dryer, mutator). |
| **crapper, dryer, mutator** | CI installs the pinned tools inside the job. Locally, use the container below. Do not install them on the host for this recipe. |

Hub CI: workflow job **`ub-gates`** runs the composite action, which calls `bash scripts/run_ub_gates_ci.sh` with advisory **0**, on every **`push`** and **`pull_request`**. Checkout uses **`fetch-depth: 0`**. The script also fetches **`UB_GATES_BASE_REF`** with no depth limit and unshallows a shallow clone. It writes `.metrics/ub-gates-outcome.txt` and a GitHub step summary (plus **`::warning`** when tools are missing). **`skipped_tools_missing`** exits **1** in this blocking default (`gates_ran=0`, not a pass).

The **`verify-hub`** job uses default checkout (**depth 1**) and runs `verify-hub-ci` (doctor, drives, optional local `run_ub_gates_report.sh`). That report wrapper stays advisory. **Reviewers confirm ub-mode gates from the `ub-gates` job at head SHA**, not from `verify-hub`.

## Local recipe (no host installs)

Run the gates in a throwaway `--rm` container. Usage line from `scripts/ub_gates_container.sh --help`:

```
Usage: bash scripts/ub_gates_container.sh [--help] [--worktree PATH] [--main-git PATH] [--metrics-dir PATH]
```

The launcher runs `docker run --rm` on `rust:1.83`, installs the pinned crapper, dryer, and mutator inside the container, mounts the worktree read-only, and sets `UB_GATES_ADVISORY=0`. The only host write is a copy of `.metrics` in a temp directory. The script prints that directory on stdout.

## Pre-PR dev flow (implementer)

Before opening a PR (`plan-code-review-workflow` Phase 2.75, `lfg` steps 3.4–3.5), the implementer runs dryer, crapper, and mutator on the new code and acts on the results.

1. Tests are green for the scoped change.
2. Run `bash scripts/ub_gates_container.sh` from the worktree. Thresholds inside the CI script: crapper `--threshold 10`, dryer `--threshold 0.8` after `rm -f .metrics/dry.edn`. Mutator receives the changed lines.
3. Fix blocking findings on changed functions (crapper) and changed lines (dryer, mutator) before the PR. Debt in untouched old functions does not block.
4. A mutator skip is `skipped_mutator` and fails the blocking job. A timeout is reported, leads the summary, and does not block.
5. There is no waiver. Blocking findings on changed code are fixed, or escalated to the CoS.
6. Record the real results on the PR **`Gates:`** line (exits, finding counts, debt counts, timeout, `.metrics/ub-gates-outcome.txt` / CI `outcome=`).

## Reviewer (CI confirmation only)

In `expert-pr-review` Step 3.5 and `plan-code-review-workflow` Phase 3:

1. At the PR **head SHA**, read CI check **`ub-gates`** and the job log / step summary / `.metrics/ub-gates-outcome.txt` (`outcome=...`). **Do not** re-run crapper, dryer, or mutator locally.
2. **`ran_clean`**: tools ran; no blocking findings on changed scope.
3. **`ran_with_findings`**: blocking findings on changed code. The default job fails. Hand back. The implementer fixes them or escalates to the CoS. Not a review round.
4. **`tool_error`**: tool failure — hand back; not a review round.
5. **`skipped_no_scope`**: OK when the PR has no gate-relevant sources.
6. **`skipped_tools_missing`** and **`skipped_mutator`**: the blocking job fails. Hand back. Not a review round.
7. A mutator timeout is named on the first summary line and does not by itself fail the job.
8. Debt counts for untouched old functions do not fail the job.

## How tools pair with principles

| Tool | Enforces (principle names) |
| --- | --- |
| **write-tests** + your test runner | test-behavior-not-implementation, prove-it-works |
| **crapper** | fix-root-causes on complexity risk; sequence-verifiable-units per function |
| **dryer** | subtract-before-you-add on duplicate structure |
| **mutator** | test-behavior-not-implementation; prove-it-works on surviving mutants |
| **uml-viewer** | Optional picture of `.metrics/` for humans |

Definitions of principle names live only in `skills/pstack-principles/SKILL.md`.

## Evidence to report

1. Test command and exit code.
2. **crapper**: findings on changed functions (CRAP > 10) and debt in untouched functions (`.metrics/crap.edn`).
3. **dryer**: delete `.metrics/dry.edn` before the run (GMA-411); findings are candidates with `:score` ≥ 0.8 that touch changed lines.
4. **mutator**: exit `0` / `2` / `3` (survivors), timeout if the 20-minute budget ends, and `.metrics/mutate/`.
5. **CI outcome** line from `ub-gates` (`outcome=`, `gate_miss=`, `mutator_timeout=`).

Put that evidence on the PR **`Gates:`** line. **`skipped_tools_missing`** and **`skipped_mutator`** are failures in blocking mode. Call them out. Do not describe them as a clean pass.
