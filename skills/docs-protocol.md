# Skill: docs-protocol

**Purpose**: Governs how agents create, update, and reference technical documentation in the `docs/` directory. Use this skill whenever you need to write or update project technical docs (API contracts, data models, pipeline, decisions).

**Invoke with**: "Follow the docs-protocol skill to [create/update] docs for [project]"

---

> **IMPORTANT**: `docs/` is the **technical reference layer** — not the operational state layer.  
> - Use `docs/` for: API contracts, schemas, ADRs, pipeline configs, long-lived technical facts.  
> - Use `memory-bank/` for: current session focus, active decisions, task progress.  
> Never mix these two layers.

---

## Preconditions

- [ ] The project exists in `manifest.yaml` with a `docs_path` field.
- [ ] You know which document type you're creating/updating (api-contracts, data-models, pipeline-overview, decisions).
- [ ] For ADRs: You have a clear context, decision, and at least one rejected alternative.

---

## Step 1 — Locate the Correct Doc

1. Read `manifest.yaml` to find the project's `docs_path`.
2. Navigate to that path: `docs/projects/<name>/` for project-specific docs, or `docs/shared/` for team-wide standards.
3. If the file doesn't exist yet, proceed to Step 2 (Create). If it exists, proceed to Step 3 (Update).

---

## Step 2 — Create New Doc File

1. Copy the structure from the equivalent file in `docs/projects/agent-bootstrap/` as your template.
2. Replace all placeholder content with project-specific information.
3. Always include the scope disclaimer at the top:
   ```markdown
   > **Scope**: [What this covers and what it doesn't].  
   > For [broader/narrower scope], see [link to shared/ or project file].
   ```
4. Add the footer:
   ```markdown
   *Last updated: YYYY-MM-DD | Update when [specific trigger condition]*
   ```
5. Save to the correct path (absolute path).

---

## Step 3 — Update Existing Doc

### For api-contracts.md / data-models.md / pipeline-overview.md

1. Read the entire file first — understand existing structure before changing anything.
2. Add new content in the appropriate section. Do not duplicate existing content.
3. If updating existing content (e.g., changing a field type): mark the old value with a strikethrough comment or remove it cleanly — never leave contradictory information.
4. Update the `Last updated` footer.

### For decisions.md (ADRs)

Use this sub-flow for every Architecture Decision Record:

1. **Assign the next ADR number** — read the index table, increment by 1.
2. **Add to the index table** — add a row with: number, title, "Proposed" status, today's date.
3. **Write the ADR body** using this structure:
   ```markdown
   ## ADR-XXX: <Title>

   **Date**: YYYY-MM-DD  
   **Status**: Proposed | Accepted | Deprecated | Superseded by ADR-YYY  
   **Deciders**: @username  

   ### Context
   [Problem, constraints, what forced this decision]

   ### Decision
   [What was decided — specific and unambiguous]

   ### Alternatives Considered
   - **Option A**: description — why rejected
   - **Option B**: description — why rejected

   ### Consequences
   **Positive:**
   - ...

   **Negative / Trade-offs:**
   - ...

   **Risks:**
   - ...
   ```
4. **Place at the bottom** of the file (new ADRs always append — never reorder existing ADRs).
5. **Update status** from "Proposed" to "Accepted" (or other) once the decision is confirmed by the team.

> **When to supersede an ADR**: If a new decision overturns an old one, do NOT delete the old ADR. Set its status to "Superseded by ADR-YYY" and reference the new ADR.

---

## Step 4 — Update Cross-References

After creating or significantly updating a doc:

1. **manifest.yaml**: Ensure `docs_path` is set for this project.
2. **memory-bank/techContext.md**: Reference the doc path if it's a new project doc setup.
3. **memory-bank/systemPatterns.md**: Reference if it changes architectural understanding.
4. **AGENTS.md**: If a new doc type or protocol was added, update the "Project Documentation" section.

---

## Step 5 — Verify

1. Re-read the file you just created/updated. Check:
   - No contradictions with `docs/shared/` (project docs override shared only where intentional and documented).
   - Correct scope disclaimer present.
   - Footer updated.
   - ADR index table matches ADR body sections.
2. If creating a new project's doc folder: confirm all 4 files exist (`api-contracts.md`, `data-models.md`, `pipeline-overview.md`, `decisions.md`).

---

## When to Use Each Doc Type

| Question | Document |
|---|---|
| "What does this endpoint expect/return?" | `api-contracts.md` |
| "What fields does this entity have?" | `data-models.md` |
| "How does our CI/CD work? How do we deploy?" | `pipeline-overview.md` |
| "Why did we choose X over Y?" | `decisions.md` (ADR) |
| "What is the team-wide standard for field naming?" | `docs/shared/api-contracts.md` |
| "What are we currently working on?" | `memory-bank/activeContext.md` (NOT docs/) |

---

## Shared vs Project Docs

| If it applies to... | Write to... |
|---|---|
| All projects (team-wide standard) | `docs/shared/<type>.md` |
| One specific project | `docs/projects/<name>/<type>.md` |
| A decision for this project | `docs/projects/<name>/decisions.md` |
| A cross-project architectural decision | `docs/shared/decisions.md` |

**When there's a conflict**: Project-level docs override shared/ for that project, but the override should be documented (e.g., "We use cursor-based pagination instead of the shared page/limit standard — see ADR-XXX").

---

## Quick Reference: Adding a New Project's Docs

```
1. Add to manifest.yaml:
   docs_path: docs/projects/<name>

2. Create directory:
   mkdir -p docs/projects/<name>

3. Create 4 files:
   - docs/projects/<name>/api-contracts.md
   - docs/projects/<name>/data-models.md
   - docs/projects/<name>/pipeline-overview.md
   - docs/projects/<name>/decisions.md

4. Use docs/projects/agent-bootstrap/ files as templates.

5. Fill in what you know; leave N/A for unknowns.

6. Reference docs_path from the project's memory-bank/techContext.md.
```

---

*Last updated: 2026-04-28 | Skill version: 1.0.0*
