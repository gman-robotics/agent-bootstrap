#!/usr/bin/env bash
# Template: advisory ub-mode gates for verify-<app>-ci (copy into bin/ and customize).
# Outcomes: ran_clean, ran_with_findings, skipped_no_scope, skipped_tools_missing, tool_error.
# Uses merge-base file list — not upstream --changed (git status only).
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

# --- Coverage (customize for your stack; required for crapper/mutator when tools exist) ---
# Python example below runs when `coverage` is installed. Non-Python repos: replace this
# entire block (see skills/ub-mode/references/gates-by-language.md) — do not ship comments only.
if python3 -m coverage --help >/dev/null 2>&1 && [[ -d tests ]]; then
  python3 -m coverage run -m unittest discover -s tests
  python3 -m coverage report -m || true
else
  echo "verify-ub-gates: PLACEHOLDER — install stack coverage (e.g. pytest-cov, JaCoCo, go -coverprofile) before unclebob gates"
fi

UB_OUT="${VERIFY_UB_OUTCOME_FILE:-.metrics/verify-ub-outcome.txt}"
export UB_GATES_OUTCOME_FILE="${UB_OUT}"
export UB_GATES_ADVISORY=1
export UB_GATES_BASE_REF="${VERIFY_UB_BASE_REF:-origin/main}"

if [[ -f "${REPO_ROOT}/scripts/run_ub_gates_report.sh" ]]; then
  bash "${REPO_ROOT}/scripts/run_ub_gates_report.sh"
else
  mkdir -p "$(dirname "${UB_OUT}")"
  printf 'outcome=skipped_tools_missing\n' >"${UB_OUT}"
  echo "verify-ub-gates: no hub run_ub_gates_report.sh — copy from agent-bootstrap scripts/ (GMA-410)"
fi

echo "verify-ub-gates: wrote ${UB_OUT}"
cat "${UB_OUT}" 2>/dev/null || true
# Report-only: always exit 0 so verify-ci does not fail on advisory gate debt.
exit 0
