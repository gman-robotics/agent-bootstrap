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
| ADR-003 | Red/Green/Refactor TDD as mandatory development methodology | Accepted | 2026-04-30 |

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

## ADR-003: Red/Green/Refactor TDD as Mandatory Development Methodology

**Date**: 2026-04-30  
**Status**: Accepted  
**Deciders**: @tginter  

### Context
Agent-assisted development moves fast but produces code that lacks test coverage unless the process explicitly enforces it. Without a clear standard, different team members and different agents apply wildly inconsistent testing discipline — some write tests after the fact, some skip them entirely for "small" changes, and some write tests that only cover happy paths. Regressions accumulate.

### Decision
Red/Green/Refactor TDD is the mandatory development methodology for all non-trivial logic across all projects. Agents enforce this during code review: new logic without a failing test written first is a blocking issue. The full standard lives in `docs/shared/tdd-standard.md`. The operational skill lives in `skills/write-tests/SKILL.md`.

### Alternatives Considered
- **Test-after (write code, then tests)**: Easier to skip under time pressure; tests tend to mirror implementation rather than specify behavior; does not catch design problems early.
- **Coverage thresholds only**: Coverage is gameable and does not enforce behavioral test quality. A 100% coverage suite with tautological assertions is worse than 60% with meaningful ones.
- **Optional / team-discretion**: Results in no consistent standard; harder to enforce in code review; agent behavior becomes unpredictable.

### Consequences
**Positive:**
- Every bug fix ships with a regression test by definition.
- Design problems surface early (untestable code is a design smell).
- Agent code review has a concrete, enforceable checklist item.
- New team members have an unambiguous process to follow.

**Negative / Trade-offs:**
- Slower for trivial changes where the test feels like ceremony.
- Requires discipline for agents to actually write the failing test first rather than the code first.

**Mitigations:**
- `docs/shared/tdd-standard.md` explicitly lists when TDD may be skipped (glue code, one-off scripts, pure layout).
- Exceptions must be noted in the PR description; repeated exceptions should result in an ADR update.

---

*Last updated: 2026-04-30 | Add new ADRs at the bottom; update the index table*
