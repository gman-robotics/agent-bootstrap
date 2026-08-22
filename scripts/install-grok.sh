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

# Resolve . / trailing slashes / symlinks so TARGET==REPO_ROOT is a real directory
# compare, not a string compare. Plugin mode against the hub checkout would export
# into committed skills/ and --force could rmtree extra references/ with no copy-back.
canonical_path() {
  python3 -c 'import os, sys; print(os.path.realpath(os.path.expanduser(sys.argv[1])))' "$1"
}

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

REPO_ROOT="$(canonical_path "$REPO_ROOT")"
TARGET="$(canonical_path "$TARGET")"

# --local refreshes the committed project tree (.grok/skills, discovered when
# this repo is the cwd). Plugin / user installs use Grok's plugin layout:
#   <plugin>/skills/  <plugin>/agents/  .grok-plugin/plugin.json
# Nested <plugin>/.grok/skills is invisible to `grok plugin validate`.
if [[ "$MODE" == "local" || "$TARGET" == "$REPO_ROOT" ]]; then
  SKILLS_DIR="${TARGET}/.grok/skills"
  AGENTS_DIR="${TARGET}/.grok/agents"
  PLUGIN_MODE=0
  MODE="local"
else
  SKILLS_DIR="${TARGET}/skills"
  AGENTS_DIR="${TARGET}/agents"
  PLUGIN_MODE=1
fi

echo "→ Mode:   ${MODE}"
echo "→ Target: ${TARGET}"
echo "→ Layout: $([[ "$PLUGIN_MODE" -eq 1 ]] && echo plugin || echo local)"
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

# export --force rmtree's each skill dir and only regenerates references/source.md.
# Copy any other canonical reference files the exporter does not emit.
echo "→ Restoring extra skill references ..."
for skill_src in "${REPO_ROOT}/skills"/*/; do
  [[ -d "${skill_src}/references" ]] || continue
  skill_name="$(basename "${skill_src}")"
  dest_ref="${SKILLS_DIR}/${skill_name}/references"
  mkdir -p "${dest_ref}"
  for ref in "${skill_src}/references"/*; do
    [[ -f "$ref" ]] || continue
    base="$(basename "$ref")"
    [[ "$base" == "source.md" ]] && continue
    cp "$ref" "${dest_ref}/${base}"
    echo "  ✓ Restored ${skill_name}/references/${base}"
  done
done

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

if [[ "$PLUGIN_MODE" -eq 0 ]]; then
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
if [[ "$PLUGIN_MODE" -eq 1 ]]; then
  skill_count="$(find "${SKILLS_DIR}" -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')"
  agent_count="$(find "${AGENTS_DIR}" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"
  plugin_json="$(cat <<JSON
{
  "name": "agent-bootstrap",
  "description": "${skill_count} reusable skills and ${agent_count} agent roles from the gman-robotics/agent-bootstrap hub. Works with Grok, Claude, and other harnesses.",
  "version": "0.6.0"
}
JSON
)"
  mkdir -p "${TARGET}/.grok-plugin" "${TARGET}/.claude-plugin"
  printf '%s\n' "${plugin_json}" > "${TARGET}/.grok-plugin/plugin.json"
  printf '%s\n' "${plugin_json}" > "${TARGET}/.claude-plugin/plugin.json"
  echo "  ✓ plugin.json created (${skill_count} skills, ${agent_count} agents)"
  # Stale nested layout from older install-grok.sh must not linger beside the
  # plugin-root skills/ agents/ Grok actually scans. Never touch the hub's
  # committed .grok/ even if mode detection were wrong.
  if [[ $FORCE -eq 1 && -d "${TARGET}/.grok" && "$TARGET" != "$REPO_ROOT" ]]; then
    rm -rf "${TARGET}/.grok"
    echo "  ✓ Removed leftover ${TARGET}/.grok (pre-plugin layout)"
  fi
fi

echo ""
echo "✅  Grok support ready at ${TARGET}"
echo ""
if [[ "$MODE" == "local" ]]; then
  echo "The .grok/ tree in this checkout is now up to date."
else
  echo "Next steps for using in any project:"
  echo "  grok plugin install --trust ${TARGET}"
  echo "  grok plugin validate ${TARGET}"
  echo "  grok inspect"
  echo "  /plan-code-review-workflow"
fi
echo ""
echo "Re-run with --force after updating skills or agents in the canonical locations."