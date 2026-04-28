# Agent Bootstrap Hub

**A shared team knowledge base for reusable AI agent roles, workflows (skills), and common projects.**

Stop re-explaining everything to every new agent harness or new team member. Clone once, configure once, and the whole team stays aligned and productive.

## Why This Exists (Team Edition)
- Agent memory resets between sessions/harnesses and between team members.
- Excellent skills and patterns developed by one person should benefit the whole team without re-explaining.
- We work on **common projects** and want consistent context, tech decisions, and history visible to everyone.
- We want standardized **plan → code → critical review → iterate** workflows and clear agent roles across the team.
- We want project and workflow knowledge to **compound** instead of disappearing into Slack threads or individual chats.

This repo solves all of that for the entire team.

## Quick Start

1. Clone this repo to a stable location.
2. Configure your harness to load `AGENTS.md` as the primary instruction file (see AGENTS.md → "How to Use This Repository with Your Harness").
3. (Optional but recommended) Add your projects to `manifest.yaml`.
4. Start working: "Follow the plan-code-review workflow to add feature X to project Y."

That's it. The agent now has:
- Defined roles (Architect, Engineer, QA Reviewer, UI/UX Engineer, ...)
- Standardized workflows (plan-code-review, expert-pr-review, cherry-pick-to-release-branch, memory-bank-protocol, ...)
- Multi-project awareness
- Persistent memory via memory-bank/

## What's Inside

- **AGENTS.md** — The single source of truth. Everything an agent needs to know.
- **CLAUDE.md** — Pointer for Claude-specific harnesses.
- **LICENSE** — MIT License.
- **ONBOARDING.md** — Quick start guide for new team members.
- **manifest.yaml** — Registry of all your projects (paths, tech, memory banks).
- **skills/** — Reusable workflow playbooks:
  - `expert-pr-review.md` — Extremely thorough, safe GitHub PR reviewer (full 8-step flow with security checklist, build/test, inline comments).
  - `cherry-pick-to-release-branch.md` — Safe cherry-pick from merged PR + automatic RC version bump.
  - `plan-code-review-workflow.md` — The core development loop (architect plans with you → engineer codes → qa reviews critically → iterate until approved).
- **agents/** — Role definitions you can activate on demand:
  - `software-architect.md` (Plan mode)
  - `software-engineer.md` (Implementation)
  - `qa-critical-reviewer.md` (Critical QA — reuses expert-pr-review)
  - `ui-ux-engineer.md`
- **memory-bank/** — 6-file continuity system (projectbrief, productContext, systemPatterns, techContext, activeContext, progress). Read at every session start. This project uses it for its own development.
- **docs/** — Persistent technical reference layer (distinct from memory-bank):
  - `docs/shared/` — team-wide standards (API conventions, data types, CI/CD, ADRs)
  - `docs/projects/<name>/` — per-project technical docs (api-contracts, data-models, pipeline-overview, decisions). Keyed to manifest.yaml `name` field.

## Core Philosophy (from Global Rules)

- **KISS** — Minimal, readable, maintainable.
- **Plan first** — Co-create detailed plans with user before significant work. Use Plan mode → Act mode.
- **Memory is truth** — Memory Bank is non-optional.
- **Roles matter** — Switch personas explicitly for better focus.
- **Critical review always** — No code ships without extremely thorough QA (often via the expert-pr-review skill).
- **Knowledge compounds** — Every task ends with updates to `docs/` and `memory-bank/` so knowledge persists and improves over time.
- **Proactive but safe** — Helpful without unnecessary permission asks, but never destructive without confirmation. Never commit/push without explicit instruction.

## Compatibility & Requirements

Works with **any** agent harness that supports custom instructions or persistent context:
- Claude Code / Claude Projects
- Cline, Roo Code, Cursor (via rules)
- Open Code, Open Interpreter, custom MCP setups
- Future harnesses (just point to AGENTS.md)

**MCP Server Dependencies:**
Several advanced skills in this hub (like `expert-pr-review` and `cherry-pick-to-release-branch`) require a working GitHub MCP server (`@modelcontextprotocol/server-github`) configured with a valid token to perform deep PR analysis and interaction.

No code changes needed in the harness — pure documentation + your existing tools.

## Contributing / Extending

- Add a new agent: Copy `agents/software-architect.md` template, fill in persona + behaviors.
- Add a new skill: Follow the detailed step-by-step + warnings + examples style of `expert-pr-review.md`.
- Update skills and agents using the existing contribution process.
- Add your project: Edit `manifest.yaml` with absolute path + `memory_bank_path` + `docs_path`. Create `docs/projects/<name>/` using templates from `docs/projects/agent-bootstrap/`.

All changes to this repo itself should follow the plan-code-review workflow (self-hosting).

## Status

Initial v0.1.0 — Core files, skills, agents, and wiki structure in place. Fully functional for immediate use.

See `memory-bank/progress.md` for current task status.

---

*Built to make AI coding agents consistently excellent across every session and every project.*