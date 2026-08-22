# Active Context: Multi-Agent Skills Hub

## Current Focus (This Session)
**GitHub issue #8 — "Rewrite swarm-forge steal set as bootstrap skills"** (2026-08-22, cloud agent, branch `cursor/steal-swarm-forge-skill-updates-a543`). Per the issue and the pasted Scout memo steal list, landed the "full useful steal set" as native in-house skill/doc edits — ideas only from `unclebob/swarm-forge` (no LICENSE on that repo; no files/scripts/prompts/dashboard HTML copied):
- Spec-gate card + clarify card: new `## Gate cards` section in `skills/reply-contract/SKILL.md` (binary Approve/Reject on a held `Documents` list vs. a plain question+Submit — gate ≠ question). Wired into `skills/grill-with-docs/SKILL.md` Step 4.
- Stable task Name: new `## Task name` section in `reply-contract`; referenced from `grill-with-docs` and `skills/close-out/SKILL.md` Step 1.
- Four-field envelope stanza (`type`/`to`/`priority`/`task`) as an **optional** markdown block in `skills/adversarial-coordination-workflow/SKILL.md` and `skills/multi-harness-coordination/SKILL.md` — explicitly excludes `merge_and_process`, SHA identity, outbox paths, stdout `TASK:`/`NO_TASK` helpers, generated bodies.
- Architectural Review Phases checklist **names only** (UI/Core Separation; Dependency Rule; Information Hiding And Encapsulation; Local Code Quality) added to `agents/software-architect.md` and cross-referenced from `skills/codebase-simplification-audit/SKILL.md` — no CRAP/mutation/DRY tool install.
- New-invariant constitution articles: `docs/shared/constitution.md` (5 short articles) + `docs/shared/decisions.md` ADR-004 (provenance/no-vendoring decision) + one-line pointers from `AGENTS.md` §6 and `skills/INDEX.md` (AGENTS.md remains the source of truth, not replaced).
- Quality-slice cleanup pass folded into the existing Engineer role (`agents/software-engineer.md`, bounded to touched files) — no new cleaner/hardener/specifier role, no Gherkin-as-spec.
- Housekeeping: `skills/INDEX.md` entries updated for the 5 touched skills; `.grok/skills/` re-exported via `python3 scripts/export_codex_skills.py --output-dir .grok/skills --force` after adding matching `SKILL_CONFIGS` quick-start bullets in `scripts/export_codex_skills.py`; restored two grill-with-docs `.grok` reference files (`adr-format.md`, `context-format.md`) that the exporter's `--force` rmtree does not regenerate (pre-existing exporter gap, not part of this issue's scope — worth a future skill-gap note).
- Explicitly **not** touched/copied per the issue: `./swarm`, `handoffd`, cockpit/dashboard, `pack_web`/curl\|tar packs, tmux/worktree control plane, CRAP/mutation/DRY tooling, `skills/expert-pr-review/SKILL.md`, `skills/plan-code-review-workflow/SKILL.md` (no rewrite, no pointer added — not needed for this scope).
- Verification: `python3 -m unittest tests.test_export_codex_skills` — 7/7 pass (both before and after the re-export). `git diff --check` flags only pre-existing two-trailing-space markdown line-break style (matches existing ADR/agent file convention, not a real issue).
- Opened as **one draft PR** against `main`; not merged, not self-reviewed (per issue instructions — user's own reviewers, e.g. Blair grok-4.6, own the review).

## Previous Focus (superseded)
**Formatting and replay review complete** (2026-06-23). Reviewed the added skill/workflow updates in this checkout and fixed local formatting issues:
- Replaced malformed `skills/agent-bootstrap/SKILL.md` placeholder text with valid skill frontmatter, quick-start steps, and replay guidance.
- Added final trailing newlines to canonical skill Markdown files that were missing them.
- Verification evidence: `python3 -m unittest tests.test_export_codex_skills` passed (6 tests), and `git diff --check` passed.
- Added missing `skills/task-loop-7-phase.md` for the strict OBSERVE -> THINK -> PLAN -> BUILD -> EXECUTE -> VERIFY -> LEARN algorithm, wired it into `skills/INDEX.md`, `AGENTS.md`, harness trigger files, `scripts/export_codex_skills.py`, exporter tests, and regenerated `.grok/skills/task-loop-7-phase/`.

Replay finding for `/Users/tginter/dev/estategururepo/agent-bootstrap`: do not blind cherry-pick the generic gman-robotics commits. That checkout has EstateGuru-specific skills and local history, is `main...origin/main [ahead 1]`, lacks `.grok/`, `scripts/install-grok.sh`, `skills/multi-harness-coordination.md`, and `skills/agent-bootstrap/SKILL.md`, and direct `git apply --check` of the generic v0.5.0 patch fails against multiple customized files. Use a selective replay/merge plan instead.

## Current Plan — Re-implement install-grok.sh + High-Priority Grok Improvements (post-PR #1)

**Context**: After the merged `feat/grok-native-support` PR (now at d02f307 on main), the repo has a solid `.grok/skills/` + `.grok/agents/` tree committed. However, it lacks a first-class installation mechanism for using the bootstrap's skills and agents in *other projects* (the primary value of this hub).

Our earlier session (commit 97874bd) built a good `scripts/install-grok.sh` + richer documentation. User explicitly chose Option B: Re-implement/adapt on top of the current merged structure (respecting its approach), starting with the two high-priority items.

**High Priority (do first)**
1. `scripts/install-grok.sh` — Adapted version that works cleanly with the current committed `.grok/` layout (exporter + current agent files).
2. Enhanced Grok documentation in `AGENTS.md` (and supporting files) for cross-project usage.

**Medium Priority (after high priority) — COMPLETED**
- Improved agent handling in `install-grok.sh`: plugin installs now generate proper Grok frontmatter (model: sonnet, tools list, color, etc.) while --local mode respects the committed structure.
- Enhanced TDD coverage in `InstallGrokScriptTests` (verifies skill count + Grok frontmatter in generated agents for user installs).
- All tests green. Script is production-ready for the two main use cases.

**Principles**
- Respect the merged PR's packaging where reasonable.
- Make the install script solve the "use bootstrap skills/agents in any project" problem.
- Strict TDD for new script code.
- Update memory-bank after significant steps.
- Full self-review + critical checklist before any commit.

---

## Previous Plan — Sync Grok Documentation Across README, AGENTS.md, and Supporting Files (for reference)
**Created by**: Software Architect (following mandatory memory-bank read of all 6 files + AGENTS.md + relevant user-guide/*.md + grep for "Grok" + git show of the feature commit + exploration of .grok/ tree and scripts/export_codex_skills.py).

**Date**: 2026-05-19
**Status**: Approved by user — Act/Engineer executing now (2026-05-19). Progress will be appended below and in progress.md after each major file or logical chunk.

### Goals
- Make the first-class Grok 4.3+ native support (added in commit 6f48582) fully documented and discoverable so Grok CLI/TUI users get the same "clone + zero config" experience as Claude Code, Cline, etc. users.
- Bring documentation parity: Grok currently has only a one-line bullet in AGENTS.md §1 and a footer; README still lists old harnesses and v0.2.0 status.
- Record the packaging decision as a proper ADR (ADR-006) for future maintainers.
- Ensure all "last updated", version strings, and "What's Inside" / compatibility lists are consistent at v0.4.0 / 2026-05-19.
- Preserve KISS, absolute-path discipline, source-of-truth rules (canonical files stay in skills/ + agents/; .grok/ is generated + symlinked).

### Scope (In)
- **Primary files**:
  - README.md (compatibility bullets, What's Inside .grok/ entry, Status/version bump).
  - AGENTS.md (expand Grok entry into a full dedicated subsection parallel to "### Claude Code: Native Agent Spawning", plus any cross-refs).
  - docs/projects/agent-bootstrap/decisions.md (new ADR-006 at the end + update index table).
- **Secondary files** (consistency / discoverability):
  - ONBOARDING.md (add 1-2 sentences on Grok zero-config, no install-agents equivalent needed).
  - CONTRIBUTING.md (add maintenance note for re-exporting .grok/ after skill/agent changes).
  - skills/INDEX.md (note that the 11 skills surface as `/<kebab-name>` in Grok via the .grok/ packaging).
  - docs/README.md and any other docs/*/decisions.md or footers with dates (light touch, only if they claim pre-0.4.0 versions).
- **Process artifacts**: This plan written to activeContext + progress; later execution will also update memory-bank at end per protocol.

### Scope (Out)
- Any change to implementation logic, the export script (beyond docs), .grok/ file contents, or adding bundled/global skills.
- Creating the actual PR or pushing (user responsibility after QA).
- Updates to external Grok user-guide (we only document our side of the integration here).
- Touching empty .grok/personas/ and .grok/roles/ beyond documenting them as intentional placeholders (per Grok's custom roles/personas TOML+md layout in 15-subagents.md).

### Detailed Changes per File (KISS, match existing tone)

1. **README.md**
   - Compatibility section (around line 72-79): Insert **Grok** bullet (prominently, after Cursor or grouped with modern ones):
     ```
     - **Grok** (xAI Grok 4.3+ CLI/TUI and compatible environments) — **Zero-config native support**. The repo includes `.grok/skills/` (11 reusable workflows invocable as `/plan-code-review-workflow`, `/expert-pr-review`, `/memory-bank-protocol`, etc.) and `.grok/agents/` (symlinks for `Engineer`, `Architect`, `QAReviewer`, `SecurityReviewer`, `UIUXEngineer` usable via the `task` tool). AGENTS.md is auto-loaded via project-rules discovery. See AGENTS.md §1 and §3 for details.
     ```
   - What's Inside (after agents/ or memory-bank/ entry): Add a `.grok/` bullet:
     ```
     - **.grok/** — Grok (and Codex) native packaging for zero-config experience:
       - `skills/<name>/SKILL.md` + `references/source.md` (thin trigger frontmatter + authoritative playbook copy of each skill in /skills/).
       - `agents/` — symlinks to the 5 canonical role definitions (enables native `subagent_type` spawning).
       - `personas/` and `roles/` — empty placeholders for future custom persona/role TOML+md definitions (Grok layout convention).
     ```
   - Status section (line ~97): Change to `Current v0.4.0 — Core files, skills, agents, docs/, and first-class Grok 4.3+ native support (.grok/ packaging) in place. Fully functional for immediate use across Claude, Cline, Grok, Cursor, and others.`
   - Update footer date if present.

2. **AGENTS.md**
   - §1 Quick Start harness list: The existing Grok bullet is good; keep or lightly polish for consistency with new details below.
   - After the "### Claude Code: Native Agent Spawning" subsection (around line 190-210), insert a parallel:
     ```
     ### Grok: Native Skills, Agents, and Project Rules (v0.4.0+)

     When using **Grok 4.3+ CLI/TUI** (or compatible), the hub provides first-class native integration with **zero extra configuration**:

     - **Project Rules**: `AGENTS.md` (and CLAUDE.md alias) is auto-discovered and loaded at every level of the repo (see Grok user-guide 11-project-rules.md). The full global rules, memory-bank protocol, and workflows are active immediately.
     - **Skills**: All 11 skills are packaged under `.grok/skills/<name>/`. Grok surfaces them as slash commands (`/plan-code-review-workflow`, `/expert-pr-review`, `/write-tests`, `/memory-bank-protocol`, `/subagent-routing`, `/debug-investigation`, etc.). Each SKILL.md contains minimal frontmatter + quick-start; the complete authoritative steps live in `references/source.md` (kept in sync with the canonical `skills/*.md` files).
     - **Agents / Subagents**: The 5 reusable roles are exposed via `.grok/agents/` symlinks. They appear in `grok inspect`, the subagent catalog (Ctrl+Shift+A), and can be spawned with the `task` tool:
       ```
       task(subagent_type="Engineer", description="...", prompt="...", ...)
       task(subagent_type="Architect", ...)
       task(subagent_type="QAReviewer", ...)
       task(subagent_type="SecurityReviewer", ...)
       task(subagent_type="UIUXEngineer", ...)
       ```
       The YAML frontmatter `name:` in each `agents/*.md` determines the `subagent_type` value. Symlinks + the exporter script guarantee the canonical definitions in `agents/` remain the single source of truth.
     - **Personas / Roles placeholders**: `.grok/personas/` and `.grok/roles/` exist as empty directories to follow Grok's discovered layout for future custom persona or role TOML definitions (see user-guide 15-subagents.md). They are safe to ignore until the hub defines shared custom ones.

     **Maintenance for contributors**:
     - Edit the canonical sources in `skills/*.md` and `agents/*.md` only.
     - After changes: `python scripts/export_codex_skills.py --output-dir .grok/skills --force` (re-generates the 11 thin wrappers) and update any symlinks under `.grok/agents/`.
     - This keeps Grok users in sync without duplication or drift.
     - See `skills/delegation-patterns.md` and `skills/subagent-routing.md` for advanced spawning patterns (Haiku vs Sonnet model selection, parallel calls, worktree isolation).

     The result matches the project vision: clone the repo, open in Grok, everything (roles, workflows, memory-bank, manifest, docs/) just works.
     ```
   - Minor: ensure the skills table in §4 and Getting Started steps mention Grok where natural.
   - Footer already correctly says "now with first-class Grok support" — leave or bump date.

3. **docs/projects/agent-bootstrap/decisions.md**
   - Update the ADR Index table (add row for ADR-006).
   - Append at the very end (before the final *Last updated*):
     ```
     ## ADR-006: First-Class Grok Support via .grok/ Packaging, Exporter, and Symlinks

     **Date**: 2026-05-19  
     **Status**: Accepted  
     **Deciders**: @tginter (implementation), Software Architect (doc plan)

     ### Context
     The agent-bootstrap hub's core value is "clone once, full multi-harness power everywhere with zero per-harness config." Previous harnesses (Claude via ~/.claude/agents + Task(), Cline via .clinerules, etc.) had dedicated integration points. Grok 4.3+ introduced its own conventional locations: `<repo_root>/.grok/skills/<name>/SKILL.md`, `.grok/agents/`, project-rules discovery of AGENTS.md, and the `task` subagent tool. Without packaging the hub's 11 skills + 5 roles into this layout, Grok users would still need manual steps — breaking the "first-class citizen" promise.

     ### Decision
     - Add a `.grok/` tree at repo root (committed).
     - Export the 11 skills using the existing `scripts/export_codex_skills.py` (one-line wording tweak for "Grok (or Codex)") producing thin SKILL.md frontmatter + full source copy under references/.
     - Create symlinks under `.grok/agents/` pointing back to `../../agents/*.md` (DRY, single source of truth).
     - Include empty `personas/` and `roles/` directories as forward-compatible placeholders for Grok's custom role/persona TOML+md discovery.
     - Update AGENTS.md (harness list + new detailed Grok subsection), manifest version, and memory-bank/ only.
     - Document maintenance (re-export + symlink) in AGENTS.md, CONTRIBUTING.md, and this ADR.
     - Treat the generated .grok/skills/.../references/source.md as copies (never hand-edit).

     ### Alternatives Considered
     - Hand-maintained duplicate Markdown in .grok/ (high drift risk, violates KISS/DRY).
     - Post-clone install script or git hook (adds friction; harnesses vary; against "zero config").
     - Make the exporter part of every plan-code-review finalize step (overkill for docs-only changes).
     - Ignore Grok (violates the universal harness-agnostic charter in projectbrief.md).

     ### Consequences
     **Positive**:
     - Grok users get identical experience: AGENTS.md loaded, 11 skills as `/...`, 5 agents spawnable by name, full memory-bank + docs/ + manifest awareness.
     - Symlinks + exporter = no duplication; canonical files stay authoritative.
     - Future-proofs the hub for any Grok persona/role extensions.
     - Self-hosting win: the hub used its own plan-code-review + memory-bank protocol + docs-protocol to land the feature.

     **Negative / Trade-offs / Risks**:
     - Contributors must remember the re-export step after editing skills/agents (mitigated by clear docs in multiple places and the plan-code-review workflow checklist).
     - Generated files bloat the repo (~2000 lines in the initial commit) — acceptable because they are thin + the value of instant Grok usability is high.
     - Empty dirs may confuse (documented here and in AGENTS.md).

     **Mitigations**: The exporter is simple, tested (`tests/test_export_codex_skills.py`), and the whole flow was verified with `grok inspect` in the originating session.
     ```

4. **Secondary consistency updates** (small, high-value):
   - ONBOARDING.md line ~22-27 area: After the Claude install-agents paragraph, add:
     ```
     **Grok users**: No install step required. The `.grok/skills/` and `.grok/agents/` directories (plus AGENTS.md project-rules) are discovered automatically the moment you open the repo in Grok. Skills appear as `/<name>`; roles are available to the `task` tool.
     ```
   - CONTRIBUTING.md under "1. Adding or Improving a Skill" and "2. Adding or Updating an Agent Role": append a bullet:
     ```
     - Re-export the Grok packaging afterwards (`python scripts/export_codex_skills.py --output-dir .grok/skills --force`) and refresh symlinks under `.grok/agents/` so Grok users receive the updates with zero manual steps. See the Grok subsection in AGENTS.md.
     ```
   - skills/INDEX.md (top, after the intro paragraph): Add one sentence:
     ```
     Grok users automatically receive all skills as slash commands (`/<skill-kebab-name>`) thanks to the `.grok/skills/` packaging committed in v0.4.0.
     ```
   - Light footer / date bumps only where a file currently claims a pre-v0.4.0 version and the content is being touched anyway (avoid churn on untouched files).

### Execution Process (Strict — plan-code-review workflow)
1. **PLAN** (this document): Architect writes plan to memory-bank/activeContext.md (this section) + progress.md. User must explicitly approve before any file edit.
2. **CODE / ACT** (Software Engineer):
   - Start by invoking memory-bank-protocol (read all 6 files).
   - For every documentation or ADR change, follow `skills/docs-protocol.md` (choose shared vs project docs, use proper ADR template, etc.).
   - Make the smallest possible, style-matching edits (use existing patterns, absolute paths in examples, > callouts for warnings, friendly/direct tone).
   - After all edits: full self-review (re-read every changed file + run `git diff`).
   - If any exporter or script touch is truly needed (unlikely), the write-tests TDD rule applies.
3. **REVIEW** (QA Critical Reviewer): Full critical pass using the expert-pr-review checklist (correctness, completeness, no duplication of source of truth, harness parity, style, future maintenance, security/none issues since docs). Recommend Approve / Request Changes.
4. **ITERATE** if needed.
5. **FINALIZE**: Update memory-bank/activeContext.md + progress.md with "Grok docs sync complete. All user and agent docs now reflect v0.4.0 Grok support." User confirmation before any commit.

### Verification Steps (in Act phase)
- Re-read all 6 memory-bank files + the edited docs.
- `git diff --stat` + spot-check key sections.
- Optionally run the exporter test suite.
- If Grok harness available: `grok inspect` (or equivalent) to confirm skills/agents still visible after any doc-only changes.
- Confirm no generated .grok/ file was edited by hand.

### Risks & Mitigations
- **Drift risk** between canonical skills/ and .grok/ copies: Mitigated by explicit maintenance steps in 3+ places + ADR.
- **Over-documentation**: Kept KISS — one new subsection, one ADR, small bullets elsewhere.
- **Date/version churn**: Only touch files we are already editing for content reasons.
- **User approval gate**: Explicit in the workflow; this plan itself is the gate.

### Next Action After User Approval
Engineer role takes over, loads this plan from activeContext, executes exactly.

**This plan was created while following every global rule: memory-bank mandatory read, subagent policy considered (none needed for pure planning), KISS, co-create with user, absolute paths, no destructive action, prioritize refactor/doc over new code.**

*End of proposed plan*

**Execution Complete (Act phase)**: 2026-05-19 — All items in the plan executed exactly by Software Engineer + inline QA Reviewer. README, AGENTS (new detailed Grok subsection), decisions.md (ADR-006), ONBOARDING, CONTRIBUTING, skills/INDEX updated per specs. Memory bank updated throughout for thread visibility. Self-review + critical QA passed (Approve).

**User approval received**: 2026-05-19 — "approved the changes. commit them and push them up to the remote." Proceeding to commit + push per explicit instruction (satisfies global rule). Final memory-bank record included in this commit.

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

---

## v0.4.0 — Grok Native Packaging (2026-05-19)

**What was done in this session (initialization + import per user request):**

- Initialized the hub for Grok 4.3+ by reading AGENTS.md + all 6 memory-bank files at session start (per mandatory protocol).
- Created `.grok/` project-scoped configuration directory (standard location per Grok docs for skills, agents, roles/personas).
- **Skills**: Used the hub's own `scripts/export_codex_skills.py` (with a one-line compatibility note improvement) to export all 11 skills into `.grok/skills/<name>/SKILL.md + references/source.md`. The thin SKILL.md files provide trigger descriptions so Grok can auto-invoke or let users run `/plan-code-review-workflow`, `/expert-pr-review`, `/memory-bank-protocol`, etc. The full authoritative playbooks live in the existing `skills/*.md` (referenced from the exported wrappers).
- **Agents / Subagents**: Created symlinks under `.grok/agents/` to the 5 canonical role definitions. Grok now auto-discovers them as project agents: `Engineer`, `Architect`, `QAReviewer`, `SecurityReviewer`, `UIUXEngineer`. These can be spawned via the `task` tool with `subagent_type` matching the `name:` in their frontmatter.
- Verified end-to-end with `grok inspect` (shows both AGENTS.md as loaded project instructions + all 11 skills + 5 agents under the agent-bootstrap repo).
- Ran the exporter's own unit tests (`tests/test_export_codex_skills.py`) — all pass.
- Updated this `activeContext.md` and `progress.md` to record the contribution.

**Impact**: The agent-bootstrap hub is now a first-class, zero-config citizen for Grok users (just like for Claude Code, Cline, Cursor, etc.). Anyone who clones the repo and opens it in a Grok-powered environment immediately gets the full skill catalog and reusable agent personas without extra steps. AGENTS.md is auto-loaded via Grok's project-rules mechanism.

**Files changed**:
- `scripts/export_codex_skills.py` (minor wording for multi-harness clarity)
- New: `.grok/skills/...` (11 exported skill packages)
- New: `.grok/agents/` (5 symlinks to the role .md files)
- `memory-bank/activeContext.md`, `memory-bank/progress.md` (this record)

This change was performed while strictly following the hub's own global rules (absolute paths, memory-bank protocol, self-review, no destructive actions, explicit user instruction for the commit).
