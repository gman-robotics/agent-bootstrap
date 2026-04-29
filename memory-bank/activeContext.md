# Active Context: Multi-Agent Skills Hub

## Current Focus (This Session)
Harness compatibility audit and gap-filling: added `.clinerules`, `.openhands_instructions`, `manifest.template.yaml`, fixed all stale wiki references, synced version footers to v0.2.0, fixed CONTRIBUTING.md numbering bug, added `docs-protocol.md` to AGENTS.md skill list.

## Recent Changes
- 2026-04-28 (v0.2.0): Added `docs/` directory with two-tier structure:
  - `docs/shared/` — team-wide standards (api-contracts, data-models, pipeline-overview, decisions with ADRs)
  - `docs/projects/agent-bootstrap/` — fully populated example project docs
- Added `skills/docs-protocol.md` — full playbook for creating/updating docs, ADR workflow, shared vs project distinction
- Updated `manifest.yaml` v0.2.0: replaced stale `wiki_sections` field with `docs_path`; added full field reference comment
- Updated `AGENTS.md`: added `## 6. Project Documentation (docs/)` section; fixed `## 7. Getting Started` numbering; replaced hardcoded machine paths in manifest example with `<REPO_ROOT>` placeholder
- Fixed `memory-bank/systemPatterns.md`: replaced stale `wiki/` component reference with `docs/`
- Fixed `CONTRIBUTING.md`: removed stale "Karpathy LLM Wiki" footer; added section 4 for adding project docs
- Fixed `README.md`: added `docs/` to "What's Inside"; fixed stale "Karpathy wiki" philosophy line; updated Contributing instructions to include `docs_path`
- Updated `skills/memory-bank-protocol.md`: added `memory-bank/ vs docs/` comparison table and decision rules

## Active Decisions
- **Two-layer documentation model**: `memory-bank/` = agent operational state (mandatory read every session); `docs/` = persistent technical reference (read on demand). These are complementary, never merge.
- **docs_path field**: Added to manifest.yaml as the agent navigation key to project technical docs.
- **docs/projects/agent-bootstrap/** serves as the canonical template for all future project doc folders.
- **ADR format**: Context / Decision / Alternatives Considered / Consequences (positive, negative, risks). Always append, never delete.
- **Machine-specific paths**: `<REPO_ROOT>` placeholder used in AGENTS.md examples; actual paths remain in manifest.yaml (user responsibility per ADR-005).

## Open Questions
- None critical. Ready for team use and further project additions.

## Current Status
**v0.2.0 complete.** All gaps identified in audit have been addressed:
- ✅ `docs/` directory fully created with shared/ and projects/agent-bootstrap/
- ✅ `skills/docs-protocol.md` created
- ✅ `manifest.yaml` updated (wiki_sections → docs_path, v0.2.0)
- ✅ `AGENTS.md` updated (new section 6, fixed numbering, placeholder paths in example)
- ✅ All stale wiki references cleaned up
- ✅ `memory-bank-protocol.md` updated with docs/ vs memory-bank/ guidance

**v0.3.0 (2026-04-29) — Harness Compatibility Audit:**
- ✅ `.clinerules` — created/updated: bootstraps Cline, Roo Code, Kilocode into hub context
- ✅ `.openhands_instructions` — created: auto-loaded by OpenHands; points to AGENTS.md
- ✅ `manifest.template.yaml` — created: team-shareable template with `<YOUR_LOCAL_PATH>` placeholders
- ✅ `.gitignore` — updated: `manifest.yaml` now gitignored (local paths stay local)
- ✅ `AGENTS.md` — updated: per-harness setup for Claude/Cline/Kilocode/OpenHands/Cursor; manifest template step; `docs-protocol.md` added to skill list; version → 0.2.0
- ✅ `README.md` — updated: Quick Start with manifest template; `.clinerules`/`.openhands_instructions` in What's Inside; per-harness Compatibility list; version → 0.2.0
- ✅ `ONBOARDING.md` — updated: Step 2 now explains manifest template copy+sed pattern
- ✅ Stale wiki refs fixed: `projectbrief.md`, `software-engineer.md`, `memory-bank-protocol.md` (version footer → 1.1/v0.2.0)
- ✅ `CONTRIBUTING.md` — fixed: step numbering bug (1,2,3,4,7 → 1,2,3,4,5)

**Next**: Team members can add their projects using the template in `docs/projects/agent-bootstrap/` and `skills/docs-protocol.md` for guidance. No further critical gaps identified.
