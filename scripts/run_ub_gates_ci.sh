#!/usr/bin/env bash
# ub-mode gates for CI (GMA-410 advisory, GMA-499 blocking).
# Uses the merge-base file list. Upstream `--changed` reads git status only.
# UB_GATES_ADVISORY=1 (default) reports and exits 0.
# UB_GATES_ADVISORY=0 fails the job on skip (except skipped_no_scope), tool_error, and findings in changed scope.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCOPE_PY="${SCRIPT_DIR}/ub_changed_scope.py"
ADVISORY="${UB_GATES_ADVISORY:-1}"
BASE_REF="${UB_GATES_BASE_REF:-origin/main}"
OUTCOME_FILE="${UB_GATES_OUTCOME_FILE:-.metrics/ub-gates-outcome.txt}"
DRYER_THRESHOLD="${UB_GATES_DRYER_THRESHOLD:-0.8}"
MUTATOR_BUDGET="${UB_GATES_MUTATOR_BUDGET_SECS:-1200}"

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
    if [[ -n "${CRAPPER_FINDINGS:-}" ]]; then printf 'crapper_findings=%s\n' "${CRAPPER_FINDINGS}"; fi
    if [[ -n "${CRAPPER_DEBT:-}" ]]; then printf 'crapper_debt=%s\n' "${CRAPPER_DEBT}"; fi
    if [[ -n "${DRYER_RC:-}" ]]; then printf 'dryer_exit=%s\n' "${DRYER_RC}"; fi
    if [[ -n "${DRYER_HIGH:-}" ]]; then printf 'dryer_candidates_ge_threshold=%s\n' "${DRYER_HIGH}"; fi
    if [[ -n "${DRYER_FINDINGS:-}" ]]; then printf 'dryer_findings=%s\n' "${DRYER_FINDINGS}"; fi
    if [[ -n "${DRYER_DEBT:-}" ]]; then printf 'dryer_debt=%s\n' "${DRYER_DEBT}"; fi
    if [[ -n "${MUTATOR_RC:-}" ]]; then printf 'mutator_exit=%s\n' "${MUTATOR_RC}"; fi
    if [[ -n "${MUTATOR_SKIPPED:-}" ]]; then printf 'mutator_skipped=%s\n' "${MUTATOR_SKIPPED}"; fi
    if [[ -n "${MUTATOR_TIMEOUT:-}" ]]; then printf 'mutator_timeout=%s\n' "${MUTATOR_TIMEOUT}"; fi
    if [[ -n "${TOOL_ERROR:-}" ]]; then printf 'tool_error=%s\n' "${TOOL_ERROR}"; fi
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
    if [[ "${OUTCOME:-}" == "skipped_tools_missing" && "${ADVISORY}" == "1" ]]; then
      echo "> **Neutral skip (not a gate pass):** \`skipped_tools_missing\` — crapper, dryer, and mutator were not on PATH. Install tools in CI is a follow-up ticket."
      echo ""
    fi
    if [[ "${OUTCOME:-}" == "skipped_tools_missing" && "${ADVISORY}" != "1" ]]; then
      echo "> **Blocking skip:** \`skipped_tools_missing\` — crapper, dryer, and mutator were not on PATH. The job fails."
      echo ""
    fi
    if [[ "${OUTCOME:-}" == "tool_error" && "${ADVISORY}" == "1" ]]; then
      echo "> **Advisory tool error (not clean, not a quality finding):** \`tool_error\` — crapper/dryer/mutator failed to run correctly. Review exit codes and metrics files; hand back to implementer."
      echo ""
    fi
    if [[ "${OUTCOME:-}" == "tool_error" && "${ADVISORY}" != "1" ]]; then
      echo "> **Blocking tool error:** \`tool_error\` — crapper/dryer/mutator failed to run correctly. The job fails."
      echo ""
    fi
    echo "| Field | Value |"
    echo "| --- | --- |"
    echo "| outcome | ${OUTCOME:-unknown} |"
    echo "| gates_ran | ${GATES_RAN:-0} |"
    echo "| gate_miss | ${GATE_MISS:-0} |"
    echo "| scope_files | ${SCOPE_COUNT:-0} |"
    if [[ -n "${CRAPPER_RC:-}" ]]; then echo "| crapper_exit | ${CRAPPER_RC} |"; fi
    if [[ -n "${CRAPPER_FINDINGS:-}" ]]; then echo "| crapper_findings | ${CRAPPER_FINDINGS} |"; fi
    if [[ -n "${CRAPPER_DEBT:-}" ]]; then echo "| crapper_debt | ${CRAPPER_DEBT} |"; fi
    if [[ -n "${DRYER_RC:-}" ]]; then echo "| dryer_exit | ${DRYER_RC} |"; fi
    if [[ -n "${DRYER_HIGH:-}" ]]; then echo "| dryer_candidates_ge_${DRYER_THRESHOLD} | ${DRYER_HIGH} |"; fi
    if [[ -n "${DRYER_FINDINGS:-}" ]]; then echo "| dryer_findings | ${DRYER_FINDINGS} |"; fi
    if [[ -n "${DRYER_DEBT:-}" ]]; then echo "| dryer_debt | ${DRYER_DEBT} |"; fi
    if [[ -n "${MUTATOR_RC:-}" ]]; then echo "| mutator_exit | ${MUTATOR_RC} |"; fi
    if [[ -n "${MUTATOR_TIMEOUT:-}" ]]; then echo "| mutator_timeout | ${MUTATOR_TIMEOUT} |"; fi
    echo ""
    echo "Outcome file: \`${OUTCOME_FILE}\`"
  } >>"${GITHUB_STEP_SUMMARY}"
}

exit_for_outcome() {
  local code=0
  case "${OUTCOME}" in
    skipped_no_scope|ran_clean)
      code=0
      ;;
    ran_with_findings)
      if [[ "${ADVISORY}" == "1" ]]; then
        log "ub-gates: advisory mode — findings reported; job succeeds"
        code=0
      else
        log "ub-gates: blocking mode — failing job on gate findings"
        code=1
      fi
      ;;
    tool_error)
      if [[ "${ADVISORY}" == "1" ]]; then
        log "ub-gates: advisory mode — tool_error reported; job succeeds"
        code=0
      else
        log "ub-gates: blocking mode — failing job on tool_error"
        code=1
      fi
      ;;
    skipped_tools_missing|skipped_no_base_ref|skipped_no_merge_base|skipped_not_git)
      if [[ "${ADVISORY}" == "1" ]]; then
        code=0
      else
        code=1
      fi
      ;;
    *)
      code=1
      ;;
  esac
  write_outcome "${OUTCOME}"
  append_step_summary
  exit "${code}"
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

gate_bin() {
  command -v "$1" >/dev/null 2>&1 && echo "$1" && return 0
  if [[ -x "./$1" ]]; then
    echo "./$1"
    return 0
  fi
  return 1
}

apply_scope_filter() {
  local cmd="$1"
  local edn="$2"
  local thresh="$3"
  local out rc counts findings debt
  out="$(mktemp)"
  set +e
  python3 "${SCOPE_PY}" "${cmd}" --base "${MERGE_BASE}" --edn "${edn}" --threshold "${thresh}" >"${out}"
  rc=$?
  set -e
  if [[ "${rc}" -ne 0 ]]; then
    cat "${out}" >&2 || true
    rm -f "${out}"
    return "${rc}"
  fi
  counts="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1], encoding="utf-8")); print(len(d["findings"])); print(len(d["debt"]))' "${out}")"
  rm -f "${out}"
  findings="${counts%%$'\n'*}"
  debt="${counts##*$'\n'}"
  if [[ "${cmd}" == "crap" ]]; then
    CRAPPER_FINDINGS="${findings}"
    CRAPPER_DEBT="${debt}"
  else
    DRYER_FINDINGS="${findings}"
    DRYER_DEBT="${debt}"
  fi
  return 0
}

run_crapper() {
  local args=(--threshold 10)
  if [[ ${#COVERAGE_PREFIX[@]} -gt 0 ]]; then
    args+=("${COVERAGE_PREFIX[@]}")
  fi
  args+=("${SCOPE_FILES[@]}")
  set +e
  "${CRAPPER}" "${args[@]}"
  CRAPPER_RC=$?
  set -e
}

run_dryer() {
  rm -f .metrics/dry.edn
  set +e
  "${DRYER}" --threshold "${DRYER_THRESHOLD}" "${SCOPE_FILES[@]}"
  DRYER_RC=$?
  set -e
}

note_mutator_rc() {
  local rc="$1"
  if [[ "${rc}" -eq 1 || "${rc}" -eq 2 ]]; then
    MUTATOR_RC="${rc}"
    TOOL_ERROR=1
    return 1
  fi
  if [[ "${rc}" -eq 3 ]]; then
    MUTATOR_RC=3
    return 0
  fi
  if [[ "${rc}" -ne 0 ]]; then
    MUTATOR_RC="${rc}"
    TOOL_ERROR=1
    return 1
  fi
  return 0
}

mark_mutator_timeout() {
  MUTATOR_TIMEOUT=1
  emit_warning "mutator budget exhausted; remaining files skipped"
}

run_mutator_blocking() {
  local deadline file lines left rc args
  MUTATOR_RC=0
  MUTATOR_TIMEOUT=0
  deadline=$((SECONDS + MUTATOR_BUDGET))
  for file in "${SCOPE_FILES[@]}"; do
    if (( SECONDS >= deadline )); then
      mark_mutator_timeout
      return 0
    fi
    lines="$(python3 "${SCOPE_PY}" lines --base "${MERGE_BASE}" --file "${file}")"
    if [[ -z "${lines}" ]]; then
      continue
    fi
    left=$((deadline - SECONDS))
    if (( left < 1 )); then
      mark_mutator_timeout
      return 0
    fi
    args=(--lines "${lines}")
    if [[ ${#COVERAGE_PREFIX[@]} -gt 0 ]]; then
      args+=("${COVERAGE_PREFIX[@]}")
    fi
    args+=("${file}")
    set +e
    timeout "${left}" "${MUTATOR}" "${args[@]}"
    rc=$?
    set -e
    if [[ "${rc}" -eq 124 || "${rc}" -eq 137 ]]; then
      mark_mutator_timeout
      return 0
    fi
    note_mutator_rc "${rc}" || return 0
  done
}

run_mutator_advisory() {
  local args=()
  if [[ ${#COVERAGE_PREFIX[@]} -gt 0 ]]; then
    args+=("${COVERAGE_PREFIX[@]}")
  fi
  args+=("${SCOPE_FILES[@]}")
  set +e
  "${MUTATOR}" "${args[@]}"
  MUTATOR_RC=$?
  set -e
}

classify_crapper() {
  CRAPPER_FINDINGS=0
  CRAPPER_DEBT=0
  if [[ "${ADVISORY}" == "1" ]]; then
    if [[ "${CRAPPER_RC}" -ne 0 ]]; then
      CRAPPER_FINDINGS=1
    fi
    return 0
  fi
  if [[ -f .metrics/crap.edn ]]; then
    apply_scope_filter crap .metrics/crap.edn 10 || return 1
  elif [[ "${CRAPPER_RC}" -ne 0 ]]; then
    return 1
  fi
  if [[ "${CRAPPER_RC}" -ne 0 && "${CRAPPER_RC}" -ne 2 ]]; then
    return 1
  fi
  return 0
}

classify_dryer() {
  DRYER_FINDINGS=0
  DRYER_DEBT=0
  DRYER_HIGH=0
  if [[ "${DRYER_RC}" -eq 1 || "${DRYER_RC}" -eq 2 ]]; then
    return 1
  fi
  if [[ "${DRYER_RC}" -eq 0 && ! -f .metrics/dry.edn ]]; then
    return 1
  fi
  if [[ "${ADVISORY}" == "1" ]]; then
    if [[ -f .metrics/dry.edn ]]; then
      DRYER_HIGH="$(count_dryer_high_candidates .metrics/dry.edn || echo 0)"
    fi
    DRYER_FINDINGS="${DRYER_HIGH}"
    return 0
  fi
  if [[ -f .metrics/dry.edn ]]; then
    apply_scope_filter dry .metrics/dry.edn "${DRYER_THRESHOLD}" || return 1
    DRYER_HIGH="${DRYER_FINDINGS}"
  fi
  return 0
}

GATE_MISS=0
GATES_RAN=0
OUTCOME=""
TOOL_ERROR=0
COVERAGE_PREFIX=()
FINDING=0

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  OUTCOME="skipped_not_git"
  GATE_MISS=1
  exit_for_outcome
fi

if ! git rev-parse --verify "${BASE_REF}^{commit}" >/dev/null 2>&1; then
  git fetch origin main --depth=1 2>/dev/null || true
fi

if ! git rev-parse --verify "${BASE_REF}^{commit}" >/dev/null 2>&1; then
  OUTCOME="skipped_no_base_ref"
  GATE_MISS=1
  exit_for_outcome
fi

MERGE_BASE="$(git merge-base HEAD "${BASE_REF}" 2>/dev/null || echo "")"
if [[ -z "${MERGE_BASE}" ]]; then
  OUTCOME="skipped_no_merge_base"
  GATE_MISS=1
  exit_for_outcome
fi

collect_scope_files "${MERGE_BASE}"
if [[ "${SCOPE_COUNT}" -eq 0 ]]; then
  OUTCOME="skipped_no_scope"
  GATE_MISS=0
  GATES_RAN=0
  log "ub-gates: no gate-relevant files in ${MERGE_BASE}...HEAD — skipped (OK)"
  exit_for_outcome
fi

SKIP_MUTATOR="${UB_GATES_SKIP_MUTATOR:-0}"
if [[ "${SKIP_MUTATOR}" != "1" && -n "${CURSOR_AGENT:-}" && -z "${GITHUB_ACTIONS:-}" ]]; then
  SKIP_MUTATOR=1
  log "ub-gates: skipping mutator (cloud agent harness; run on laptop or CI)"
fi

CRAPPER="$(gate_bin crapper || true)"
DRYER="$(gate_bin dryer || true)"
MUTATOR=""
if [[ "${SKIP_MUTATOR}" != "1" ]]; then
  MUTATOR="$(gate_bin mutator || true)"
fi

need_mutator=1
if [[ "${SKIP_MUTATOR}" == "1" ]]; then
  need_mutator=0
fi

if [[ -z "${CRAPPER}" || -z "${DRYER}" || ( "${need_mutator}" -eq 1 && -z "${MUTATOR}" ) ]]; then
  OUTCOME="skipped_tools_missing"
  GATE_MISS=1
  GATES_RAN=0
  emit_warning "skipped_tools_missing — crapper, dryer, and mutator not on PATH (${SCOPE_COUNT} gate-relevant file(s) in scope). This is not a gate pass; install tools in CI is a follow-up ticket."
  log "ub-gates: scope had ${SCOPE_COUNT} file(s); see skills/ub-mode/references/gates-by-language.md"
  exit_for_outcome
fi

if [[ -n "${UB_GATES_COVERAGE_CMD:-}" ]]; then
  set +e
  bash -c "${UB_GATES_COVERAGE_CMD}"
  cov_rc=$?
  set -e
  if [[ "${cov_rc}" -ne 0 ]]; then
    OUTCOME="tool_error"
    GATE_MISS=1
    TOOL_ERROR=1
    GATES_RAN=0
    emit_warning "tool_error — UB_GATES_COVERAGE_CMD failed"
    exit_for_outcome
  fi
  COVERAGE_PREFIX=(--use-existing-coverage)
fi

log "ub-gates: running on ${SCOPE_COUNT} file(s) from ${MERGE_BASE}...HEAD (advisory=${ADVISORY})"
log "ub-gates: ${SCOPE_FILES[*]}"

run_crapper
run_dryer
MUTATOR_SKIPPED=0
MUTATOR_TIMEOUT=0
if [[ "${SKIP_MUTATOR}" == "1" ]]; then
  MUTATOR_SKIPPED=1
  MUTATOR_RC=""
else
  if [[ "${ADVISORY}" == "1" ]]; then
    run_mutator_advisory
  else
    run_mutator_blocking
  fi
fi

if [[ -n "${MUTATOR_RC}" ]]; then
  log "ub-gates: crapper exit ${CRAPPER_RC}; dryer exit ${DRYER_RC}; mutator exit ${MUTATOR_RC}"
else
  log "ub-gates: crapper exit ${CRAPPER_RC}; dryer exit ${DRYER_RC}; mutator skipped"
fi

if ! classify_crapper; then
  TOOL_ERROR=1
fi
if ! classify_dryer; then
  TOOL_ERROR=1
fi
if [[ "${ADVISORY}" == "1" && -n "${MUTATOR_RC}" && "${MUTATOR_RC}" -eq 2 ]]; then
  TOOL_ERROR=1
fi

if [[ "${TOOL_ERROR}" -eq 0 ]]; then
  if [[ "${CRAPPER_FINDINGS}" -gt 0 ]]; then FINDING=1; fi
  if [[ "${DRYER_FINDINGS}" -gt 0 ]]; then FINDING=1; fi
  if [[ -n "${MUTATOR_RC}" && "${MUTATOR_RC}" -eq 3 ]]; then FINDING=1; fi
fi

GATES_RAN=1
if [[ "${TOOL_ERROR}" -eq 1 ]]; then
  OUTCOME="tool_error"
  GATE_MISS=1
  emit_warning "tool_error — dryer/mutator tool failure or missing .metrics/dry.edn after dryer; not ran_clean."
elif [[ "${FINDING}" -eq 1 ]]; then
  OUTCOME="ran_with_findings"
else
  OUTCOME="ran_clean"
fi

exit_for_outcome
