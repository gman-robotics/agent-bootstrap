# Mem0 Lessons Plan for agent-bootstrap

> **Scope**: This document captures Mem0-inspired ideas that can strengthen `agent-bootstrap` while keeping the hub local-first, repository-backed, and safe for work-computer use. It does not propose adopting hosted Mem0, installing remote memory MCP services, or adding automatic prompt capture.

## Context

Mem0 is a persistent memory layer for AI agents. Its most relevant design ideas for `agent-bootstrap` are not the hosted service or vector database, but the workflow patterns around memory recall, typed memory writes, lifecycle hooks, and plugin packaging.

`agent-bootstrap` already has a strong local foundation:

- `AGENTS.md` as the harness-agnostic source of truth.
- `manifest.yaml` as the project registry.
- `skills/` as reusable workflow definitions.
- `memory-bank/` as the six-file operational memory layer.
- `docs/` as the long-lived technical reference layer.
- `scripts/export_codex_skills.py` for exporting repo skills into Codex global skill folders.

The plan below keeps that model intact. The goal is to improve recall quality and onboarding ergonomics without introducing a third-party memory service into the development workflow.

## Goals

- Make local memory recall more deliberate and less dependent on reading every file for every task.
- Give memory entries stable types so agents can search for decisions, conventions, failed approaches, and preferences separately.
- Add optional lifecycle reminders for Codex, Claude Code, Cursor, and similar harnesses.
- Package `agent-bootstrap` as an installable plugin-style bundle where supported.
- Preserve the current security posture: local files first, no automatic remote persistence, no hidden prompt capture.

## Non-Goals

- Do not integrate the hosted Mem0 platform by default.
- Do not run the self-hosted Mem0 REST server as part of `agent-bootstrap`.
- Do not require vector search, embeddings, Postgres, or additional services.
- Do not silently write memories on every prompt.
- Do not replace the six-file memory-bank protocol.

## Lessons to Reuse

### 1. Memory Recall Rubric

Mem0's strongest workflow idea is a decision rubric for when to search memory. `agent-bootstrap` should adapt this into a local-file protocol.

Search local memory when the user:

- References prior work, decisions, or things "we" built.
- Asks a decision-style question such as "how should we..." or "what is the best way...".
- Reports a bug, flaky test, regression, or confusing environment behavior.
- Starts non-trivial work in a known project.
- Touches team conventions, user preferences, architecture, or workflow policy.

Skip memory search when:

- The prompt is a trivial acknowledgement or continuation.
- The user is only stating new information that should be written later.
- The task is a simple syntax or general-knowledge question.
- The relevant memory has already been searched during the same turn.

### 2. Typed Memory Entries

Mem0 uses explicit metadata types for filtering. `agent-bootstrap` can use the same concept in Markdown without a database.

Recommended memory types:

| Type | Use For | Default Location |
|---|---|---|
| `decision` | Architecture, workflow, and tooling choices | `docs/**/decisions.md` or `memory-bank/progress.md` summary |
| `convention` | Naming, style, branch, testing, and review norms | `memory-bank/systemPatterns.md`, `docs/shared/` |
| `anti_pattern` | Failed approaches, recurring mistakes, known traps | `memory-bank/progress.md` |
| `task_learning` | Useful task-specific strategies and fixes | `memory-bank/progress.md` |
| `environmental` | Local setup, dependency, CI, or deployment discoveries | `memory-bank/techContext.md` |
| `user_preference` | Stated preferences for tools, process, and defaults | `memory-bank/activeContext.md` or shared memory layer |
| `session_state` | Temporary current-state snapshots | `memory-bank/activeContext.md` |

For new entries, prefer a compact structured block:

```markdown
### 2026-05-14 - Short descriptive title

type: decision
scope: agent-bootstrap
status: active

- Decision or learning in one or more specific bullets.
- Include file paths, commands, PR links, or error text when useful for future search.
```

### 3. Multi-Angle Local Search

Instead of one broad search, agents should run two to four targeted local searches across the active project and bootstrap docs.

Example for an auth refactor:

```bash
rg -n "auth|JWT|token" /absolute/path/to/project/memory-bank /absolute/path/to/agent-bootstrap/docs
rg -n "type: decision|ADR-.*auth|auth.*decision" /absolute/path/to/project /absolute/path/to/agent-bootstrap/docs
rg -n "type: anti_pattern|auth.*failed|JWT.*failed" /absolute/path/to/project/memory-bank
rg -n "type: user_preference|auth.*preference|security.*preference" /absolute/path/to/agent-bootstrap/memory-bank
```

This keeps the current transparent file-backed model while gaining some of the practical recall benefits that semantic memory systems aim to provide.

### 4. Lifecycle Reminders

Mem0's hook model is worth adapting as optional local reminders.

Proposed hook behavior:

| Event | Local agent-bootstrap Behavior |
|---|---|
| `SessionStart` | Remind the agent to load `AGENTS.md`, `manifest.yaml`, and the relevant memory-bank files. |
| `UserPromptSubmit` | Inject a short rubric asking whether local memory search would help. |
| `Stop` | Remind the agent to update `activeContext.md` and `progress.md` if durable learning occurred. |

These hooks should be opt-in, idempotent, and uninstallable. They should not make network calls or write memory automatically.

### 5. Plugin Packaging

Mem0 packages MCP configuration, skills, hooks, and metadata as a plugin. `agent-bootstrap` can follow that packaging pattern without adopting Mem0's backend.

Candidate files:

```text
.codex-plugin/plugin.json
.agents/plugins/marketplace.json
hooks/codex-hooks.json
scripts/install-codex-hooks.py
scripts/search-memory.sh
scripts/export_codex_skills.py
```

The initial plugin should expose the existing skills and optional hooks. MCP should remain out of scope unless a future local-only MCP server becomes useful.

## Proposed Implementation Plan

### Phase 1 - Local Recall Protocol

Deliverables:

- Add `skills/context-recall-protocol/SKILL.md`.
- Update `skills/INDEX.md` to include the new skill and trigger conditions.
- Add examples for multi-angle `rg` searches using `manifest.yaml` and project memory-bank paths.
- Clarify how this protocol complements, rather than replaces, `memory-bank-protocol.md`.

Acceptance criteria:

- The new skill tells agents when to search, when to skip, what to search, and how to summarize results.
- The protocol is fully local-file based.
- No external services or new dependencies are required.

### Phase 2 - Typed Memory Convention

Deliverables:

- Update `skills/memory-bank-protocol/SKILL.md` with the recommended `type`, `scope`, and `status` block format.
- Add guidance for durable vs temporary memory.
- Add examples to the hub `memory-bank/` files or a dedicated template section.

Acceptance criteria:

- Existing memory-bank files remain valid.
- New entries can be searched by `type:` using `rg`.
- The docs still preserve the `memory-bank/` vs `docs/` separation.

### Phase 3 - Search Helper Script

Deliverables:

- Add `scripts/search-memory.sh`.
- Support searching a named manifest project plus bootstrap docs.
- Keep output concise enough to paste into an agent context.

Candidate interface:

```bash
scripts/search-memory.sh agent-bootstrap "plugin packaging"
scripts/search-memory.sh guru-robotics "docutext desired_count"
scripts/search-memory.sh --type decision agent-bootstrap "relative paths"
```

Acceptance criteria:

- Resolves project paths from `manifest.yaml`.
- Searches project memory-bank, project docs, shared docs, and bootstrap memory-bank.
- Fails clearly when a project is not in the manifest.
- Does not require Python packages beyond the standard library if implemented in Python, or external tools beyond `rg` if implemented as shell.

### Phase 4 - Optional Hook Installer

Deliverables:

- Add `hooks/codex-hooks.json`.
- Add `scripts/install-codex-hooks.py`.
- Support install and uninstall.
- Preserve existing user hooks.

Acceptance criteria:

- Hooks only inject reminders.
- Hooks do not send data over the network.
- Hooks do not mutate memory-bank files automatically.
- Re-running the installer is idempotent.

### Phase 5 - Codex Plugin Packaging

Deliverables:

- Add `.codex-plugin/plugin.json`.
- Add `.agents/plugins/marketplace.json` if needed for local plugin registration.
- Ensure exported skills work cleanly from the plugin.
- Document install and uninstall steps in `README.md` or `ONBOARDING.md`.

Acceptance criteria:

- A developer can install the bootstrap plugin locally.
- Skills load through the plugin without copying instructions manually.
- Hooks remain optional and documented separately from skill installation.

## Security Requirements

- Default behavior must be local-only.
- No hosted memory service should be configured by default.
- No hook should capture or persist raw prompts automatically.
- Hook scripts must be small, auditable, and deterministic.
- Any future MCP server should be local-only by default and explicitly documented before use.
- Generated plugin config must avoid embedding secrets.

## Open Questions

- Should typed memory blocks be added directly to existing six memory-bank files, or should each project get an optional `memory-bank/index.md` for searchable entries?
- Should `scripts/search-memory.sh` be shell-only, or should it be a Python script for safer YAML parsing?
- Should hook installation target only Codex first, then Claude/Cursor later?
- Should plugin packaging be a separate release milestone after local recall proves useful?

## Recommended Next Step

Start with Phase 1 and Phase 2 only. They are low-risk, improve current workflows immediately, and preserve the existing file-backed architecture. Defer hooks and plugin packaging until the local recall convention is proven useful in normal project work.

*Last updated: 2026-05-14 | Update when the local recall protocol, typed memory convention, hooks, or plugin packaging plan changes*
