# API Contracts: agent-bootstrap

> This project is a **documentation-only hub** (Markdown + YAML). It has no runtime API.  
> This file documents the "interface contracts" between the hub's components — i.e., the structural agreements that agents and team members rely on.

---

## Interface: AGENTS.md as System Prompt

**Consumer**: Any agent harness (Claude Code, Cline, Open Code, etc.)  
**Provider**: This repository  

### Contract
- `AGENTS.md` MUST be the first file loaded by any agent working in this hub.
- It MUST contain at minimum: Global Rules, Agent Definitions, Skill Index, manifest.yaml reference.
- Its structure (section numbering, headers) MUST NOT change without updating all harness configurations that depend on it.
- Version field in file footer MUST be bumped on any structural change.

### Breaking Changes
- Renaming or removing a top-level section (e.g., "## 2. Global Rules") is a breaking change.
- Changing the agent activation phrase format is a breaking change.
- Removing a skill reference from the "Other Key Skills" list is a breaking change.

---

## Interface: manifest.yaml Schema

**Consumer**: Agents parsing project context  
**Provider**: Team members maintaining the manifest  

### Required Fields Per Project Entry
```yaml
- name: string           # kebab-case, unique identifier
  path: string           # absolute path on local machine
  description: string    # multi-line ok
  primary_tech: string   # comma-separated
  memory_bank_path: string  # absolute path
  docs_path: string      # relative path from repo root, e.g. docs/projects/<name>
```

### Optional Fields
```yaml
  notes: string          # free-form notes for agents
```

### Removed Fields (no longer valid)
```yaml
  wiki_sections: []      # REMOVED — replaced by docs_path (ADR-002)
```

### Breaking Changes
- Removing a required field is a breaking change — all existing entries must be migrated.
- Renaming `name` breaks agent project-switching (agents key on `name`).

---

## Interface: memory-bank/ File Protocol

**Consumer**: Agents (read at session start, write at session end)  
**Provider**: Team members + agents maintaining memory-bank  

### Contract
- Exactly 6 files MUST exist: `projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`, `activeContext.md`, `progress.md`.
- Read order: `projectbrief → productContext → systemPatterns → techContext → activeContext → progress`.
- `activeContext.md` is the most volatile — agents update it every session.
- `progress.md` tracks completion status of all tasks.

See `skills/memory-bank-protocol.md` for the full playbook.

---

## Interface: skills/ Invocation Protocol

**Consumer**: Agents executing workflows  
**Provider**: Skill authors  

### Contract
- Every skill MUST have: a title, numbered steps, clear preconditions, and a completion criteria.
- Skills are invoked by name: `"Follow the expert-pr-review skill"`.
- Skills MUST NOT auto-commit or auto-push (global rule — user explicit confirmation required).
- Skills SHOULD include `> [!WARNING]` blocks for destructive or irreversible steps.

---

## Interface: docs/ Navigation

**Consumer**: Agents and humans looking up technical reference  
**Provider**: Team members maintaining docs  

### Contract
- `docs_path` in `manifest.yaml` points to the project's doc folder: `docs/projects/<name>/`.
- Each project folder SHOULD contain: `api-contracts.md`, `data-models.md`, `pipeline-overview.md`, `decisions.md`.
- `docs/shared/` contains team-wide standards that override project-level defaults where they conflict.

---

*Last updated: 2026-04-28 | Update when component interfaces change*
