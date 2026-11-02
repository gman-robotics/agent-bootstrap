# Ub-gates advisory bundle (verify-hub-ci)

After INDEX and live-check drives, `bin/verify-hub-ci` runs coverage-backed unit tests and **`scripts/run_ub_gates_report.sh`** (advisory only). This mirrors the template in `skills/create-verification-skill/references/verify-ci-ub-gates.sh` and feeds unclebob gates when `crapper`, `dryer`, and `mutator` are on PATH.

## Sub-features

- `coverage-unittest` — `coverage run -m unittest discover -s tests` when `coverage` is installed; plain unittest otherwise.
- `advisory-report` — `UB_GATES_ADVISORY=1` via `run_ub_gates_report.sh`; script always exits `0` so the verify bundle does not fail on gate debt.
- `outcome-artifact` — copies `.metrics/ub-gates-outcome.txt` into `$VERIFY_HUB_ARTIFACTS_DIR` when present.

## How to get to it (user POV)

- From repo root after dev deps: `bash .cursor/skills/verify-hub/bin/verify-hub-ci` (full bundle), or run `bash scripts/run_ub_gates_report.sh` alone after coverage tests when debugging gates.

## Driving it with verify-hub

Preconditions:

- `verify-hub doctor` OK.
- Git checkout with a merge base to `origin/main` (or set `UB_GATES_BASE_REF`) when you expect a non-empty scope.
- `$VERIFY_HUB_ARTIFACTS_DIR` created.

- **Full bundle.** Run `bash .cursor/skills/verify-hub/bin/verify-hub-ci`. Require final line `verify-hub-ci: OK (artifacts=<dir>)`. Inspect `${VERIFY_HUB_ARTIFACTS_DIR}/ub-gates-outcome.txt` when gates ran or skipped.
- **Outcome names.** Expect hub keys from `run_ub_gates_ci.sh`: `outcome=ran_clean`, `ran_with_findings`, `skipped_no_scope`, `skipped_tools_missing`, `skipped_mutator`, `skipped_no_base_ref`, `skipped_not_git`, or `tool_error`. A missing merge-base (empty `git merge-base`) is `tool_error`, not a separate `skipped_no_merge_base` outcome file key (`skipped_no_merge_base` appears only in the exit-case table for blocking mode).
- **Proof.** `ub-gates-outcome.txt` plus `coverage-report.txt` (when coverage ran) under the artifacts dir.

## Gotchas

- Scope file list comes from `git diff --name-only --diff-filter=ACMRT <merge-base> HEAD` in `collect_scope_files` inside `scripts/run_ub_gates_ci.sh`, then extension and test-path filters. **`scripts/ub_changed_scope.py`** applies the `lines` / `crap` / `dry` finding filter on gate metrics — not the merge-base file list. This is not git status `--changed`. On a branch with no gate-relevant files vs the merge base, `outcome=skipped_no_scope` is normal.
- When `CURSOR_AGENT` is set and `GITHUB_ACTIONS` is unset, `run_ub_gates_report.sh` exports `UB_GATES_SKIP_MUTATOR=1` (same skip in `run_ub_gates_ci.sh`). That does **not** always write `skipped_mutator`. Empty gate-relevant scope → `skipped_no_scope` (returns before mutator logic). Missing `crapper` or `dryer` → `skipped_tools_missing` (with mutator skip, missing `mutator` alone does not). Gate findings → `ran_with_findings`. Tool failure → `tool_error`. **`skipped_mutator`** is only after crapper and dryer run with no findings and no tool error, but mutator was skipped. Advisory mode still exits `0` for all of these (`run_ub_gates_report.sh` always ends with `exit 0`).
- Blocking CI uses the same scripts with `UB_GATES_ADVISORY=0` (see [Blocking ub-gates CI job](./ub-gates-blocking-ci.md)); do not confuse advisory verify output with a failing PR check.
