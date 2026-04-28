# Shared Architecture Decision Records (ADRs)

> **Scope**: Cross-project architectural and team-wide decisions.  
> For project-specific decisions, see `docs/projects/<name>/decisions.md`.

---

## ADR Template

Copy this template for each new decision. Assign the next sequential number.

```markdown
## ADR-XXX: <Title>

**Date**: YYYY-MM-DD  
**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-YYY  
**Deciders**: @username, @username  

### Context
What is the problem or situation forcing this decision? What constraints exist?

### Decision
What was decided? Be specific and unambiguous.

### Alternatives Considered
- **Option A**: Brief description — why rejected
- **Option B**: Brief description — why rejected

### Consequences
**Positive:**
- ...

**Negative / Trade-offs:**
- ...

**Risks:**
- ...
```

---

## ADR Index

| # | Title | Status | Date |
|---|---|---|---|
| ADR-001 | Use Markdown + YAML as primary format for agent harness hub | Accepted | 2026-04-28 |
| ADR-002 | Remove wiki layer, use docs/ instead | Accepted | 2026-04-28 |

---

## ADR-001: Use Markdown + YAML as Primary Format for Agent Harness Hub

**Date**: 2026-04-28  
**Status**: Accepted  
**Deciders**: @tginter  

### Context
The agent-bootstrap hub needs to be readable by both humans and AI agent harnesses (Claude Code, Cline, Open Code, etc.). Formats that require build steps, compilers, or special tooling would create barriers to adoption and harness compatibility.

### Decision
Use pure Markdown (`.md`) for all documentation and instructions, and YAML (`.yaml`) for structured configuration (manifest, metadata). No build system, no framework, no runtime required.

### Alternatives Considered
- **JSON**: Machine-readable but poor human readability; no comments.
- **TOML**: Better than JSON but less universal support in harnesses.
- **Notion / Confluence**: Great UX but not version-controlled, not portable, harness-incompatible.
- **HTML/MDX**: Requires a renderer; overkill for this use case.

### Consequences
**Positive:**
- Maximum portability — works in any editor, any harness, any OS.
- No dependencies to install or maintain.
- Version-controlled natively in Git.
- Easy for agents to read, parse, and update.

**Negative / Trade-offs:**
- Limited interactive features (no embedded widgets, no search without tooling).
- Mermaid diagrams require renderer support (most modern tools support this).

**Risks:**
- Low. Pure text is extremely stable.

---

## ADR-002: Remove Wiki Layer, Use `docs/` Instead

**Date**: 2026-04-28  
**Status**: Accepted  
**Deciders**: @tginter  

### Context
The initial hub design included an `llm-wiki/` directory managed by a dedicated wiki skill. During initial setup, this was removed to keep the repo focused. However, this left a gap: no persistent technical reference layer for projects. The `manifest.yaml` still referenced `wiki_sections` (now stale).

### Decision
Replace the wiki concept with a focused `docs/` directory using a two-tier structure:
- `docs/shared/` for team-wide standards
- `docs/projects/<name>/` for per-project technical reference

This is simpler than a full wiki (no index management, no cross-linking complexity) while covering the core need: persistent, version-controlled technical docs accessible to both humans and agents.

### Alternatives Considered
- **Restore the wiki**: More powerful but higher maintenance overhead; agents must manage an index; not KISS.
- **Store everything in memory-bank/**: Wrong layer — memory-bank is operational state, not reference docs. Mixing them creates confusion.
- **External tool (Notion, Confluence)**: Not version-controlled, not portable, not agent-readable.

### Consequences
**Positive:**
- Clear separation of concerns: `docs/` for technical reference, `memory-bank/` for operational state.
- KISS — minimal structure, easy to extend.
- Agents can navigate via `docs_path` in manifest.yaml.

**Negative / Trade-offs:**
- No cross-document linking or search (acceptable for current scale).
- Requires discipline to keep docs vs memory-bank usage clean.

**Risks:**
- Low. Structure is simple and easy to refactor later.

---

*Last updated: 2026-04-28 | Add new ADRs at the bottom; update the index table*
