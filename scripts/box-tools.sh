#!/usr/bin/env bash
# box-tools.sh — report agent tooling presence on this machine. (GMA-351)
#
#   scripts/box-tools.sh --check
#
# Prints one line per CLI: "pstack <cli>: present|partial|missing (<detail>)".
# Read-only: inspects files under $HOME only, runs no CLI and changes nothing.
# Exit 0 if every CLI has pstack, 1 if any is partial/missing, 2 on usage error.
set -euo pipefail

usage() { echo "usage: $0 --check" >&2; }

# True if "pstack" appears in the [plugins] enabled = [...] array (single or multi-line).
grok_enabled() {
  awk '
    /^\[/ { sect = $0; inarr = 0 }
    sect == "[plugins]" && /^[[:space:]]*enabled[[:space:]]*=/ { inarr = 1 }
    inarr && /"pstack"/ { found = 1 }
    inarr && /\]/ { inarr = 0 }
    END { exit found ? 0 : 1 }
  ' "$1"
}

# grok: plugin installed (registry) AND enabled in config.toml.
check_grok() {
  local reg="$HOME/.grok/installed-plugins/registry.json"
  local cfg="$HOME/.grok/config.toml"
  if [[ ! -f "$reg" ]] || ! grep -q '"pstack"' "$reg"; then
    echo "missing (not in $reg)"; return 1
  fi
  if [[ ! -f "$cfg" ]] || ! grok_enabled "$cfg"; then
    echo "missing (installed but not enabled in $cfg)"; return 1
  fi
  echo "present (grok plugin)"
}

# claude: marketplace plugin install OR user-level poteto-mode skill.
check_claude() {
  local inst="$HOME/.claude/plugins/installed_plugins.json"
  if [[ -f "$inst" ]] && grep -q '"pstack@' "$inst"; then
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

main() {
  if [[ $# -ne 1 || "$1" != "--check" ]]; then usage; exit 2; fi
  local rc=0 out
  out=$(check_grok) || rc=1;   echo "pstack grok: $out"
  out=$(check_claude) || rc=1; echo "pstack claude: $out"
  out=$(check_cursor) || rc=1; echo "pstack cursor-agent: $out"
  exit "$rc"
}

main "$@"
