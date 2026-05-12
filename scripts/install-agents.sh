#!/usr/bin/env bash
# install-agents.sh — Symlink all agents/*.md into ~/.claude/agents/
# so Claude Code's global agent scan path resolves the named agents.
#
# Usage:  bash scripts/install-agents.sh
# Safe to re-run: existing symlinks are overwritten with -sf.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_SRC="${REPO_ROOT}/agents"
CLAUDE_AGENTS_DIR="${HOME}/.claude/agents"

echo "→ Source:      ${AGENTS_SRC}"
echo "→ Destination: ${CLAUDE_AGENTS_DIR}"
echo ""

mkdir -p "${CLAUDE_AGENTS_DIR}"

installed=0
for agent_file in "${AGENTS_SRC}"/*.md; do
  filename="$(basename "${agent_file}")"
  target="${CLAUDE_AGENTS_DIR}/${filename}"
  ln -sf "${agent_file}" "${target}"
  echo "  ✓  ${filename}"
  ((installed++))
done

echo ""
echo "✅  ${installed} agent(s) symlinked to ${CLAUDE_AGENTS_DIR}"
echo ""
echo "Agents are now available in Claude Code via Task(subagent_type=\"<Name>\")."
echo "Re-run this script after adding new agents/*.md files."
