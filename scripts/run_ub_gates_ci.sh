#!/usr/bin/env bash
# Advisory ub-mode gates for CI (GMA-410). Same commands as implementer pre-PR dev flow.
# Prerequisites: crapper, dryer, mutator on PATH; coverage for mutator/crapper (see gates-by-language.md).
set -euo pipefail

ADVISORY="${UB_GATES_ADVISORY:-1}"
BASE_REF="${UB_GATES_BASE_REF:-origin/main}"

log() { printf '%s\n' "$*"; }
finish() {
  local rc="$1"
  if [[ "${ADVISORY}" == "1" && "${rc}" -ne 0 ]]; then
    log "ub-gates: advisory mode — reporting exit ${rc} without failing the job"
    exit 0
  fi
  exit "${rc}"
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  log "ub-gates: not a git checkout — skip"
  exit 0
fi

if git show-ref --verify --quiet "refs/remotes/${BASE_REF#origin/}" 2>/dev/null || git show-ref --verify --quiet "${BASE_REF}" 2>/dev/null; then
  :
else
  git fetch origin main --depth=1 2>/dev/null || true
fi

MERGE_BASE="$(git merge-base HEAD "${BASE_REF}" 2>/dev/null || echo "")"
if [[ -z "${MERGE_BASE}" ]]; then
  log "ub-gates: no merge base with ${BASE_REF} — skip"
  exit 0
fi

CHANGED="$(git diff --name-only "${MERGE_BASE}"...HEAD || true)"
if [[ -z "${CHANGED}" ]]; then
  log "ub-gates: no changed files — skip"
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
  log "ub-gates: prerequisite — install crapper, dryer, and mutator on PATH (see skills/ub-mode/references/gates-by-language.md)"
  log "ub-gates: CI job present; tools missing — skip run (document in PR Gates: line)"
  exit 0
fi

log "ub-gates: running on diff ${MERGE_BASE}...HEAD (advisory=${ADVISORY})"

set +e
"${CRAPPER}" --changed --threshold 10
crapper_rc=$?
rm -f .metrics/dry.edn
"${DRYER}" --changed --threshold 0.8
dryer_rc=$?
"${MUTATOR}" --changed
mutator_rc=$?
set -e

log "ub-gates: crapper exit ${crapper_rc}; dryer exit ${dryer_rc}; mutator exit ${mutator_rc}"

worst=0
[[ "${crapper_rc}" -ne 0 ]] && worst="${crapper_rc}"
[[ "${dryer_rc}" -ne 0 && "${dryer_rc}" -gt "${worst}" ]] && worst="${dryer_rc}"
[[ "${mutator_rc}" -ne 0 && "${mutator_rc}" -gt "${worst}" ]] && worst="${mutator_rc}"

finish "${worst}"
