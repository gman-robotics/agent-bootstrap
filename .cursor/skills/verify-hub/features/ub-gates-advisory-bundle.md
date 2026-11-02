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

- **Full bundle.** Run `bash .cursor/skills/verify-hub/bin/verify-hub-ci`. Require final line `verify-hub-ci: OK`. Inspect `${VERIFY_HUB_ARTIFACTS_DIR}/ub-gates-outcome.txt` when gates ran or skipped.
- **Outcome names.** Expect hub keys: `outcome=ran_clean`, `ran_with_findings`, `skipped_no_scope`, `skipped_tools_missing`, `skipped_mutator`, or `tool_error` (see `scripts/run_ub_gates_ci.sh` header).
- **Proof.** `ub-gates-outcome.txt` plus `coverage-report.txt` (when coverage ran) under the artifacts dir.

## Gotchas

- Scope uses the **merge-base file list** (`scripts/ub_changed_scope.py`), not git status `--changed`. On a branch with no gate-relevant files vs `origin/main`, `outcome=skipped_no_scope` is normal.
- Cloud agents may set `UB_GATES_SKIP_MUTATOR=1` inside `run_ub_gates_report.sh`; that records `skipped_mutator` in advisory mode and still exits `0`.
- Blocking CI uses the same scripts with `UB_GATES_ADVISORY=0` (see [Blocking ub-gates CI job](./ub-gates-blocking-ci.md)); do not confuse advisory verify output with a failing PR check.
