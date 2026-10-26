#!/usr/bin/env bash
# Report-only ub gates for verify-<app>-ci scripts (GMA-410). Never fails the verify bundle
# on gate findings; delegates to run_ub_gates_ci.sh with advisory mode.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export UB_GATES_ADVISORY=1
if [[ -n "${CURSOR_AGENT:-}" && -z "${GITHUB_ACTIONS:-}" ]]; then
  export UB_GATES_SKIP_MUTATOR=1
fi
exec bash "${SCRIPT_DIR}/run_ub_gates_ci.sh"
