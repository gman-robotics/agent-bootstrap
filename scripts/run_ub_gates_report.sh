#!/usr/bin/env bash
# Report-only ub gates for verify-<app>-ci scripts (GMA-410). Never fails the verify bundle
# on gate findings or on run_ub_gates_ci.sh infrastructure exits; delegates to run_ub_gates_ci.sh
# with advisory mode. The ub-gates CI job calls run_ub_gates_ci.sh directly (may exit 1).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export UB_GATES_ADVISORY=1
if [[ -n "${CURSOR_AGENT:-}" && -z "${GITHUB_ACTIONS:-}" ]]; then
  export UB_GATES_SKIP_MUTATOR=1
fi

OUTCOME_FILE="${UB_GATES_OUTCOME_FILE:-.metrics/ub-gates-outcome.txt}"

set +e
bash "${SCRIPT_DIR}/run_ub_gates_ci.sh"
_ci_rc=$?
set -e

if [[ ! -f "${OUTCOME_FILE}" ]]; then
  mkdir -p "$(dirname "${OUTCOME_FILE}")"
  {
    printf 'outcome=skipped_not_git\n'
    printf 'gate_miss=1\n'
    printf 'gates_ran=0\n'
    printf 'advisory=1\n'
  } >"${OUTCOME_FILE}"
fi

exit 0
