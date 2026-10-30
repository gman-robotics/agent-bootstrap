#!/usr/bin/env bash
# ub-mode gates for CI (GMA-410 report path, GMA-499 blocking).
# Uses the merge-base file list. Upstream `--changed` reads git status only.
# UB_GATES_ADVISORY defaults to 0 (blocking). UB_GATES_ADVISORY=1 reports and exits 0.
# run_ub_gates_report.sh sets UB_GATES_ADVISORY=1. A direct call does not.
# Blocking mode fails on skip (except skipped_no_scope), tool_error, findings in
# changed scope, and skipped_mutator.
# UB_GATES_SKIP_MUTATOR=1 and the CURSOR_AGENT auto-skip are skipped_mutator in
# blocking mode (exit 1). They are never ran_clean. Advisory mode may still skip.
# A failed git diff --name-only is tool_error. A missing merge base is tool_error.
# Base-ref fetch honors UB_GATES_BASE_REF, uses no depth limit, and unshallows
# a shallow clone. Mutator budget timeout is non-blocking; the step summary's
# first line states the timeout. .pyi and .d.ts are outside gate scope.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCOPE_PY="${SCRIPT_DIR}/ub_changed_scope.py"
ADVISORY="${UB_GATES_ADVISORY:-0}"
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
    if [[ "${MUTATOR_TIMEOUT:-0}" == "1" ]]; then
      echo "mutator timeout: budget exhausted; non-blocking"
    fi
    echo "## ub-gates"
    echo ""
    if [[ "${OUTCOME:-}" == "skipped_mutator" ]]; then
      echo "> **Blocking skip:** \`skipped_mutator\` — mutator did not run. This is not a clean result."
      echo ""
    fi
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
    skipped_mutator)
      log "ub-gates: blocking mode — mutator skip is not ran_clean"
      code=1
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
    *.pyi|*.d.ts) return 1 ;;
    *.py|*.ts|*.tsx|*.mts|*.cts|*.js|*.jsx|*.mjs|*.cjs|*.go|*.rs|*.java|*.clj|*.cljs|*.cljc) return 0 ;;
    *) return 1 ;;
  esac
}

# test code is the oracle; mutator upstream skips it too.
is_test_path() {
  local path="$1"
  local base="${path##*/}"
  case "/${path}/" in
    */test/*|*/tests/*|*/spec/*|*/specs/*|*/testdata/*|*/__tests__/*|*/fixtures/*) return 0 ;;
  esac
  case "${base}" in
    test_*.py|*_test.py|*_test.go|*_test.rs|*Test.java) return 0 ;;
    *.test.ts|*.test.tsx|*.test.js|*.test.jsx|*.test.mts|*.test.cts|*.test.mjs|*.test.cjs) return 0 ;;
    *.spec.ts|*.spec.tsx|*.spec.js|*.spec.jsx|*.spec.mts|*.spec.cts|*.spec.mjs|*.spec.cjs) return 0 ;;
  esac
  return 1
}

collect_scope_files() {
  local merge_base="$1"
  local f list rc
  SCOPE_FILES=()
  SCOPE_DIFF_FAILED=0
  list="$(mktemp)"
  set +e
  git diff --name-only --diff-filter=ACMRT "${merge_base}" HEAD >"${list}" 2>/dev/null
  rc=$?
  set -e
  if [[ "${rc}" -ne 0 ]]; then
    rm -f "${list}"
    SCOPE_DIFF_FAILED=1
    SCOPE_COUNT=0
    return 0
  fi
  while IFS= read -r f; do
    [[ -z "${f}" ]] && continue
    [[ -f "${f}" ]] || continue
    gate_relevant_file "${f}" || continue
    is_test_path "${f}" && continue
    SCOPE_FILES+=("${f}")
  done <"${list}"
  rm -f "${list}"
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

lcov_ready() {
  python3 - <<'PY'
import pathlib
import sys

roots = (pathlib.Path("target/coverage"), pathlib.Path("coverage"))
for root in roots:
    if not root.exists():
        continue
    for path in root.rglob("lcov.info"):
        if path.is_file() and path.stat().st_size > 0:
            sys.exit(0)
sys.exit(1)
PY
}

apply_scope_filter() {
  local cmd="$1"
  local edn="$2"
  local thresh="$3"
  local out rc counts findings debt
  local -a flags
  flags=(--base "${MERGE_BASE}" --edn "${edn}" --threshold "${thresh}")
  if [[ "${cmd}" == "crap" && ${#COVERAGE_PREFIX[@]} -gt 0 ]]; then
    flags+=(--coverage-expected)
  fi
  out="$(mktemp)"
  set +e
  python3 "${SCOPE_PY}" "${cmd}" "${flags[@]}" >"${out}"
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

append_mutator_test_command() {
  local -n _dest="$1"
  if [[ -n "${UB_GATES_MUTATOR_TEST_CMD:-}" ]]; then
    _dest+=(--test-command "${UB_GATES_MUTATOR_TEST_CMD}")
  fi
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
    append_mutator_test_command args
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
  append_mutator_test_command args
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
  if [[ ! -f .metrics/crap.edn ]]; then
    return 1
  fi
  apply_scope_filter crap .metrics/crap.edn 10 || return 1
  if [[ "${CRAPPER_RC}" -ne 0 && "${CRAPPER_RC}" -ne 2 ]]; then
    return 1
  fi
  return 0
}

classify_dryer() {
  DRYER_FINDINGS=0
  DRYER_DEBT=0
  DRYER_HIGH=0
  # 0 is the only dryer success code. Exit 1, 2, and every other code are
  # tool_error even when .metrics/dry.edn exists.
  if [[ "${DRYER_RC}" -ne 0 ]]; then
    return 1
  fi
  if [[ ! -f .metrics/dry.edn ]]; then
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

base_remote_name() {
  if [[ "${BASE_REF}" == */* ]]; then
    printf '%s\n' "${BASE_REF%%/*}"
  else
    printf '%s\n' "origin"
  fi
}

base_branch_name() {
  if [[ "${BASE_REF}" == */* ]]; then
    printf '%s\n' "${BASE_REF#*/}"
  else
    printf '%s\n' "${BASE_REF}"
  fi
}

repo_is_shallow() {
  [[ "$(git rev-parse --is-shallow-repository 2>/dev/null || echo false)" == "true" ]]
}

fetch_base_ref() {
  local remote branch
  remote="$(base_remote_name)"
  branch="$(base_branch_name)"
  if repo_is_shallow; then
    git fetch --unshallow "${remote}" 2>/dev/null || git fetch --unshallow 2>/dev/null || true
  fi
  if ! git rev-parse --verify "${BASE_REF}^{commit}" >/dev/null 2>&1; then
    git fetch "${remote}" "+refs/heads/${branch}:refs/remotes/${remote}/${branch}" 2>/dev/null || true
  fi
}

fetch_base_ref

if ! git rev-parse --verify "${BASE_REF}^{commit}" >/dev/null 2>&1; then
  OUTCOME="skipped_no_base_ref"
  GATE_MISS=1
  exit_for_outcome
fi

MERGE_BASE="$(git merge-base HEAD "${BASE_REF}" 2>/dev/null || echo "")"
if [[ -z "${MERGE_BASE}" ]]; then
  OUTCOME="tool_error"
  GATE_MISS=1
  TOOL_ERROR=1
  emit_warning "tool_error — no merge base between HEAD and ${BASE_REF}"
  exit_for_outcome
fi

collect_scope_files "${MERGE_BASE}"
if [[ "${SCOPE_DIFF_FAILED}" -eq 1 ]]; then
  OUTCOME="tool_error"
  GATE_MISS=1
  TOOL_ERROR=1
  emit_warning "tool_error — git diff --name-only failed"
  exit_for_outcome
fi
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
  if ! lcov_ready; then
    OUTCOME="tool_error"
    GATE_MISS=1
    TOOL_ERROR=1
    GATES_RAN=0
    emit_warning "tool_error — coverage command exited 0 but lcov is missing or empty"
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
elif [[ "${ADVISORY}" != "1" && "${MUTATOR_SKIPPED}" == "1" ]]; then
  OUTCOME="skipped_mutator"
  GATE_MISS=1
else
  OUTCOME="ran_clean"
fi

exit_for_outcome
