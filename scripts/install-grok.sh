#!/usr/bin/env bash
# install-grok.sh — Install / refresh agent-bootstrap skills + agents for Grok
#
# Works with the committed .grok/ structure added in the Grok native packaging PR.
#
# Primary use cases:
#   1. "When grok build loads this repo" → skills & agents are already discoverable.
#   2. Using the bootstrap's skills/agents in *other* projects (the main value of the hub).
#
# Usage:
#   bash scripts/install-grok.sh --help
#   bash scripts/install-grok.sh --local                    # verify/refresh .grok/ in this clone
#   bash scripts/install-grok.sh                            # install to ~/.grok/plugins/agent-bootstrap
#   bash scripts/install-grok.sh --force                    # overwrite existing export

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

MODE="user"     # user | local
TARGET=""
FORCE=0
HELP=0

usage() {
  cat <<EOF
$SCRIPT_NAME — Grok support installer for the agent-bootstrap hub

Options:
  --local               Operate on the current (or --target) checkout
  --target <dir>        Base directory (defaults to REPO_ROOT for --local, ~/.grok/plugins/agent-bootstrap otherwise)
  --force               Overwrite existing files
  --help                Show this message

When run without --local, the script installs the skills and agents so they are
available in any project via Grok's plugin system.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --local)  MODE="local"; shift ;;
    --target) TARGET="$2"; shift 2 ;;
    --force)  FORCE=1; shift ;;
    -h|--help) HELP=1; shift ;;
    *) echo "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

if [[ $HELP -eq 1 ]]; then
  usage; exit 0
fi

if [[ -z "$TARGET" ]]; then
  if [[ "$MODE" == "local" ]]; then
    TARGET="$REPO_ROOT"
  else
    TARGET="${HOME}/.grok/plugins/agent-bootstrap"
  fi
fi

GROK_DIR="${TARGET}/.grok"
SKILLS_DIR="${GROK_DIR}/skills"
AGENTS_DIR="${GROK_DIR}/agents"

echo "→ Mode:   ${MODE}"
echo "→ Target: ${TARGET}"
echo ""

mkdir -p "${SKILLS_DIR}" "${AGENTS_DIR}"

# --- Skills (use the canonical exporter) ---
echo "→ Exporting skills using export_codex_skills.py ..."
EXPORT_ARGS=(--source-dir "${REPO_ROOT}/skills" --output-dir "${SKILLS_DIR}")
if [[ $FORCE -eq 1 ]]; then
  EXPORT_ARGS+=(--force)
fi
python3 "${REPO_ROOT}/scripts/export_codex_skills.py" "${EXPORT_ARGS[@]}"
echo "  ✓ Skills exported to ${SKILLS_DIR}"

# --- Agents ---
# For --local (source repo): we keep the committed versions as decided by the packaging PR
#   (they use the original frontmatter + the body is the canonical role definition).
#
# For user/plugin installs (the important cross-project case): we generate proper
# Grok-native frontmatter (tools, model: sonnet, color, prompt_mode, agents_md)
# while keeping the role body from the canonical agents/*.md.
echo "→ Installing agent definitions ..."
if [[ $FORCE -eq 1 ]]; then
  rm -rf "${AGENTS_DIR}"/*
fi

if [[ "$MODE" == "local" || "$TARGET" == "$REPO_ROOT" ]]; then
  # Development mode inside the hub: copy the committed .grok/agents/ as-is
  cp -r "${REPO_ROOT}/.grok/agents/"* "${AGENTS_DIR}/" 2>/dev/null || true
  echo "  ✓ Agents copied from committed .grok/agents/ (local mode)"
else
  # Plugin / cross-project install: generate Grok-optimized frontmatter
  for agent_src in "${REPO_ROOT}/agents/"*.md; do
    [[ -f "$agent_src" ]] || continue
    base="$(basename "$agent_src")"
    out="${AGENTS_DIR}/${base}"

    # Determine nice name and color
    case "$base" in
      software-architect.md)   nice_name="software-architect"; color="blue" ;;
      software-engineer.md)    nice_name="software-engineer";  color="green" ;;
      qa-critical-reviewer.md) nice_name="qa-critical-reviewer"; color="red" ;;
      ui-ux-engineer.md)       nice_name="ui-ux-engineer";      color="purple" ;;
      security-reviewer.md)    nice_name="security-reviewer";   color="orange" ;;
      *) nice_name="${base%.md}"; color="gray" ;;
    esac

    # Extract body after the second --- (portable awk)
    body="$(awk '/^---/ {c++} c==2 && !/^---/' "$agent_src")"
    if [[ -z "$body" ]]; then
      body="$(tail -n +20 "$agent_src")"
    fi

    cat > "$out" <<AGENT
---
name: ${nice_name}
description: $(grep -m1 '^description:' "$agent_src" | cut -d: -f2- | xargs || echo "Role from agent-bootstrap")
tools: ["Glob", "Grep", "Read", "Bash", "TodoWrite", "WebFetch"]
model: sonnet
color: ${color}
prompt_mode: full
agents_md: true
---

${body}
AGENT
    echo "  ✓ Generated Grok-native ${nice_name}"
  done
  echo "  ✓ Agents generated with Grok frontmatter (plugin mode)"
fi

# Create plugin.json only for actual user/plugin installs (not when refreshing the source repo)
if [[ "$MODE" != "local" && "$TARGET" != "$REPO_ROOT" ]]; then
  mkdir -p "${TARGET}/.claude-plugin"
  cat > "${TARGET}/.claude-plugin/plugin.json" <<JSON
{
  "name": "agent-bootstrap",
  "description": "11 reusable skills and 5 agent roles from the gman-robotics/agent-bootstrap hub. Works with Grok, Claude, and other harnesses.",
  "version": "0.4.0"
}
JSON
  echo "  ✓ plugin.json created"
fi

echo ""
echo "✅  Grok support ready at ${TARGET}"
echo ""
if [[ "$MODE" == "local" ]]; then
  echo "The .grok/ tree in this checkout is now up to date."
else
  echo "Next steps for using in any project:"
  echo "  grok inspect"
  echo "  /plugins trust ${TARGET}"
  echo "  /plan-code-review-workflow"
fi
echo ""
echo "Re-run with --force after updating skills or agents in the canonical locations."