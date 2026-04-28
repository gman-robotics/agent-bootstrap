# Contributing to the Multi-Agent Skills Hub

**Welcome, team member!** 

New to the team? Start with **`ONBOARDING.md`** first.

This repository is our **shared team knowledge base** for:
- Reusable skills and agent roles that improve workflows across all our agent harnesses (Claude Code, Cline, Open Code, etc.).
- Knowledge about our common projects (architecture decisions, patterns, gotchas).
- Persistent context via memory-bank/.

Everything here is designed to be **reused and improved by the whole team**.

## How to Contribute

We use the same workflows the agents use — this keeps quality high and consistent.

### 1. Adding or Improving a Skill
1. **Follow the plan-code-review workflow** (highly recommended for any non-trivial change).
2. Create or edit the skill in `skills/`.
3. Update `AGENTS.md` → "Other Key Skills" section if it's a new core skill.
4. Update relevant memory-bank files if the skill affects project context.
7. Open a Pull Request. Use the **"New Skill"** PR template.

### 2. Adding or Updating an Agent Role
1. Create/edit in `agents/`.
2. Update `AGENTS.md` → "Agents — Reusable Role Definitions".
3. Add usage examples in the relevant skill (e.g., plan-code-review-workflow.md).

### 3. Adding a Common Project to manifest.yaml
1. Add the project with absolute path, description, primary tech, `memory_bank_path`, and `docs_path`.
2. Create the project's `memory-bank/` (copy the 6-file template from this hub's `memory-bank/`).
3. Create the project's `docs/projects/<name>/` directory (copy templates from `docs/projects/agent-bootstrap/`).
4. Update this CONTRIBUTING.md if the process changes.

### 4. Adding or Updating Project Documentation
1. Navigate to `docs/projects/<name>/` (or `docs/shared/` for team-wide standards).
2. Follow the **docs-protocol skill** (`skills/docs-protocol.md`) for creating or updating docs.
3. For architectural decisions: add an ADR to `docs/projects/<name>/decisions.md` (or `docs/shared/decisions.md` for cross-project decisions).
4. Update `memory-bank/techContext.md` if the change is significant.

## Review Process (Mandatory for All Changes)
- All contributions go through **Pull Request**.
- Use the **plan-code-review workflow** internally before opening the PR.
- At least one other team member must review using the **expert-pr-review skill** (or equivalent).
- Merge only after approval (squash + merge preferred).

## Style Guidelines
- **KISS** — Keep it minimal, readable, and actionable.
- Use absolute paths everywhere.
- Friendly, direct, concise tone (match expert-pr-review style).
- Every new skill must be useful to at least 2+ team members.
- No sensitive data (credentials, internal-only info) in any files.

## Questions?
- Ask in the team chat or open an issue with the **"Question / Discussion"** template.
- For urgent changes, tag the current maintainers in the PR.

**Thank you for helping make our agent harnesses and projects better for the whole team!**

*Last updated: 2026-04-28 | Maintained by the team*
