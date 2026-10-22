#!/usr/bin/env bash
# box-tools.sh — report and install agent tooling on this machine. (GMA-351)
#
#   scripts/box-tools.sh --check [--tools-only]
#   scripts/box-tools.sh --install [--with-rtk]
#
# --check prints one line per pstack CLI ("pstack <cli>: present|partial|missing (<detail>)")
# and one line per lean-context tool ("<tool>: present|missing (<detail>)"). It is read-only:
# it inspects files under $HOME and asks each tool for its version, and changes nothing.
# --tools-only skips the pstack lines (for CI, which has no pstack).
# Exit 0 if every pstack CLI and every required tool (rg, jq, markitdown) is present,
# 1 if any is partial/missing, 2 on usage error.
#
# --install puts pinned, SHA-256-verified rg and jq (and rtk with --with-rtk) in ~/.local/bin,
# pip --user installs pinned trafilatura, and only reports markitdown. Linux only; never uses
# sudo or edits shell rc files. On macOS it installs nothing and prints a brew hint.
set -euo pipefail

INSTALL_DIR="${HOME}/.local/bin"

# --- pinned versions (do not fetch from moving branches) ---
RG_VERSION="14.1.1"
JQ_VERSION="1.7.1"
RTK_VERSION="v1.0.1"
# trafilatura 2.3.1 needs lxml>=6.1.3; lxml 6 moved lxml.html.clean to lxml_html_clean.
TRAFILATURA_VERSION="2.3.1"
LXML_VERSION="6.1.3"
LXML_HTML_CLEAN_VERSION="0.4.5"

# https://github.com/BurntSushi/ripgrep/releases/download/14.1.1/<asset>.sha256
RG_SHA256_X86_64="4cf9f2741e6c465ffdb7c26f38056a59e2a2544b51f7cc128ef28337eeae4d8e"
RG_SHA256_AARCH64="c827481c4ff4ea10c9dc7a4022c8de5db34a5737cb74484d62eb94a95841ab2f"
# https://github.com/jqlang/jq/releases/download/jq-1.7.1/sha256sum.txt
JQ_SHA256_AMD64="5942c9b0934e510ee61eb3e30273f1b3fe2590df93933a93d7c58b81d19c8ff5"
JQ_SHA256_ARM64="4dd2d8a0661df0b22f1bb9a1f9830f06b6f3b8f7d91211a1ef5d7c4f06a8b4a5"
# https://github.com/rtk-ai/rtk/releases/download/v1.0.1/checksums.txt
RTK_SHA256_X86_64="5b919c3bccb799b67a61866d0e617410a4fcdf173e2614440e59de2fa2003436"
RTK_SHA256_AARCH64="cd627c4091ad90b5e5aca83ca5af66ee4b8aa8537a736533fa90544f461f1c2b"

usage() {
  cat >&2 <<'EOF'
usage: box-tools.sh --check [--tools-only]
       box-tools.sh --install [--with-rtk]
       box-tools.sh --help

  --check       Report pstack per CLI and rg/jq/markitdown (required),
                trafilatura/rtk (optional). Exit 0 all present, 1 otherwise.
  --tools-only  With --check: skip the pstack lines.
  --install     Linux: install rg, jq, trafilatura under ~/.local (no sudo).
                markitdown is verify-only. macOS: prints a brew hint.
  --with-rtk    With --install: also install the pinned rtk release.
EOF
}

# ---------------------------------------------------------------- pstack checks

# True if "pstack" is an exact string entry of the [plugins] enabled = [...] array.
# Section headers may carry trailing spaces or a comment; '#' outside a string starts
# a comment; ']' ends the array only outside strings and comments.
grok_enabled() {
  awk '
    function scan(s,   i, c, str) {
      for (i = 1; i <= length(s); i++) {
        c = substr(s, i, 1)
        if (inq) {
          if (c == "\\") { i++; continue }
          if (c == "\"") { inq = 0; if (buf == "pstack") found = 1; continue }
          buf = buf c
        } else if (c == "\"") { inq = 1; buf = "" }
        else if (c == "#") { return }
        else if (c == "]") { inarr = 0; return }
      }
    }
    !inarr && /^[[:space:]]*\[/ {
      h = $0; sub(/[[:space:]]*(#.*)?$/, "", h); sub(/^[[:space:]]+/, "", h); sect = h; next
    }
    inarr { scan($0); next }
    sect == "[plugins]" && /^[[:space:]]*enabled[[:space:]]*=/ {
      rest = $0; sub(/^[^=]*=[[:space:]]*/, "", rest)
      if (substr(rest, 1, 1) == "[") { inarr = 1; inq = 0; scan(substr(rest, 2)) }
    }
    END { exit found ? 0 : 1 }
  ' "$1"
}

# grok: plugin installed (registry) AND enabled in config.toml.
check_grok() {
  local reg="$HOME/.grok/installed-plugins/registry.json"
  local cfg="$HOME/.grok/config.toml"
  if [[ ! -f "$reg" ]]; then
    echo "missing (registry.json not found: $reg)"; return 1
  fi
  if ! grep -qF '"pstack"' "$reg"; then
    echo "missing (no pstack entry in $reg)"; return 1
  fi
  if [[ ! -f "$cfg" ]]; then
    echo "missing (installed but config.toml not found: $cfg)"; return 1
  fi
  if ! grok_enabled "$cfg"; then
    echo "missing (installed but not enabled in $cfg)"; return 1
  fi
  echo "present (grok plugin)"
}

# claude: marketplace plugin install OR user-level poteto-mode skill.
check_claude() {
  local inst="$HOME/.claude/plugins/installed_plugins.json"
  if [[ -f "$inst" ]] && grep -qF '"pstack@' "$inst"; then
    echo "present (claude plugin)"; return 0
  fi
  if [[ -f "$HOME/.claude/skills/poteto-mode/SKILL.md" ]]; then
    echo "present (~/.claude/skills)"; return 0
  fi
  echo "missing"; return 1
}

# cursor-agent: upstream poteto-mode skill; hub port (architect+interrogate) is partial.
check_cursor() {
  local d="$HOME/.cursor/skills"
  if [[ -f "$d/poteto-mode/SKILL.md" ]]; then
    echo "present (~/.cursor/skills)"; return 0
  fi
  if [[ -f "$d/architect/SKILL.md" && -f "$d/interrogate/SKILL.md" ]]; then
    echo "partial (hub port, no poteto-mode)"; return 1
  fi
  echo "missing"; return 1
}

# ---------------------------------------------------------------- tool checks

py_version() {
  command -v python3 >/dev/null 2>&1 || return 1
  python3 -c "import importlib.metadata as m; print(m.version('$1'))" 2>/dev/null
}

py_imports() {
  command -v python3 >/dev/null 2>&1 && python3 -c "import $1" >/dev/null 2>&1
}

# Prints the version and returns 0 if the tool is usable, else returns 1.
tool_version() {
  local v
  case "$1" in
    rg) command -v rg >/dev/null 2>&1 || return 1
        rg --version 2>/dev/null | awk 'NR == 1 { print $2 }' ;;
    jq) command -v jq >/dev/null 2>&1 || return 1
        jq --version 2>/dev/null | sed 's/^jq-//' ;;
    markitdown)
      if py_imports markitdown && v="$(py_version markitdown)"; then echo "$v"; return 0; fi
      command -v markitdown >/dev/null 2>&1 || return 1
      markitdown --version 2>/dev/null | awk 'NR == 1 { print $NF }' ;;
    trafilatura)
      py_imports trafilatura || return 1
      py_version trafilatura || echo "unknown" ;;
    rtk) command -v rtk >/dev/null 2>&1 || return 1
         rtk --version 2>/dev/null | awk 'NR == 1 { print $2 }' ;;
  esac
}

check_tools() {
  local rc=0 tool v
  for tool in rg jq markitdown trafilatura rtk; do
    if v="$(tool_version "$tool")"; then
      echo "$tool: present (${v:-unknown})"
    else
      case "$tool" in
        rg | jq | markitdown) echo "$tool: missing (required)"; rc=1 ;;
        *) echo "$tool: missing (optional)" ;;
      esac
    fi
  done
  return "$rc"
}

run_check() {
  local tools_only="$1" rc=0 out
  if [[ "$tools_only" -eq 0 ]]; then
    out=$(check_grok) || rc=1;   echo "pstack grok: $out"
    out=$(check_claude) || rc=1; echo "pstack claude: $out"
    out=$(check_cursor) || rc=1; echo "pstack cursor-agent: $out"
  fi
  check_tools || rc=1
  return "$rc"
}

# ---------------------------------------------------------------- install (Linux)

detect_linux_arch() {
  local machine
  machine="$(uname -m)"
  case "${machine}" in
    x86_64 | amd64) echo "x86_64" ;;
    aarch64 | arm64) echo "aarch64" ;;
    *) echo "unsupported architecture: ${machine}" >&2; exit 1 ;;
  esac
}

verify_sha256_file() {
  local file="$1" expected="$2" label="$3" actual
  if ! command -v sha256sum >/dev/null 2>&1; then
    echo "sha256sum is required to verify ${label}" >&2; exit 1
  fi
  actual="$(sha256sum "${file}" | awk '{print $1}')"
  if [[ "${actual}" != "${expected}" ]]; then
    echo "checksum mismatch for ${label}: expected ${expected}, got ${actual}" >&2; exit 1
  fi
}

safe_tar_extract() {
  local archive="$1" dest="$2"
  if tar -tzf "${archive}" | grep -qE '^/|(^|/)\.\.(/|$)'; then
    echo "refusing to extract archive with unsafe paths: ${archive}" >&2; exit 1
  fi
  tar -xzf "${archive}" -C "${dest}"
}

install_rg() {
  if tool_version rg >/dev/null; then echo "skip rg (already present)"; return 0; fi
  local arch asset tmp archive extracted
  arch="$(detect_linux_arch)"
  case "${arch}" in
    x86_64) asset="ripgrep-${RG_VERSION}-x86_64-unknown-linux-musl.tar.gz" ;;
    aarch64) asset="ripgrep-${RG_VERSION}-aarch64-unknown-linux-gnu.tar.gz" ;;
  esac
  tmp="$(mktemp -d)"
  archive="${tmp}/${asset}"
  curl -fsSL "https://github.com/BurntSushi/ripgrep/releases/download/${RG_VERSION}/${asset}" -o "${archive}"
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
  if tool_version jq >/dev/null; then echo "skip jq (already present)"; return 0; fi
  local arch asset tmp binary
  arch="$(detect_linux_arch)"
  case "${arch}" in
    x86_64) asset="jq-linux-amd64" ;;
    aarch64) asset="jq-linux-arm64" ;;
  esac
  tmp="$(mktemp -d)"
  binary="${tmp}/jq"
  curl -fsSL "https://github.com/jqlang/jq/releases/download/jq-${JQ_VERSION}/${asset}" -o "${binary}"
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
  if tool_version trafilatura >/dev/null; then echo "skip trafilatura (already present)"; return 0; fi
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required to install trafilatura" >&2; exit 1
  fi
  # PEP 668: --user alone can be blocked; with --user, --break-system-packages stays in ~/.local.
  python3 -m pip install --user --break-system-packages \
    "trafilatura==${TRAFILATURA_VERSION}" "lxml==${LXML_VERSION}" \
    "lxml_html_clean==${LXML_HTML_CLEAN_VERSION}"
  if ! py_imports trafilatura; then
    echo "trafilatura ${TRAFILATURA_VERSION} installed but does not import; check lxml/lxml_html_clean" >&2
    exit 1
  fi
  echo "installed trafilatura ${TRAFILATURA_VERSION} (pip --user)"
}

install_rtk() {
  if tool_version rtk >/dev/null; then echo "skip rtk (already present)"; return 0; fi
  local arch asset tmp archive expected
  arch="$(detect_linux_arch)"
  case "${arch}" in
    x86_64) asset="rtk-x86_64-unknown-linux-musl.tar.gz"; expected="${RTK_SHA256_X86_64}" ;;
    aarch64) asset="rtk-aarch64-unknown-linux-gnu.tar.gz"; expected="${RTK_SHA256_AARCH64}" ;;
  esac
  tmp="$(mktemp -d)"
  archive="${tmp}/${asset}"
  curl -fsSL "https://github.com/rtk-ai/rtk/releases/download/${RTK_VERSION}/${asset}" -o "${archive}"
  verify_sha256_file "${archive}" "${expected}" "${asset}"
  safe_tar_extract "${archive}" "${tmp}"
  mkdir -p "${INSTALL_DIR}"
  install -m 0755 "${tmp}/rtk" "${INSTALL_DIR}/rtk"
  rm -rf "${tmp}"
  echo "installed rtk ${RTK_VERSION} -> ${INSTALL_DIR}/rtk"
}

report_markitdown() {
  if tool_version markitdown >/dev/null; then
    echo "skip markitdown (already present; verify-only)"
  else
    echo "markitdown missing (verify-only; install with: python3 -m pip install --user markitdown)" >&2
  fi
}

run_install() {
  local with_rtk="$1"
  if [[ "$(uname -s)" == "Darwin" ]]; then
    echo "macOS: box-tools installs nothing here. Use: brew install ripgrep jq" \
      "&& python3 -m pip install --user markitdown trafilatura lxml_html_clean"
    return 0
  fi
  install_rg
  install_jq
  report_markitdown
  install_trafilatura
  if [[ "${with_rtk}" -eq 1 ]]; then install_rtk; fi
  case ":${PATH}:" in
    *":${INSTALL_DIR}:"*) ;;
    *) echo "hint: add ${INSTALL_DIR} to PATH to use installed tools" >&2 ;;
  esac
}

main() {
  local mode="" tools_only=0 with_rtk=0
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --check) [[ -z "$mode" ]] || { usage; exit 2; }; mode=check ;;
      --install) [[ -z "$mode" ]] || { usage; exit 2; }; mode=install ;;
      --tools-only) tools_only=1 ;;
      --with-rtk) with_rtk=1 ;;
      --help | -h) usage; exit 0 ;;
      *) usage; exit 2 ;;
    esac
    shift
  done
  case "$mode" in
    check)
      [[ "$with_rtk" -eq 0 ]] || { usage; exit 2; }
      run_check "$tools_only" || exit 1 ;;
    install)
      [[ "$tools_only" -eq 0 ]] || { usage; exit 2; }
      run_install "$with_rtk" ;;
    *) usage; exit 2 ;;
  esac
}

main "$@"
