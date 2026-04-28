# Tech Context: Multi-Agent Skills Hub

## Technologies & Stack
- **Primary Artifacts**: Markdown (.md), YAML (.yaml), Mermaid diagrams (embedded in MD).
- **No Primary Language**: Designed to be language-agnostic. Skills can reference any tech (e.g., the cherry-pick skill assumes Node.js/npm package.json but is generalized).
- **Agent Harness Integration**:
  - Claude Code / Claude Projects: Set custom instructions to AGENTS.md content or file path.
  - Cline / Roo Code: Use .clinerules or workspace rules pointing to AGENTS.md + agents.
  - Open Code / Other: Similar, load root AGENTS.md as system prompt or persistent context.
- **Tools Used by Agents** (when in harness):
  - File system: read_file, write_file, edit_file, bash (for git, npm, etc. but only as instructed by skills).
  - GitHub: gh CLI, MCP GitHub tools (for PR skills).
  - No build system required for the hub itself (it's docs).

## Development Setup (for this repo)
- Clone to any location.
- For local editing: any Markdown editor with preview (Obsidian, Typora, VS Code + Markdown extensions recommended for wiki linking).
- To "run" a skill: Agent reads the .md and follows steps exactly, using its available tools (bash, file ops, etc.).
- Testing a skill: User invokes "Use the expert-pr-review skill on PR #123 in repo X" — agent executes the full flow.

## Constraints & Conventions
- **Absolute Paths Only**: All file references in instructions and skills use full paths (e.g., /home/workdir/artifacts/...). This matches global rule 5 and prevents path errors in different harness sandboxes.
- **Non-Interactive Commands**: All bash in skills must use flags for no user input (e.g., `git cherry-pick --continue` not interactive).
- **Memory Bank Protocol**: Every significant task starts with:
  1. Read all 6 core memory-bank/*.md files (in order: projectbrief, productContext, systemPatterns, techContext, activeContext, progress).
  2. Update activeContext.md and progress.md at end.
- **KISS Principle**: Keep files small, instructions concise, no unnecessary nesting. Prefer flat structures.
- **Self-Review**: Before finalizing any change to this repo's files, the QA agent (or self) must review per expert-pr-review checklist.
- **No Version Control Commits**: This repo's files are created/edited by agent, but git commit only on explicit user instruction (global rule).

## Dependencies
- None at runtime (pure text).
- For skills that interact with real projects: assumes gh, git, node/npm, etc. are available in the harness environment (as in user's setup).
- Wiki may use Mermaid for diagrams (supported in most Markdown renderers and Claude artifacts).

## Conventions
- File naming: kebab-case.md for skills and agents.
- Headers: Use ## for sections, **bold** for key terms, > for warnings, code blocks for commands.
- Tone: Friendly, direct, concise, actionable (match the expert-pr-review and global rule styles in this hub).
- Updates: After any edit to core files, re-read to verify (global rule 8).
