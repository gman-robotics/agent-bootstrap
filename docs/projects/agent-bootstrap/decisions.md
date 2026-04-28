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
| ADR-005 | Hardcode machine-specific paths as user responsibility | Accepted | 2026-04-28 |

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

## ADR-005: Machine-Specific Paths Are User Responsibility

**Date**: 2026-04-28  
**Status**: Accepted  
**Deciders**: @tginter  

### Context
`AGENTS.md` and `manifest.yaml` contain absolute paths (e.g., `/Users/tginter/dev/gman-robotics/agent-bootstrap`). These are machine-specific and break for other team members.

### Decision
Absolute paths in committed files are acceptable as templates/examples, with clear documentation in `ONBOARDING.md` that each team member must update these paths to match their local setup. The alternative (relative paths) conflicts with the global rule requiring absolute paths for agent reliability.

### Alternatives Considered
- **Relative paths**: Causes agent errors when working directory differs from expectation.
- **Environment variable substitution**: Requires runtime tooling; not KISS.
- **Placeholder tokens (`<REPO_ROOT>`)**: Cleaner but requires find-and-replace setup step.

### Consequences
**Positive:** Works immediately after simple find-and-replace during onboarding.  
**Negative:** Easy to accidentally commit machine-specific paths. Must document clearly.

**Mitigation**: `ONBOARDING.md` step 2 explicitly instructs path update. `.gitignore` can exclude user-specific overrides if needed in future.

---

*Last updated: 2026-04-28 | Add new ADRs at the bottom; update the index table*
