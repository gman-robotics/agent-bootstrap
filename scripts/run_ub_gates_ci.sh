#!/usr/bin/env bash
# Advisory ub-mode gates for CI (GMA-410). Uses merge-base file list — not `--changed`
# (upstream `--changed` reads git status / uncommitted files only).
set -euo pipefail

ADVISORY="${UB_GATES_ADVISORY:-1}"
BASE_REF="${UB_GATES_BASE_REF:-origin/main}"
OUTCOME_FILE="${UB_GATES_OUTCOME_FILE:-.metrics/ub-gates-outcome.txt}"
DRYER_THRESHOLD="${UB_GATES_DRYER_THRESHOLD:-0.8}"

log() { printf '%s\n' "$*"; }

write_outcome() {
  mkdir -p "$(dirname "${OUTCOME_FILE}")"
  {
    printf 'outcome=%s\n' "$1"
    printf 'gate_miss=%s\n' "${GATE_MISS:-0}"
    printf 'gates_ran=%s\n' "${GATES_RAN:-0}"
    printf 'advisory=%s\n' "${ADVISORY}"
    if [[ -n "${SCOPE_COUNT:-}" ]]; then printf 'scope_files=%s\n' "${SCOPE_COUNT}"; fi
    if [[ -n "${CRAPPER_RC:-}" ]]; then printf 'crapper_exit=%s\n' "${CRAPPER_RC}"; fi
    if [[ -n "${DRYER_RC:-}" ]]; then printf 'dryer_exit=%s\n' "${DRYER_RC}"; fi
    if [[ -n "${DRYER_HIGH:-}" ]]; then printf 'dryer_candidates_ge_threshold=%s\n' "${DRYER_HIGH}"; fi
    if [[ -n "${MUTATOR_RC:-}" ]]; then printf 'mutator_exit=%s\n' "${MUTATOR_RC}"; fi
  } >"${OUTCOME_FILE}"
}

emit_warning() {
  local msg="$1"
  log "ub-gates: WARNING: ${msg}"
  if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
    local safe="${msg//'%'/'%25'}"
    safe="${safe//$'\n'/'%0A'}"
    safe="${safe//$'\r'/'%0D'}"
    echo "::warning title=ub-gates::${safe}"
  fi
}

append_step_summary() {
  [[ -n "${GITHUB_STEP_SUMMARY:-}" ]] || return 0
  mkdir -p "$(dirname "${GITHUB_STEP_SUMMARY}")" 2>/dev/null || return 0
  {
    echo "## ub-gates"
    echo ""
    if [[ "${OUTCOME:-}" == "skipped_tools_missing" ]]; then
      echo "> **Neutral skip (not a gate pass):** \`skipped_tools_missing\` — crapper, dryer, and mutator were not on PATH. Install tools in CI is a follow-up ticket."
      echo ""
    fi
    echo "| Field | Value |"
    echo "| --- | --- |"
    echo "| outcome | ${OUTCOME:-unknown} |"
    echo "| gates_ran | ${GATES_RAN:-0} |"
    echo "| gate_miss | ${GATE_MISS:-0} |"
    echo "| scope_files | ${SCOPE_COUNT:-0} |"
    if [[ -n "${CRAPPER_RC:-}" ]]; then echo "| crapper_exit | ${CRAPPER_RC} |"; fi
    if [[ -n "${DRYER_RC:-}" ]]; then echo "| dryer_exit | ${DRYER_RC} |"; fi
    if [[ -n "${DRYER_HIGH:-}" ]]; then echo "| dryer_candidates_ge_${DRYER_THRESHOLD} | ${DRYER_HIGH} |"; fi
    if [[ -n "${MUTATOR_RC:-}" ]]; then echo "| mutator_exit | ${MUTATOR_RC} |"; fi
    echo ""
    echo "Outcome file: \`${OUTCOME_FILE}\`"
  } >>"${GITHUB_STEP_SUMMARY}"
}

gate_relevant_file() {
  case "$1" in
    *.py|*.pyi|*.ts|*.tsx|*.mts|*.cts|*.js|*.jsx|*.mjs|*.cjs|*.go|*.rs|*.java|*.clj|*.cljs|*.cljc) return 0 ;;
    *) return 1 ;;
  esac
}

collect_scope_files() {
  local merge_base="$1"
  local f
  SCOPE_FILES=()
  while IFS= read -r f; do
    [[ -z "${f}" ]] && continue
    [[ -f "${f}" ]] || continue
    gate_relevant_file "${f}" || continue
    SCOPE_FILES+=("${f}")
  done < <(git diff --name-only --diff-filter=ACMRT "${merge_base}" HEAD 2>/dev/null || true)
  SCOPE_COUNT="${#SCOPE_FILES[@]}"
}

count_dryer_high_candidates() {
  local path="${1:-.metrics/dry.edn}"
  [[ -f "${path}" ]] || return 1
  python3 - "${path}" "${DRYER_THRESHOLD}" <<'PY'
import re, sys
path, thresh = sys.argv[1], float(sys.argv[2])
text = open(path, encoding="utf-8").read()
scores = [float(m) for m in re.findall(r":score\s+([\d.]+)", text)]
high = sum(1 for s in scores if s >= thresh)
print(high)
PY
}

GATE_MISS=0
GATES_RAN=0
OUTCOME=""

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  OUTCOME="skipped_not_git"
  GATE_MISS=1
  write_outcome "${OUTCOME}"
  append_step_summary
  exit 1
fi

if ! git rev-parse --verify "${BASE_REF}^{commit}" >/dev/null 2>&1; then
  git fetch origin main --depth=1 2>/dev/null || true
fi

if ! git rev-parse --verify "${BASE_REF}^{commit}" >/dev/null 2>&1; then
  OUTCOME="skipped_no_base_ref"
  GATE_MISS=1
  write_outcome "${OUTCOME}"
  append_step_summary
  exit 1
fi

MERGE_BASE="$(git merge-base HEAD "${BASE_REF}" 2>/dev/null || echo "")"
if [[ -z "${MERGE_BASE}" ]]; then
  OUTCOME="skipped_no_merge_base"
  GATE_MISS=1
  write_outcome "${OUTCOME}"
  append_step_summary
  exit 1
fi

collect_scope_files "${MERGE_BASE}"
if [[ "${SCOPE_COUNT}" -eq 0 ]]; then
  OUTCOME="skipped_no_scope"
  GATE_MISS=0
  GATES_RAN=0
  write_outcome "${OUTCOME}"
  append_step_summary
  log "ub-gates: no gate-relevant files in ${MERGE_BASE}...HEAD — skipped (OK)"
  exit 0
fi

gate_bin() {
  command -v "$1" >/dev/null 2>&1 && echo "$1" && return 0
  if [[ -x "./$1" ]]; then
    echo "./$1"
    return 0
  fi
  return 1
}

CRAPPER="$(gate_bin crapper || true)"
DRYER="$(gate_bin dryer || true)"
MUTATOR="$(gate_bin mutator || true)"

if [[ -z "${CRAPPER}" || -z "${DRYER}" || -z "${MUTATOR}" ]]; then
  OUTCOME="skipped_tools_missing"
  GATE_MISS=1
  GATES_RAN=0
  write_outcome "${OUTCOME}"
  append_step_summary
  emit_warning "skipped_tools_missing — crapper, dryer, and mutator not on PATH (${SCOPE_COUNT} gate-relevant file(s) in scope). This is not a gate pass; install tools in CI is a follow-up ticket."
  log "ub-gates: scope had ${SCOPE_COUNT} file(s); see skills/ub-mode/references/gates-by-language.md"
  exit 0
fi

log "ub-gates: running on ${SCOPE_COUNT} file(s) from ${MERGE_BASE}...HEAD (advisory=${ADVISORY})"
log "ub-gates: ${SCOPE_FILES[*]}"

set +e
"${CRAPPER}" --threshold 10 "${SCOPE_FILES[@]}"
CRAPPER_RC=$?
rm -f .metrics/dry.edn
"${DRYER}" --threshold "${DRYER_THRESHOLD}" "${SCOPE_FILES[@]}"
DRYER_RC=$?
DRYER_HIGH=0
if [[ -f .metrics/dry.edn ]]; then
  DRYER_HIGH="$(count_dryer_high_candidates .metrics/dry.edn || echo 0)"
else
  DRYER_HIGH=0
fi
"${MUTATOR}" "${SCOPE_FILES[@]}"
MUTATOR_RC=$?
set -e

log "ub-gates: crapper exit ${CRAPPER_RC}; dryer exit ${DRYER_RC}; dryer candidates >= ${DRYER_THRESHOLD}: ${DRYER_HIGH}; mutator exit ${MUTATOR_RC}"

FINDING=0
if [[ "${CRAPPER_RC}" -ne 0 ]]; then FINDING=1; fi
if [[ "${DRYER_HIGH}" -gt 0 ]]; then FINDING=1; fi
if [[ "${MUTATOR_RC}" -eq 3 ]]; then FINDING=1; fi

if [[ "${FINDING}" -eq 1 ]]; then
  OUTCOME="ran_with_findings"
else
  OUTCOME="ran_clean"
fi
GATES_RAN=1

write_outcome "${OUTCOME}"
append_step_summary

if [[ "${FINDING}" -eq 1 && "${ADVISORY}" != "1" ]]; then
  log "ub-gates: blocking mode — failing job on gate findings"
  exit 1
fi

if [[ "${FINDING}" -eq 1 ]]; then
  log "ub-gates: advisory mode — findings reported; job succeeds"
fi

exit 0
