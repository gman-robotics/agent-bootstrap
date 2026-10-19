#!/usr/bin/env bash
# User-space installer/checker for lean-context CLI helpers (GMA-351).
# Installs into ~/.local/bin only; never uses sudo or edits shell rc files.
set -euo pipefail

INSTALL_DIR="${HOME}/.local/bin"
WITH_RTK=0
MODE=install

# --- pinned versions (do not fetch from moving branches) ---
RG_VERSION="14.1.1"
JQ_VERSION="1.7.1"
TRAFILATURA_VERSION="2.3.1"
RTK_VERSION="v1.0.1"

# ripgrep per-asset .sha256 files:
# https://github.com/BurntSushi/ripgrep/releases/download/14.1.1/<asset>.sha256
RG_SHA256_X86_64="4cf9f2741e6c465ffdb7c26f38056a59e2a2544b51f7cc128ef28337eeae4d8e"
RG_SHA256_AARCH64="c827481c4ff4ea10c9dc7a4022c8de5db34a5737cb74484d62eb94a95841ab2f"

# jq sha256sum.txt:
# https://github.com/jqlang/jq/releases/download/jq-1.7.1/sha256sum.txt
JQ_SHA256_AMD64="5942c9b0934e510ee61eb3e30273f1b3fe2590df93933a93d7c58b81d19c8ff5"
JQ_SHA256_ARM64="4dd2d8a0661df0b22f1bb9a1f9830f06b6f3b8f7d91211a1ef5d7c4f06a8b4a5"

# rtk checksums.txt:
# https://github.com/rtk-ai/rtk/releases/download/v1.0.1/checksums.txt
RTK_SHA256_X86_64="5b919c3bccb799b67a61866d0e617410a4fcdf173e2614440e59de2fa2003436"
RTK_SHA256_AARCH64="cd627c4091ad90b5e5aca83ca5af66ee4b8aa8537a736533fa90544f461f1c2b"

usage() {
  cat <<'EOF'
Usage: box-tools.sh [--check | --help] [--with-rtk]

Install or verify user-space CLI helpers for lean-context work:
  rg, jq (required binaries), markitdown (verify only — never installed here),
  trafilatura (optional pip), rtk (optional binary with --with-rtk).

  --check   Report present/missing; exit non-zero if a required tool is missing.
  --help    Show this help.
  --with-rtk  Also install the pinned rtk release (never runs rtk init).

Installs into ~/.local/bin. Uses pip --user for Python packages. No sudo.
EOF
}

path_hint_if_needed() {
  case ":${PATH}:" in
    *":${INSTALL_DIR}:"*) ;;
    *)
      echo "hint: add ${INSTALL_DIR} to PATH to use installed tools" >&2
      ;;
  esac
}

detect_linux_arch() {
  local machine
  machine="$(uname -m)"
  case "${machine}" in
    x86_64 | amd64)
      echo "x86_64"
      ;;
    aarch64 | arm64)
      echo "aarch64"
      ;;
    *)
      echo "unsupported architecture: ${machine}" >&2
      exit 1
      ;;
  esac
}

verify_sha256_file() {
  local file="$1" expected="$2" label="$3"
  local actual
  if ! command -v sha256sum >/dev/null 2>&1; then
    echo "sha256sum is required to verify ${label}" >&2
    exit 1
  fi
  actual="$(sha256sum "${file}" | awk '{print $1}')"
  if [[ "${actual}" != "${expected}" ]]; then
    echo "checksum mismatch for ${label}: expected ${expected}, got ${actual}" >&2
    exit 1
  fi
}

safe_tar_extract() {
  local archive="$1" dest="$2"
  if tar -tzf "${archive}" | grep -qE '^/|(^|/)\.\.(/|$)'; then
    echo "refusing to extract archive with unsafe paths: ${archive}" >&2
    exit 1
  fi
  tar -xzf "${archive}" -C "${dest}"
}

command_version() {
  local tool="$1"
  case "${tool}" in
    rg)
      if command -v rg >/dev/null 2>&1; then
        rg --version 2>/dev/null | awk '{print $2; exit}'
      fi
      ;;
    jq)
      if command -v jq >/dev/null 2>&1; then
        jq --version 2>/dev/null | sed 's/^jq-//'
      fi
      ;;
    markitdown)
      if command -v markitdown >/dev/null 2>&1; then
        markitdown --version 2>/dev/null | head -n1
        return 0
      fi
      if python3 -c "import markitdown" >/dev/null 2>&1; then
        python3 -c "import importlib.metadata as m; print(m.version('markitdown'))"
      fi
      ;;
    trafilatura)
      if python3 -c "import trafilatura" >/dev/null 2>&1; then
        python3 -c "import importlib.metadata as m; print(m.version('trafilatura'))"
      fi
      ;;
    rtk)
      if command -v rtk >/dev/null 2>&1; then
        rtk --version 2>/dev/null | awk '{print $1; exit}'
      fi
      ;;
  esac
}

tool_present() {
  local tool="$1"
  [[ -n "$(command_version "${tool}" || true)" ]]
}

report_check_line() {
  local tool="$1"
  local version
  version="$(command_version "${tool}" || true)"
  if [[ -n "${version}" ]]; then
    printf 'present %s %s\n' "${tool}" "${version}"
    return 0
  fi
  printf 'missing %s\n' "${tool}"
  return 1
}

run_check() {
  local failed=0
  local tool
  for tool in rg jq markitdown trafilatura rtk; do
    if ! report_check_line "${tool}"; then
      case "${tool}" in
        rg | jq | markitdown) failed=1 ;;
      esac
    fi
  done
  return "${failed}"
}

install_rg() {
  if tool_present rg; then
    echo "skip rg (already present)"
    return 0
  fi
  local arch asset url tmp archive extracted
  arch="$(detect_linux_arch)"
  case "${arch}" in
    x86_64)
      asset="ripgrep-${RG_VERSION}-x86_64-unknown-linux-musl.tar.gz"
      ;;
    aarch64)
      asset="ripgrep-${RG_VERSION}-aarch64-unknown-linux-gnu.tar.gz"
      ;;
  esac
  url="https://github.com/BurntSushi/ripgrep/releases/download/${RG_VERSION}/${asset}"
  tmp="$(mktemp -d)"
  archive="${tmp}/${asset}"
  curl -fsSL "${url}" -o "${archive}"
  case "${arch}" in
    x86_64) verify_sha256_file "${archive}" "${RG_SHA256_X86_64}" "${asset}" ;;
    aarch64) verify_sha256_file "${archive}" "${RG_SHA256_AARCH64}" "${asset}" ;;
  esac
  safe_tar_extract "${archive}" "${tmp}"
  extracted="$(find "${tmp}" -name rg -type f | head -n1)"
  mkdir -p "${INSTALL_DIR}"
  install -m 0755 "${extracted}" "${INSTALL_DIR}/rg"
  rm -rf "${tmp}"
  echo "installed rg ${RG_VERSION} -> ${INSTALL_DIR}/rg"
}

install_jq() {
  if tool_present jq; then
    echo "skip jq (already present)"
    return 0
  fi
  local arch asset url tmp binary
  arch="$(detect_linux_arch)"
  case "${arch}" in
    x86_64) asset="jq-linux-amd64" ;;
    aarch64) asset="jq-linux-arm64" ;;
  esac
  url="https://github.com/jqlang/jq/releases/download/jq-${JQ_VERSION}/${asset}"
  tmp="$(mktemp -d)"
  binary="${tmp}/jq"
  curl -fsSL "${url}" -o "${binary}"
  case "${arch}" in
    x86_64) verify_sha256_file "${binary}" "${JQ_SHA256_AMD64}" "${asset}" ;;
    aarch64) verify_sha256_file "${binary}" "${JQ_SHA256_ARM64}" "${asset}" ;;
  esac
  mkdir -p "${INSTALL_DIR}"
  install -m 0755 "${binary}" "${INSTALL_DIR}/jq"
  rm -rf "${tmp}"
  echo "installed jq ${JQ_VERSION} -> ${INSTALL_DIR}/jq"
}

install_trafilatura() {
  if tool_present trafilatura; then
    echo "skip trafilatura (already present)"
    return 0
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required to install trafilatura" >&2
    exit 1
  fi
  # PEP 668 (Debian/Ubuntu): --user alone can still be blocked; --break-system-packages
  # with --user keeps installs under ~/.local only.
  python3 -m pip install --user --break-system-packages "trafilatura==${TRAFILATURA_VERSION}"
  echo "installed trafilatura ${TRAFILATURA_VERSION} (pip --user)"
}

install_rtk() {
  if tool_present rtk; then
    echo "skip rtk (already present)"
    return 0
  fi
  local arch asset url tmp archive expected
  arch="$(detect_linux_arch)"
  case "${arch}" in
    x86_64)
      asset="rtk-x86_64-unknown-linux-musl.tar.gz"
      expected="${RTK_SHA256_X86_64}"
      ;;
    aarch64)
      asset="rtk-aarch64-unknown-linux-gnu.tar.gz"
      expected="${RTK_SHA256_AARCH64}"
      ;;
  esac
  url="https://github.com/rtk-ai/rtk/releases/download/${RTK_VERSION}/${asset}"
  tmp="$(mktemp -d)"
  archive="${tmp}/${asset}"
  curl -fsSL "${url}" -o "${archive}"
  verify_sha256_file "${archive}" "${expected}" "${asset}"
  safe_tar_extract "${archive}" "${tmp}"
  mkdir -p "${INSTALL_DIR}"
  install -m 0755 "${tmp}/rtk" "${INSTALL_DIR}/rtk"
  rm -rf "${tmp}"
  echo "installed rtk ${RTK_VERSION} -> ${INSTALL_DIR}/rtk"
}

report_markitdown() {
  if tool_present markitdown; then
    echo "markitdown present ($(command_version markitdown))"
  else
    echo "markitdown missing (verify-only in box-tools; install with: python3 -m pip install --user markitdown)" >&2
  fi
}

run_install() {
  mkdir -p "${INSTALL_DIR}"
  install_rg
  install_jq
  report_markitdown
  install_trafilatura
  if [[ "${WITH_RTK}" -eq 1 ]]; then
    install_rtk
  fi
  path_hint_if_needed
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check)
      MODE=check
      shift
      ;;
    --help | -h)
      usage
      exit 0
      ;;
    --with-rtk)
      WITH_RTK=1
      shift
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

case "${MODE}" in
  check)
    run_check
    ;;
  install)
    run_install
    ;;
esac
