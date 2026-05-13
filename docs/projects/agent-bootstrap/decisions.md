# Architecture Decision Records: agent-bootstrap

> Project-specific decisions for the agent-bootstrap hub itself.  
> Cross-project and team-wide decisions are in `docs/shared/decisions.md`.

---

## ADR Index

| # | Title | Status | Date |
|---|---|---|---|
| ADR-001 | Use 6-file memory-bank structure for session continuity | Accepted | 2026-04-28 |
| ADR-002 | Include skills verbatim in /skills/ (self-contained) | Accepted | 2026-04-28 |
| ADR-003 | Remove wiki layer; use docs/ for technical reference | Accepted | 2026-04-28 |
| ADR-004 | Four initial agent roles (Architect, Engineer, QA, UI/UX) | Accepted | 2026-04-28 |
| ADR-005 | Use relative paths in manifest.yaml for team shareability | Accepted | 2026-05-13 |

---

## ADR-001: Use 6-File Memory-Bank Structure for Session Continuity

**Date**: 2026-04-28  
**Status**: Accepted  
**Deciders**: @tginter  

### Context
AI agent harnesses lose all memory between sessions. Without a persistent context mechanism, every session starts from zero — forcing repetitive re-explanation of project state, active decisions, and progress.

### Decision
Adopt a 6-file `memory-bank/` structure (projectbrief, productContext, systemPatterns, techContext, activeContext, progress) as the mandatory session-start read protocol for all agents working in this hub or any project registered in `manifest.yaml`.

### Alternatives Considered
- **Rely on conversation history**: Not available across sessions or harnesses.
- **External database / vector store**: Heavy infrastructure for a docs-only repo; harness-dependent.
- **Single large context file**: Hard to maintain, hard to parse, grows unbounded.

### Consequences
**Positive:**
- Zero session-to-session context loss.
- Harness-agnostic — any tool that can read files works.
- Structured hierarchy makes it easy to read specific sections quickly.

**Negative / Trade-offs:**
- Agents must be instructed to read all 6 files at session start (non-optional).
- Memory-bank files can become stale if contributors skip the update step.

---

## ADR-002: Include Skills Verbatim in `/skills/` (Self-Contained)

**Date**: 2026-04-28  
**Status**: Accepted  
**Deciders**: @tginter  

### Context
Initial design considered referencing external skill sources (uploaded files, external URLs). For a published GitHub repo used by a team, all content must be self-contained and version-controlled.

### Decision
All skills (`expert-pr-review.md`, `cherry-pick-to-release-branch.md`, etc.) are stored verbatim in `/skills/` within this repo. No external references or dependencies.

### Consequences
**Positive:**
- Fully self-contained — clone and use immediately.
- Version-controlled — skill changes are tracked in Git history.
- Team can contribute improvements via PR.

**Negative / Trade-offs:**
- Skills must be manually updated if the original source improves.
- Duplication if skills exist elsewhere (acceptable — canonical copy lives here).

---

## ADR-003: Remove Wiki Layer; Use `docs/` for Technical Reference

**Date**: 2026-04-28  
**Status**: Accepted  
**Deciders**: @tginter  

### Context
The initial design included an `llm-wiki/` directory with an index and cross-linked pages managed by an `llm-wiki` skill. During initial setup, this was removed to reduce scope. However, this left a gap: no persistent technical reference layer. The `manifest.yaml` `wiki_sections` field became stale.

### Decision
Introduce a focused `docs/` directory:
- `docs/shared/` — team-wide standards
- `docs/projects/<name>/` — per-project technical reference (api-contracts, data-models, pipeline-overview, decisions)
- `manifest.yaml` gains `docs_path` field, replacing the removed `wiki_sections` field.
- New skill `skills/docs-protocol.md` governs how agents create and update docs.

### Consequences
**Positive:** Fills the documentation gap. KISS. Agents can navigate via `docs_path`.  
**Negative:** No cross-linking or search (acceptable for current scale).

---

## ADR-004: Four Initial Agent Roles

**Date**: 2026-04-28  
**Status**: Accepted  
**Deciders**: @tginter  

### Context
The hub needs a minimal but complete set of agent personas to cover the core development lifecycle without over-engineering.

### Decision
Start with exactly four roles:
1. `software-architect.md` — planning and co-creation (Plan mode)
2. `software-engineer.md` — implementation (Act mode)
3. `qa-critical-reviewer.md` — code review and PR review (uses expert-pr-review)
4. `ui-ux-engineer.md` — frontend and UX work

Additional roles (security-auditor, devops-engineer, technical-writer) follow the same template when needed.

### Consequences
**Positive:** Covers the full plan → code → review lifecycle. Easy to extend.  
**Negative:** UI/UX role may be rarely used for this docs-only repo (but valuable for real projects).

---

## ADR-005: Use Relative Paths in manifest.yaml for Team Shareability

**Date**: 2026-05-13  
**Status**: Accepted  
**Deciders**: @tginter  

### Context
The original ADR-005 (2026-04-28) chose absolute paths + gitignore as the solution to machine-specific paths. This required every team member to copy `manifest.template.yaml`, run a find-and-replace, and keep their `manifest.yaml` out of git. This was friction with no real benefit given the team's standard checkout layout.

### Decision
`manifest.yaml` uses **relative paths** (e.g., `../my-app`, `./memory-bank`) resolved against the directory containing `manifest.yaml`. All repos are cloned as siblings under one parent — so `../my-app` works identically on every developer's machine regardless of where the parent directory lives. `manifest.yaml` is committed and shared; no per-machine setup required.

The global rule "always use absolute paths" applies to **agent file operations** (tool calls, skill steps), not to manifest configuration. Agents must resolve manifest paths to absolute paths before use.

### Alternatives Considered
- **Absolute paths + gitignore (original ADR-005)**: Required per-machine setup step; easy to forget; prevented sharing `manifest.yaml` in git.
- **Environment variable substitution (`$HOME/dev/...`)**: Requires shell expansion at read time; not supported by YAML parsers without extra tooling.

### Consequences
**Positive:** `manifest.yaml` works for the whole team out of the box. No onboarding step needed. No risk of accidentally committing machine paths.  
**Negative:** Assumes sibling checkout layout. Teams with non-standard layouts use `manifest.template.yaml` + local absolute-path override (documented in `ONBOARDING.md`).

---

---

*Last updated: 2026-05-13 | Add new ADRs at the bottom; update the index table*
