#!/usr/bin/env bash
# Run ub-gates in a throwaway container. No host installs.
# The only host write is a copy of .metrics in a temp directory.
# Worktree is mounted read-only. The main git directory is mounted read-only
# when it lives outside the worktree. Tools are installed only inside the
# container (rust:1.83, uv venv, pinned crapper/dryer/mutator).
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash scripts/ub_gates_container.sh [--help] [--worktree PATH] [--main-git PATH] [--metrics-dir PATH]

Run scripts/run_ub_gates_ci.sh inside `docker run --rm` on image rust:1.83.
uv creates a Python 3.13 virtualenv inside the container and installs the
pinned crapper, dryer, and mutator there. The worktree mount is read-only (:ro).
The main git directory is mounted :ro when it is outside the worktree.
.metrics is copied to a temp directory on the host. Nothing else is written
on the host. The launcher sets UB_GATES_ADVISORY=0.
EOF
}

inside() {
  if ! command -v git >/dev/null 2>&1 || ! command -v curl >/dev/null 2>&1; then
    apt-get update -qq
    apt-get install -y -qq git ca-certificates curl
  fi
  git config --global --add safe.directory '*'
  lock="/work/scripts/ub-tools.lock"
  uv_ver="$(awk -F= '$1=="uv" {print $2; exit}' "${lock}")"
  py_ver="$(awk -F= '$1=="python" {print $2; exit}' "${lock}")"
  test -n "${uv_ver}"
  test -n "${py_ver}"
  curl -LsSf "https://astral.sh/uv/${uv_ver}/install.sh" | env UV_INSTALL_DIR=/tmp/uv UV_NO_MODIFY_PATH=1 sh
  /tmp/uv/uv venv -p "${py_ver}" /opt/ub/.venv
  dest="/opt/ub/src"
  mkdir -p "${dest}"
  clone_tool() {
    local name="$1"
    local url="$2"
    local sha="$3"
    local dir="${dest}/${name}"
    mkdir -p "${dir}"
    git -C "${dir}" init -q
    git -C "${dir}" remote add origin "${url}"
    git -C "${dir}" fetch origin "${sha}"
    git -C "${dir}" checkout --detach FETCH_HEAD
    local head
    head="$(cd "${dir}" && git rev-parse HEAD)"
    if [[ "${head}" != "${sha}" ]]; then
      echo "ub-gates container: ${name} HEAD ${head} does not equal lock ${sha}" >&2
      exit 1
    fi
  }
  clone_tool crapper https://github.com/unclebob/crapper "$(awk -F= '$1=="crapper" {print $2; exit}' "${lock}")"
  clone_tool dryer https://github.com/unclebob/dryer "$(awk -F= '$1=="dryer" {print $2; exit}' "${lock}")"
  clone_tool mutator https://github.com/unclebob/mutator "$(awk -F= '$1=="mutator" {print $2; exit}' "${lock}")"
  VIRTUAL_ENV=/opt/ub/.venv /tmp/uv/uv pip install "${dest}/crapper" "${dest}/dryer" "${dest}/mutator"
  rm -rf /tmp/app
  git clone --shared /work /tmp/app
  cd /tmp/app
  export PATH="/opt/ub/.venv/bin:${PATH}"
  export UB_GATES_ADVISORY=0
  set +e
  bash /work/scripts/run_ub_gates_ci.sh
  rc=$?
  set -e
  if [[ -d .metrics ]]; then
    mkdir -p /metrics-out
    cp -a .metrics/. /metrics-out/
  fi
  exit "${rc}"
}

WORKTREE=""
MAIN_GIT=""
METRICS_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help|help)
      usage
      exit 0
      ;;
    --inside)
      inside
      exit 0
      ;;
    --worktree)
      WORKTREE="${2:-}"
      shift 2
      ;;
    --main-git)
      MAIN_GIT="${2:-}"
      shift 2
      ;;
    --metrics-dir)
      METRICS_DIR="${2:-}"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "${WORKTREE}" ]]; then
  WORKTREE="$(pwd)"
fi
if [[ -z "${MAIN_GIT}" ]]; then
  if git -C "${WORKTREE}" rev-parse --git-common-dir >/dev/null 2>&1; then
    MAIN_GIT="$(git -C "${WORKTREE}" rev-parse --git-common-dir)"
    case "${MAIN_GIT}" in
      /*) ;;
      *) MAIN_GIT="$(cd "${WORKTREE}" && cd "${MAIN_GIT}" && pwd)" ;;
    esac
  else
    MAIN_GIT="${WORKTREE}/.git"
  fi
fi
if [[ -z "${METRICS_DIR}" ]]; then
  METRICS_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ub-gates-metrics.XXXXXX")"
fi
mkdir -p "${METRICS_DIR}"

mounts=(-v "${WORKTREE}:/work:ro" -v "${METRICS_DIR}:/metrics-out")
case "${MAIN_GIT}" in
  "${WORKTREE}/.git"|"${WORKTREE}/.git/") ;;
  *) mounts+=(-v "${MAIN_GIT}:${MAIN_GIT}:ro") ;;
esac

printf '%s\n' "${METRICS_DIR}"
docker run --rm -i \
  "${mounts[@]}" \
  -e UB_GATES_ADVISORY=0 \
  -e "UB_GATES_BASE_REF=${UB_GATES_BASE_REF:-origin/main}" \
  -e "UB_GATES_COVERAGE_CMD=${UB_GATES_COVERAGE_CMD:-}" \
  -e "UB_GATES_MUTATOR_TEST_CMD=${UB_GATES_MUTATOR_TEST_CMD:-}" \
  -w /tmp \
  rust:1.83 \
  bash -s <<'EOS'
set -euo pipefail
if command -v git >/dev/null 2>&1; then
  git config --global --add safe.directory '*'
fi
exec bash /work/scripts/ub_gates_container.sh --inside
EOS
