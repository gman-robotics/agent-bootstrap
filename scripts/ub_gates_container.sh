#!/usr/bin/env bash
# Run ub-gates in a throwaway container. No host installs.
# The only host write is a copy of .metrics in a temp directory.
# Worktree is mounted read-only. The main git directory is mounted read-only
# when it lives outside the worktree. Tools are installed only inside the
# container. The image comes from scripts/ub-tools.lock: rust_image
# (rust:1.83) or go_image (golang:1.26) when the worktree lists go.mod.
# UB_GATES_IMAGE overrides that choice. A worktree with go.mod and
# Cargo.toml needs UB_GATES_IMAGE. uv venv, pinned crapper/dryer/mutator.
# The throwaway clone is cleared except .git, then the mounted worktree is
# copied in place so a directory is replaced, not nested. The clone commit
# stays inside the container. The host repository is not committed.
# refs/remotes/$UB_GATES_BASE_REF is copied from the mounted worktree.
# UB_GATES_ADVISORY stays 0. Coverage and the mutator test command stay empty
# unless the caller sets them. requirements-dev.txt is installed into the
# container venv when that file is present.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash scripts/ub_gates_container.sh [--help] [--worktree PATH] [--main-git PATH] [--metrics-dir PATH]

Run scripts/run_ub_gates_ci.sh inside `docker run --rm`.
The image comes from scripts/ub-tools.lock (`rust_image`, default rust:1.83).
A worktree that lists go.mod and no Cargo.toml uses `go_image` (golang:1.26).
Set UB_GATES_IMAGE to select the image. Set it when the worktree has both
go.mod and Cargo.toml. uv creates a Python 3.13 virtualenv inside the
container and installs the pinned crapper, dryer, and mutator there. When
requirements-dev.txt is present it is installed into that venv. The worktree
mount is read-only (:ro). The main git directory is mounted :ro when it is
outside the worktree. .metrics is copied to a temp directory on the host.
Nothing else is written on the host. The launcher sets UB_GATES_ADVISORY=0.
EOF
}

overlay_worktree() {
  local src="$1"
  local dest="$2"
  find "${dest}" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
  find "${src}" -mindepth 1 -maxdepth 1 ! -name .git -exec cp -a {} "${dest}/" \;
}

map_base_ref() {
  local src="$1"
  local dest="$2"
  local remote_ref="refs/remotes/${UB_GATES_BASE_REF:-origin/main}"
  if git -C "${src}" rev-parse --verify "${remote_ref}^{commit}" >/dev/null 2>&1; then
    git -C "${dest}" update-ref "${remote_ref}" "$(git -C "${src}" rev-parse "${remote_ref}")"
  fi
}

commit_local_scope() {
  git add -A
  if ! git diff --cached --quiet; then
    git -c user.email="ub-gates@localhost" -c user.name="ub-gates" commit -q -m "ub-gates local scope"
  fi
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
  if [[ -f /work/requirements-dev.txt ]]; then
    VIRTUAL_ENV=/opt/ub/.venv /tmp/uv/uv pip install -r /work/requirements-dev.txt
  fi
  rm -rf /tmp/app
  git clone --shared /work /tmp/app
  map_base_ref /work /tmp/app
  overlay_worktree /work /tmp/app
  cd /tmp/app
  commit_local_scope
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

lock_field() {
  local file="$1"
  local key="$2"
  awk -F= -v k="${key}" '$1==k {print $2; exit}' "${file}"
}

read_lock_images() {
  local lock="$1"
  if [[ ! -f "${lock}" ]]; then
    printf 'ub-gates container: missing scripts/ub-tools.lock\n' >&2
    return 2
  fi
  READ_RUST_IMAGE="$(lock_field "${lock}" rust_image)"
  READ_GO_IMAGE="$(lock_field "${lock}" go_image)"
  if [[ -z "${READ_RUST_IMAGE}" || -z "${READ_GO_IMAGE}" ]]; then
    printf 'ub-gates container: scripts/ub-tools.lock must set rust_image and go_image\n' >&2
    return 2
  fi
}

file_listed() {
  local listing="$1"
  local name="$2"
  while IFS= read -r line; do [[ "${line##*/}" == "${name}" ]] && return 0; done < "${listing}"; return 1
}

choose_image() {
  local has_go="$1"
  local has_cargo="$2"
  local rust_image="$3"
  local go_image="$4"
  if [[ "${has_go}" -eq 1 && "${has_cargo}" -eq 1 ]]; then
    printf 'ub-gates container: worktree has go.mod and Cargo.toml; set UB_GATES_IMAGE\n' >&2
    return 2
  fi
  if [[ "${has_go}" -eq 1 ]]; then
    printf '%s\n' "${go_image}"
    return 0
  fi
  printf '%s\n' "${rust_image}"
}

pick_image() {
  local worktree="$1"
  local lock listing rc has_go has_cargo
  if [[ -n "${UB_GATES_IMAGE:-}" ]]; then
    printf '%s\n' "${UB_GATES_IMAGE}"
    return 0
  fi
  lock="${worktree}/scripts/ub-tools.lock"
  read_lock_images "${lock}" || return $?
  listing="$(mktemp)"
  set +e
  git -C "${worktree}" ls-files -co --exclude-standard >"${listing}" 2>/dev/null
  rc=$?
  set -e
  if [[ "${rc}" -ne 0 ]]; then
    rm -f "${listing}"
    printf '%s\n' "${READ_RUST_IMAGE}"
    return 0
  fi
  has_go=0
  has_cargo=0
  if file_listed "${listing}" "go.mod"; then
    has_go=1
  fi
  if file_listed "${listing}" "Cargo.toml"; then
    has_cargo=1
  fi
  rm -f "${listing}"
  choose_image "${has_go}" "${has_cargo}" "${READ_RUST_IMAGE}" "${READ_GO_IMAGE}"
}

main() {
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

  local image pick_rc
  set +e
  image="$(pick_image "${WORKTREE}")"
  pick_rc=$?
  set -e
  if [[ "${pick_rc}" -ne 0 ]]; then
    exit "${pick_rc}"
  fi

  printf '%s\n' "${METRICS_DIR}"
  docker run --rm -i \
    "${mounts[@]}" \
    -e UB_GATES_ADVISORY=0 \
    -e "UB_GATES_BASE_REF=${UB_GATES_BASE_REF:-origin/main}" \
    -e "UB_GATES_COVERAGE_CMD=${UB_GATES_COVERAGE_CMD:-}" \
    -e "UB_GATES_MUTATOR_TEST_CMD=${UB_GATES_MUTATOR_TEST_CMD:-}" \
    -w /tmp \
    "${image}" \
    bash -s <<'EOS'
set -euo pipefail
if command -v git >/dev/null 2>&1; then
  git config --global --add safe.directory '*'
fi
exec bash /work/scripts/ub_gates_container.sh --inside
EOS
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
