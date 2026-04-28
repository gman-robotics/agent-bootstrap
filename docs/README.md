# Project Documentation (`docs/`)

This directory is the **persistent technical reference layer** for all projects in the agent-bootstrap hub.

## Two-Layer Model: `docs/` vs `memory-bank/`

This repo uses two complementary layers — understanding the difference is important:

| Layer | `docs/` | `memory-bank/` |
|---|---|---|
| **Purpose** | Persistent technical reference | Agent operational state |
| **Content** | API contracts, data models, architecture, decisions | Current focus, active decisions, session progress |
| **Read by** | Humans + agents on demand | Agents at every session start (mandatory) |
| **Update cadence** | When technical specs or decisions change | After every significant task |
| **Analogy** | Engineering wiki / reference docs | Working memory / RAM |

**Rule of thumb:**  
- "What does the API look like?" → `docs/`  
- "What are we working on right now?" → `memory-bank/`

## Directory Structure

```
docs/
├── README.md          ← this file
├── shared/            ← cross-project standards and conventions
│   ├── api-contracts.md
│   ├── data-models.md
│   ├── pipeline-overview.md
│   └── decisions.md
└── projects/
    └── <project_name>/   ← one folder per project in manifest.yaml
        ├── api-contracts.md
        ├── data-models.md
        ├── pipeline-overview.md
        └── decisions.md
```

## `shared/` — Team-Wide Standards

Applies across all projects. Examples:
- API naming conventions all projects follow
- Shared data types (user, org, timestamp format)
- Standard CI/CD pipeline patterns
- Cross-project architectural decisions

## `projects/<name>/` — Per-Project Technical Docs

Keyed to the `name` field in `manifest.yaml`. Contains project-specific detail. Examples:
- This project's specific API endpoints and contracts
- This project's database schema
- This project's deployment pipeline
- Architecture decisions specific to this project

## Document Types

| File | What Goes Here |
|---|---|
| `api-contracts.md` | Endpoint definitions, request/response schemas, auth patterns, versioning |
| `data-models.md` | Entities, relationships, field definitions, validation rules |
| `pipeline-overview.md` | Build, test, deploy, release processes and their configs |
| `decisions.md` | Architecture Decision Records (ADRs) — what was decided, why, and the consequences |

## How Agents Use This

Agents navigate here via the `docs_path` field in `manifest.yaml`:
```yaml
docs_path: docs/projects/my-app
```

See `skills/docs-protocol.md` for the full playbook on creating, updating, and referencing these docs.

## Adding a New Project

1. Add the project to `manifest.yaml` with `docs_path: docs/projects/<name>`.
2. Copy the template files from `docs/projects/agent-bootstrap/` into `docs/projects/<name>/`.
3. Fill in the relevant sections (skip/leave `N/A` for anything not applicable yet).
4. Reference the docs in your project's `memory-bank/techContext.md` and `memory-bank/systemPatterns.md`.

---

*Maintained by the team | See `CONTRIBUTING.md` for contribution guidelines*
