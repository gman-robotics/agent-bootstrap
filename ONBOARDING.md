# Team Onboarding — Agent Bootstrap Hub

**Welcome to the team!** This guide will help you get productive with our shared agent harness workflows quickly.

## Quick Start (First 20 Minutes)

1. **Clone only this repo** to a stable parent directory:
   ```bash
   mkdir -p ~/dev/my-org && cd ~/dev/my-org
   git clone https://github.com/your-org/agent-bootstrap.git agent-bootstrap
   ```
2. **Let your agent clone the rest.** Open your preferred harness, point it at this repo, and say:
   > "Clone any repos from manifest.yaml that are missing on disk."

   The agent reads `manifest.yaml`, checks each project's `path`, and runs `git clone <git_url> <path>` for any that are absent. All repos land as siblings of `agent-bootstrap/` automatically.

   > If your repos live in non-standard locations, copy `manifest.template.yaml` to a local `manifest.yaml`, fill in absolute paths, and add `manifest.yaml` to your `.gitignore`.

3. **Read `AGENTS.md`** (the single source of truth). This is the most important file.
4. **Read the 6 files in `memory-bank/`** for this hub (especially `projectbrief.md` and `activeContext.md`).
5. **Explore `skills/` and `agents/`** to understand what reusable workflows and roles are available.
6. **Configure your harness** to load `AGENTS.md` (see `AGENTS.md` → "How to Use This Repository with Your Harness" for per-harness instructions).
7. **Claude Code users only — install agents globally:**
   ```bash
   bash scripts/install-agents.sh
   ```
   This symlinks every `agents/*.md` file into `~/.claude/agents/` so Claude Code can resolve agents by name when using `Task(subagent_type="...")`. Safe to re-run after adding new agents. For full delegation patterns, see `skills/delegation-patterns/SKILL.md`.

**Grok users**: No install step required. The `.grok/skills/` and `.grok/agents/` directories (plus AGENTS.md project-rules) are discovered automatically the moment you open the repo in Grok. Skills appear as `/<name>`; roles are available to the `task` tool.

## Environment Prerequisites (MCP)

Many of the advanced agent skills (like `expert-pr-review` and `cherry-pick-to-release-branch`) require specific Model Context Protocol (MCP) servers to function correctly. Ensure your IDE or agent harness has the following MCP servers configured:
- **GitHub MCP Server** (`@modelcontextprotocol/server-github`): Required for PR reviews, fetching PR commits, inline commenting, etc. Ensure it is authenticated with a valid GitHub token.
- *(Optional)* Additional servers for local shell commands or directory reads depending on your specific agent harness.

## Key Concepts

- **AGENTS.md** — The single source of truth. Every agent loads this first.
- **memory-bank/** — Persistent context for projects. Read all 6 files at the start of every session.
- **skills/** — Reusable playbooks (e.g. `expert-pr-review.md`, `plan-code-review-workflow.md`).
- **agents/** — Reusable role definitions you can "become" (Architect, Engineer, QA Reviewer, etc.).
- **manifest.yaml** — Registry of all our common projects so agents instantly know context.

## First Tasks to Try

1. Run the **plan-code-review workflow** on a small, real task.
2. Use the **expert-pr-review skill** on one of your recent PRs.
3. Add one of your active projects to `manifest.yaml` and create its `memory-bank/`.

## Team Norms

- Always follow the **plan-code-review workflow** for non-trivial work.
- Update `memory-bank/progress.md` after significant tasks.
- Use absolute paths in all instructions and skills.
- Contribute improvements back to `skills/` and `agents/` so the whole team benefits.

## Common Questions

**"How do I switch to a different project?"**  
Say: "Switch to project 'my-app' per manifest.yaml"

**"I built a useful new pattern/skill. Where does it go?"**  
Add it to `skills/` and follow the process in `CONTRIBUTING.md`.

**"I'm stuck or confused."**  
Re-read `AGENTS.md` section 2 (Global Rules) — it usually has the answer.

## Next Steps After Onboarding

- Start using the hub on your daily work.
- Contribute your first improvement (even a small one).
- Help improve the onboarding experience for the next new team member.

**We're building this together — your feedback and contributions make everyone's work better.**

*Maintained by the team | Last updated: 2026-05-13*