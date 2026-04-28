# Data Models: agent-bootstrap

> This project is a **documentation-only hub** (Markdown + YAML). There is no database.  
> This file documents the structural "data models" of the hub's configuration and knowledge files.

---

## Core Entities

### Project (manifest.yaml entry)

The primary structured data entity in this hub.

```
Project {
  name:             string   # kebab-case, unique, used as directory key
  path:             string   # absolute local path to the project repo
  description:      string   # human + agent readable summary
  primary_tech:     string   # comma-separated tech stack
  memory_bank_path: string   # absolute path to the project's memory-bank/
  docs_path:        string   # relative path to project docs, e.g. docs/projects/<name>
  notes:            string?  # optional free-form agent hints
}
```

**Relationships:**
```
Project 1--1 MemoryBank (memory_bank_path)
Project 1--1 ProjectDocs (docs_path)
```

---

### MemoryBank

The 6-file operational context for a project. One per project.

```
MemoryBank {
  projectbrief:   MarkdownFile   # project goals, scope, requirements
  productContext: MarkdownFile   # purpose, problems solved, UX goals
  systemPatterns: MarkdownFile   # architecture, design patterns, relationships
  techContext:    MarkdownFile   # tech stack, setup, constraints, conventions
  activeContext:  MarkdownFile   # current focus, recent changes, next steps (volatile)
  progress:       MarkdownFile   # task status, what works, known issues (volatile)
}
```

---

### AgentRole (agents/*.md)

A persona definition that an agent loads to change its behavior.

```
AgentRole {
  name:         string   # e.g. "software-architect"
  persona:      string   # description of the role's identity
  key_behaviors: list    # list of specific behavioral rules
  when_to_activate: string  # trigger condition
}
```

**Current roles:**
- `software-architect.md` — planning, co-creation with user
- `software-engineer.md` — implementation
- `qa-critical-reviewer.md` — critical code and PR review
- `ui-ux-engineer.md` — frontend + UX focus

---

### Skill (skills/*.md)

A reusable workflow playbook.

```
Skill {
  name:           string   # e.g. "expert-pr-review"
  steps:          list     # numbered, executable steps
  preconditions:  list     # what must be true before starting
  warnings:       list     # destructive/irreversible steps highlighted
  examples:       list     # optional worked examples
}
```

**Current skills:**
- `expert-pr-review.md`
- `cherry-pick-to-release-branch.md`
- `plan-code-review-workflow.md`
- `memory-bank-protocol.md`
- `docs-protocol.md`

---

### ProjectDocs (docs/projects/<name>/)

The technical reference documentation for a project.

```
ProjectDocs {
  api_contracts:     MarkdownFile   # endpoint/interface definitions
  data_models:       MarkdownFile   # entity schemas and conventions
  pipeline_overview: MarkdownFile   # CI/CD, build, release process
  decisions:         MarkdownFile   # ADR log
}
```

---

## File Naming Conventions

| Entity | Convention | Example |
|---|---|---|
| Skill files | `kebab-case.md` | `expert-pr-review.md` |
| Agent files | `kebab-case.md` | `software-architect.md` |
| Memory bank files | `camelCase.md` | `activeContext.md` |
| Doc files | `kebab-case.md` | `api-contracts.md` |
| Config files | `kebab-case.yaml` | `manifest.yaml` |

---

*Last updated: 2026-04-28 | Update when hub structure or configuration schema changes*
