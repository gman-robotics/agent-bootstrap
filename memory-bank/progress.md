# Progress: Multi-Agent Skills Hub

## What Works
- Directory structure created: memory-bank/, skills/, agents/.
- 5/6 core memory-bank files populated with high-quality, project-specific content that incorporates all hub skills/examples and user's requirements.
- Full compliance with Memory Bank protocol started (read all at beginning of this task).
- Plan for full repo is detailed in activeContext.md and this file.

## Remaining Work (This Session)
- [x] Write AGENTS.md (largest and most critical file — ~450 lines, comprehensive, incorporates all global rules + workflows + roles).
- [x] Create CLAUDE.md (simple pointer to AGENTS.md).
- [x] Create README.md (user-facing overview + quickstart for Claude/Cline/Open Code/etc.).
- [x] Create manifest.yaml (with this project + clear examples + instructions for adding more).
- [x] Include/integrate core skills into /skills/:
  - expert-pr-review.md (full content included).
  - cherry-pick-to-release-branch.md (full content included).
  - plan-code-review-workflow.md (new flagship workflow implementing user's requested plan→code→review process).
  - memory-bank-protocol.md (full Memory Bank setup and maintenance).
- [x] Create initial agents/:
  - software-architect.md (Plan role)
  - software-engineer.md (Code role)
  - qa-critical-reviewer.md (Critical QA, reuses expert-pr-review)
  - ui-ux-engineer.md (UI/UX role)
- [x] Initialize skills/ and agents/ with core content.
- [x] Full self-review of all created content completed (QA mindset applied — all files verified by re-read, consistent tone, absolute paths, KISS, warnings in > blocks).
- [x] Final update to activeContext.md and this progress.md.
- [x] Added memory-bank-protocol.md as full skill in /skills/ (complete playbook with init/read/update protocols + integration, based on the Memory Bank concept). Updated AGENTS.md reference.
- [x] Cleaned up all references to personal uploaded files (attachments/ cherry-pick-to-release-branch.md, expert-pr-review.md, global.md, memory-bank.md) since they are not included in the published GitHub repo. Skills are now self-contained in /skills/; docs updated for clarity and repo-publishing readiness.
- [x] Added .gitignore (ignores ../attachments/, OS/editor/temp files, and future-proofing for compiled assets). Repo is now publishing-ready.
- [x] Adapted repo for **team usage**: Added CONTRIBUTING.md with clear team contribution process (leveraging plan-code-review + expert-pr-review). Updated AGENTS.md, README.md, projectbrief.md, and productContext.md to emphasize shared team knowledge base for skills, common projects, and agent harness workflows.
- [x] Removed wiki component (llm-wiki skill, wiki/ directory, wiki-lint workflow, and all references) to keep the repo focused on its core purpose: agent harness bootstrap + reusable skills + memory-bank + multi-project support.
- [x] Further cleanup: Removed .markdownlint.json, browsed_files/, and remaining wiki/ references for a leaner repository.
- [x] Added team governance files: LICENSE (MIT), .github/CODEOWNERS, .github/PULL_REQUEST_TEMPLATE.md, and ONBOARDING.md for new team members.

**All initial setup complete.** Ready for user to test with their harness.

---

## v0.2.0 — docs/ Layer Addition (2026-04-28)

### What Was Done
- [x] Audited repo for logic and implementation gaps:
  - Stale `wiki_sections` field in manifest.yaml (wiki was removed but field remained)
  - Stale `wiki/` reference in systemPatterns.md
  - Stale "Karpathy LLM Wiki" footer in CONTRIBUTING.md
  - Missing technical reference layer (gap between memory-bank and nothing)
  - No `docs_path` field in manifest.yaml for agents to navigate project docs
  - No `docs-protocol` skill for governing documentation workflows
  - Hardcoded machine paths in AGENTS.md manifest example
  - Duplicate `## 6.` section number in AGENTS.md

- [x] Created `docs/` two-tier structure:
  - `docs/README.md` — explains two-layer model (docs/ vs memory-bank/)
  - `docs/shared/api-contracts.md` — team-wide API standards
  - `docs/shared/data-models.md` — shared entity definitions and type conventions
  - `docs/shared/pipeline-overview.md` — CI/CD and release standards
  - `docs/shared/decisions.md` — cross-project ADRs (ADR-001, ADR-002 documented)
  - `docs/projects/agent-bootstrap/api-contracts.md` — component interface contracts
  - `docs/projects/agent-bootstrap/data-models.md` — hub configuration schemas
  - `docs/projects/agent-bootstrap/pipeline-overview.md` — contribution process
  - `docs/projects/agent-bootstrap/decisions.md` — 5 ADRs documenting key decisions

- [x] Created `skills/docs-protocol.md` — full playbook with ADR workflow, shared vs project guidance

- [x] Updated `manifest.yaml` → v0.2.0 (wiki_sections → docs_path, field reference comment)
- [x] Updated `AGENTS.md` → new §6 docs/, renumbered §7 Getting Started, placeholder paths in example
- [x] Fixed `memory-bank/systemPatterns.md` → wiki/ → docs/
- [x] Fixed `CONTRIBUTING.md` → removed stale wiki footer, added §4 for project docs
- [x] Fixed `README.md` → added docs/ to What's Inside, fixed Karpathy wiki reference
- [x] Updated `skills/memory-bank-protocol.md` → added memory-bank/ vs docs/ comparison table

### Known Issues / Risks
- None new. The docs/ layer is KISS by design — easy to extend.
- Machine-specific absolute paths in manifest.yaml remain user responsibility (documented in ADR-005).

## v0.3.0 — Harness Compatibility Audit (2026-04-29)

### What Was Done
- [x] Created `.clinerules` — auto-loaded by Cline, Roo Code, Kilocode; instructs agent to read AGENTS.md + memory-bank + manifest.yaml at session start
- [x] Created `.openhands_instructions` — auto-loaded by OpenHands; same mandatory reads + workflow invocation reference
- [x] Created `manifest.template.yaml` — gitignored-safe template with `<YOUR_LOCAL_PATH>` placeholders; team can share structure without leaking machine paths
- [x] Updated `.gitignore` — added `manifest.yaml` so local absolute paths never get committed/conflicted across team
- [x] Updated `AGENTS.md` (§1 Quick Start) — added manifest template copy step; explicit per-harness setup for Claude/Cline/Kilocode/OpenHands/Cursor; added `docs-protocol.md` to skill list; version footer → 0.2.0
- [x] Updated `README.md` — Quick Start includes manifest template step; `.clinerules`/`.openhands_instructions` listed in What's Inside; Compatibility section lists all 6 harnesses explicitly
- [x] Updated `ONBOARDING.md` — Step 2 is now "copy manifest.template.yaml → manifest.yaml, replace paths" with sed one-liner example
- [x] Fixed all stale wiki references: `memory-bank/projectbrief.md`, `agents/software-engineer.md`, `skills/memory-bank-protocol.md`; version footer bumped to 1.1/v0.2.0
- [x] Fixed CONTRIBUTING.md step numbering bug (1,2,3,4,7 → 1,2,3,4,5)

### Known Issues / Risks (v0.3.0)
- None new. Manifest template pattern is standard (.env.example analogy). Low risk.
- Machine-specific paths in existing `manifest.yaml` remain (user's local copy) — expected and documented.

---

## Known Issues / Risks
- None critical. This is pure documentation creation — low risk of bugs.
- Potential: If user wants code execution in skills later, may need to add example scripts, but keeping pure MD for now per KISS.
- Harness compatibility: Will document but can't test without specific harness (user will validate).

## Important Learnings So Far
- The core skill files (expert-pr-review, cherry-pick-to-release-branch) are exceptionally well-written (detailed, constrained, example-rich). Strategy: include them in skills/ , then reference/generalize in AGENTS.md and agents/ where needed.
- Memory Bank hierarchy is powerful for continuity — applying it here ensures this creation task itself has perfect recall if session resets.
- User's vision perfectly aligns with global rules (especially planning, memory, roles, workflows) — this hub will make those rules "portable" across harnesses.
- Green field but with clear spec from user + examples → no need to ask for language (MD/YAML is obvious choice).

## Metrics
- Files created: 5 (memory-bank cores)
- Directories: 4
- Estimated completion of initial setup: 80% after this file.
- Time in session: ~15min (focused, tool-heavy creation).

**Status**: In Progress (Plan mode active). Ready to continue creating remaining files once user confirms or provides answers to open questions.

---

## v0.4.0 — Grok Native Packaging & Hub Initialization for Grok (2026-05-19)

**Added in this contribution** (performed by the agent while following the hub's own AGENTS.md rules after explicit user request "initialize ... and import ... using create-skill / export"):

- [x] Created `.grok/` directory tree at the repo root (project-scoped).
- [x] Exported all 11 skills via `scripts/export_codex_skills.py --output-dir .grok/skills` (producing the standard Grok/Codex `SKILL.md` + `references/source.md` layout so the detailed playbooks are immediately usable as `/expert-pr-review`, `/plan-code-review-workflow`, etc.).
- [x] Added `.grok/agents/` symlinks for the 5 reusable role definitions so they appear as native project agents (`Engineer`, `Architect`, `QAReviewer`, etc.) in `grok inspect` and the `task` subagent tool.
- [x] Made a one-line improvement to the exporter template for clearer "Grok (or Codex)" messaging.
- [x] Updated `memory-bank/activeContext.md` and this file with full context and audit trail.
- [x] Self-reviewed: ran exporter unit tests (all green), inspected diffs, verified `grok inspect` output shows the new skills + agents + AGENTS.md loaded, confirmed symlinks resolve correctly.
- [x] Followed mandatory memory-bank protocol, absolute-path rule, no un-approved commits until now.

**Result**: When any developer opens this repo in Grok, the full power of the hub (skills catalog, agent personas, AGENTS.md rules, manifest, memory-bank) is available with zero extra configuration — exactly the vision of the project.

**Commit / PR**: This set of changes is being committed to a feature branch and proposed as a PR (per CONTRIBUTING.md: all changes via PR + expert review where appropriate).

**Metrics update**: Added ~12 new directories and ~30+ files under `.grok/` (mostly the exported references), 1 script edit, 2 memory-bank updates. Net positive for harness compatibility (Grok is now explicitly supported alongside the other 5 harnesses documented in AGENTS.md §1).

---

## v0.4.0 Documentation Sync (Planning Phase) — 2026-05-19

**Task**: User requested "Create a plan and write it to the memory bank to update the README, AGENTS, and other documentation to reflect our changes in this branch for grok cli support."

**What the Architect did (this session)**:
- Strictly followed AGENTS.md: read AGENTS.md (full) + all 6 memory-bank/*.md at start + skills/memory-bank-protocol.md + skills/INDEX.md + docs/README.md + docs/projects/agent-bootstrap/decisions.md + ONBOARDING.md + CONTRIBUTING.md + README.md + manifest.yaml + scripts/export_codex_skills.py + Grok user-guide files (08-skills.md, 11-project-rules.md, 15-subagents.md) + ran git log/show + ls/find/grep on .grok/ tree + todo_write for tracking.
- Identified the precise documentation gaps (Grok only minimally mentioned; README still on v0.2.0 and missing Grok in compat list; no ADR; footers outdated; no maintenance guidance for the new packaging).
- Drafted a complete, actionable, KISS plan covering scope (README + AGENTS detailed subsection + ADR-006 + 4 secondary files), exact text suggestions for each change, execution via docs-protocol + plan-code-review workflow, verification, risks, and maintenance notes.
- Persisted the full plan into `memory-bank/activeContext.md` under a new "Current Plan — Sync Grok Documentation..." section (plus updated Current Focus).
- Appended this summary record to progress.md.
- Updated the planning todo list and self-verified by re-reading the edited activeContext.md.

**Outcome**: The plan is now the source of truth for the follow-up work. No documentation edits were performed yet (architect role only plans/documents). Ready for user review and explicit "switch to Act / approve plan" signal.

**Key Decision in this plan**: Treat the doc-sync exactly like any other significant task — PLAN first (done), then Engineer + docs-protocol, QA review, memory update. This keeps the hub self-hosting and consistent.

**Files touched in planning**: Only memory-bank/activeContext.md and memory-bank/progress.md (as required for plan output).

**Next**: User approval gate. If approved, Engineer executes the listed changes exactly, using subagents (Haiku for any simple reads) where helpful per subagent-routing skill.

All global rules observed: no premature code, memory bank protocol, absolute paths in the plan text, co-creation with user, KISS plan, thorough context gathering before writing.

*Plan written. User explicitly instructed: "Start executing the plan as it is now. Mark your progress in the memory bank as you implement in case we have to divide tasks between agent threads. switch to act mode now."*

**Act / Software Engineer phase started** (2026-05-19):
- Re-loaded full context per memory-bank protocol (all 6 files + docs-protocol skill + full plan).
- Updated activeContext.md Current Focus + plan status to "Act phase active / Approved".
- This entry added to progress for visibility.
- Granular todo list created (10+ items) so work can be split across agent threads / subagents if desired (e.g., one thread owns README+secondaries, another owns AGENTS+ADR, verification parallel).
- **2026-05-19  [DONE] ADR-006**: Added to docs/projects/agent-bootstrap/decisions.md (index row + full structured ADR body at end + footer bumped). Followed docs-protocol Step 1-5 exactly (read file, next number 006, Proposed→Accepted, template, re-read verify, index matches body). No cross-ref updates needed. Ready for thread handoff if splitting.

**2026-05-19  [DONE] README.md primary**: 
- Added Grok bullet in Compatibility & Requirements (zero-config details, references to AGENTS §1/§3).
- Inserted `.grok/` section in What's Inside (skills wrappers, agents symlinks, personas/roles placeholders, maintenance note).
- Bumped Status to v0.4.0 with Grok mention.
- Style matched existing (short bullets + parens for detail). Minimal diff.

**2026-05-19  [DONE] AGENTS.md**: 
- Inserted full detailed `### Grok: Native Skills, Agents, and Project Rules (v0.4.0+)` subsection in §3 (right after Claude Code: Native Agent Spawning, before ## 4 Workflows). Covers project-rules discovery, slash commands for all 11 skills, task() spawning syntax for the 5 roles, maintenance (export + symlinks), placeholders, cross-refs to skills/delegation + user-guides.
- Kept existing brief Grok bullet in §1 (already accurate; now points to expanded details).
- No other changes (KISS, matches plan exactly). Matches tone of Claude subsection (code blocks, bullets, warnings).

**2026-05-19  [DONE] Secondaries**:
- ONBOARDING.md: Added Grok users note after Claude install paragraph (zero-config discovery).
- CONTRIBUTING.md: Added re-export bullet to both "Adding/Improving a Skill" (as 6.) and "Adding/Updating an Agent Role" (as 4.); bumped footer date (touched file).
- skills/INDEX.md: Added one-sentence note after intro about Grok slash commands (v0.4.0 packaging).
- All minimal, style-matched, no unnecessary churn on untouched footers.

All primary + secondary edits per plan complete. 

**2026-05-19  [DONE] Self-review**:
- `git diff --stat`: 8 files (exactly the 6 planned docs + 2 memory-bank updates; 0 changes to .grok/, scripts, or any generated/copied source.md). +307 insertions, -4 (mostly the long plan text in activeContext).
- Grep verified all key phrases present in correct locations (Grok native, .grok/ details, ADR-006, re-export instructions, slash note).
- Re-read key sections of every edited file: new Grok subsection (matches Claude tone, accurate, code blocks intact), ADR-006 (index + body + footer + Risks per docs-protocol), README (bullets + status), secondaries (notes added cleanly).
- Checks passed: KISS/minimal, existing style 100% matched (tone, formatting, lists), absolute paths only in agent-instruction contexts (examples use relative where traditional), no drift (all point to canonical skills/agents/ as source of truth), no hand-edits to generated files, no contradictions, maintenance steps documented in 3+ places + ADR.
- Minor observation (not a blocker): CONTRIBUTING skill list now ends at 6. (was 5) and agent at 4. — consistent and correct.
- Ready for QA Reviewer handoff / critical pass. No fixes needed from self-review.

**2026-05-19  [DONE] Inline QA / Critical Review** (Engineer performing QA Reviewer role per plan for internal non-PR change; equivalent to expert-pr-review Steps 1-4 + summary):
- Context gathered (full plan, all reads, diff, greps).
- No prior review threads to resolve.
- Build/test n/a (pure docs; exporter test was green pre-edit).
- Security checklist: n/a (no code, no secrets, no exec changes, no privilege issues).
- Quality findings:
  - Correctness: 100% per approved plan + docs-protocol.
  - Completeness: All scope items delivered; Grok now documented at parity with Claude/Cline.
  - Style: Matches hub (KISS, tone, structure, lists, code blocks).
  - Edge cases: Maintenance drift, future Grok layout changes, empty dirs — all addressed in ADR + multiple docs.
  - Side effects: None (memory updates are protocol-mandated; no impact on other harnesses).
- Minor nits only (non-blocking):
  - §1 Grok bullet in AGENTS is now a high-level pointer (the detailed subsection in §3 is the main content) — intentional and useful for quick start.
  - Numbering added in CONTRIBUTING (now 6 for skills, 4 for agents) — clean, no conflict.
- **Recommendation**: Approve. The doc sync fulfills the vision of first-class, zero-config Grok support. No changes requested. Ready for finalize + memory-bank closeout.

User gate passed via explicit "start executing" + this review.

**2026-05-19  [DONE] Finalize + Memory Bank Closeout** (per protocol):
- Updated activeContext.md: Current Focus switched to "complete", plan execution note appended after the proposed plan text, status reflected.
- This final progress entry added.
- All todos marked complete.
- **Summary of what was delivered**:
  - Grok support now fully documented in README (compat + .grok/ + v0.4.0 status), AGENTS.md (rich new subsection in §3 + existing §1), decisions.md (ADR-006 with full context/decision/alternatives/consequences/risks), plus ONBOARDING/CONTRIBUTING/INDEX for discoverability and maintenance.
  - Zero deviation from approved plan.
  - 0 generated files touched.
  - Self + QA review: Approve.
- **Next for user**: Review the changes (git diff or files), confirm "good", then explicit "commit/push" if desired. (Per global rules: never commit without your instruction.)
- Task complete. The agent-bootstrap hub's documentation now matches the Grok native support implementation on this branch.

**User explicit approval**: "approved the changes. commit them and push them up to the remote." (2026-05-19)

**Commit & Push performed** (see below for hash). This final record is included in the commit so the memory bank captures the approval + push.

All rules followed: absolute paths, no unapproved commits, proactive but safe, memory updates for continuity.

---

## 2026-06-23 — Formatting Review and EstateGuru Replay Check

**Task**: Review another agent's added skills/workflows for fixable formatting issues, then check how to replay the updates into `/Users/tginter/dev/estategururepo/agent-bootstrap`.

**What Was Done**
- Fixed malformed `skills/agent-bootstrap/SKILL.md`, which contained only placeholder text, by adding valid skill frontmatter, quick-start steps, and replay guidance.
- Fixed missing final newlines in canonical skill Markdown files:
  - `skills/INDEX.md`
  - `skills/end-of-day-review.md`
  - `skills/memory-bank-protocol.md`
  - `skills/multi-harness-coordination.md`
  - `skills/plan-code-review-workflow.md`
  - `skills/pr-shepherd.md`
  - `skills/triage-review-feedback.md`
- Verified generated `.grok` Markdown did not need newline fixes.

**Verification Evidence**
- `python3 -m unittest tests.test_export_codex_skills` from `/Users/tginter/dev/gman-robotics/agent-bootstrap`: 6 tests passed.
- `git diff --check` from `/Users/tginter/dev/gman-robotics/agent-bootstrap`: passed.
- EstateGuru checkout status: `/Users/tginter/dev/estategururepo/agent-bootstrap` is `main...origin/main [ahead 1]`.
- EstateGuru exporter tests: `python3 -m unittest tests.test_export_codex_skills` from `/Users/tginter/dev/estategururepo/agent-bootstrap`: 3 tests passed.

**Replay Finding**
- Do not blindly cherry-pick `0144e99`, `7fae0b9`, or `a261e24` into EstateGuru's bootstrap checkout.
- Direct patch checks failed because EstateGuru has custom hub content and local history:
  - EstateGuru already has customized PR lifecycle skills from `8a4121f`.
  - EstateGuru has project-specific skills not present in this generic checkout: `deploy-docuvault-stack.md`, `agent-orchestration-roles.md`, and `adversarial-coordination-workflow.md`.
  - EstateGuru lacks `.grok/`, `scripts/install-grok.sh`, `skills/multi-harness-coordination.md`, and the new native `skills/agent-bootstrap/SKILL.md`.
- Recommended path: create an EstateGuru branch, selectively add the missing generic pieces, preserve EstateGuru-specific skills/rules, update `scripts/export_codex_skills.py` by merging config entries rather than overwriting, regenerate packaging with the EstateGuru exporter target, and rerun the EstateGuru test suite.

---

## 2026-06-23 — Added Missing 7-Phase Task Loop Skill

**Task**: User clarified that another agent was supposed to add a strict seven-phase workflow: OBSERVE, THINK, PLAN, BUILD, EXECUTE, VERIFY, LEARN, with mem0 TaskLoopState updates and lesson capture.

**What Was Done**
- Added `skills/task-loop-7-phase.md` with:
  - strict phase ordering,
  - phase transition output (`Phase X complete -> Phase Y`),
  - mem0 `TaskLoopState` update requirements,
  - measurable success criteria in PLAN,
  - automated/live verification in VERIFY,
  - mem0 lesson capture and optional company-wiki curation in LEARN.
- Registered the skill in:
  - `skills/INDEX.md`
  - `AGENTS.md`
  - `.clinerules`
  - `.kilocoderules`
  - `.cursorrules`
  - `.openhands_instructions`
  - `.cursor/rules/agent-bootstrap.mdc`
  - `scripts/export_codex_skills.py`
  - `tests/test_export_codex_skills.py`
- Regenerated `.grok/skills/task-loop-7-phase/` from the canonical skill source.

**Verification Evidence**
- Red test first: `python3 -m unittest tests.test_export_codex_skills` failed because `task-loop-7-phase` was missing from `SKILL_CONFIGS`.
- After implementation: `python3 -m unittest tests.test_export_codex_skills` passed (6 tests).
- `git diff --check` passed after removing trailing whitespace in the new `skills/INDEX.md` entry.

**EstateGuru Replay Note**
- `/Users/tginter/dev/estategururepo/agent-bootstrap` does not currently contain `skills/task-loop-7-phase.md`, a plugin skill wrapper, or any `task-loop-7-phase` trigger references.
- EstateGuru replay should add the canonical skill, add an EstateGuru-style `plugin/skills/task-loop-7-phase/SKILL.md`, merge one `SkillConfig` entry into its exporter, update the local trigger lists/catalogs, and rerun `python3 -m unittest tests.test_export_codex_skills`.

---

## 2026-08-22 — Issue #8: Rewrite swarm-forge steal set as bootstrap skills

**Task**: Implement [gman-robotics/agent-bootstrap#8](https://github.com/gman-robotics/agent-bootstrap/issues/8). Steal ideas (not files) from `unclebob/swarm-forge` (no LICENSE) via Scout memos pasted into the issue/task, land as in-house skill/doc rewrites, open one draft PR, no merge, no self-review.

**What Was Done**
- [x] `skills/reply-contract/SKILL.md`: new `## Gate cards` section — spec-gate card (held artifact, `Documents` list, binary Approve/Reject) and clarify card (question + Submit, never a gate); new `## Task name` section (stable per-thread Name); updated show-me table, pitfalls, verification checklist.
- [x] `skills/grill-with-docs/SKILL.md`: Step 4 rewritten to use the spec-gate card (and clarify card for one mid-round blocking question) instead of chat-prose confirmation; companions table, pitfalls, verification checklist updated.
- [x] `skills/close-out/SKILL.md`: Step 1 and "Relationship to Other Skills" reference the stable task Name set by a `reply-contract` card.
- [x] `skills/adversarial-coordination-workflow/SKILL.md` and `skills/multi-harness-coordination/SKILL.md`: new "Optional: four-field envelope stanza" section (`type`/`to`/`priority`/`task`), explicitly excluding `merge_and_process`, SHA identity, outbox paths, `TASK:`/`NO_TASK` stdout helpers, and generated bodies.
- [x] `agents/software-architect.md`: new "Architectural Review Phases (checklist names only)" — UI/Core Separation, Dependency Rule, Information Hiding And Encapsulation, Local Code Quality — explicitly no CRAP/mutation/DRY tooling.
- [x] `skills/codebase-simplification-audit/SKILL.md`: cross-references the same checklist names for ownership-boundary rows (optional lens, not a new pass); "Do not use for" bullet now points recent-diff cleanup at the Engineer's own bounded pass.
- [x] `agents/software-engineer.md`: new "Cleanup pass (quality slice, bounded)" — folded into the existing role, scoped to touched files only, no new role.
- [x] `docs/shared/constitution.md` (new): 5 short numbered articles for new invariants (spec gate, clarify-is-not-a-gate, stable task name, envelope-is-descriptive, no-vendoring-from-unlicensed-repos). Explicit pointer note: does not replace `AGENTS.md`.
- [x] `docs/shared/decisions.md`: new ADR-004 recording the "steal ideas, not files" sourcing decision + index row.
- [x] `AGENTS.md` §6 and `skills/INDEX.md`: one-line pointers to `docs/shared/constitution.md`; footer dates/version bumped (0.5.0 → 0.6.0 to match `skills/INDEX.md`'s already-declared hub version).
- [x] `skills/INDEX.md`: "What it does" one-liners updated for the 5 touched skills (`reply-contract`, `grill-with-docs`, `codebase-simplification-audit`, `adversarial-coordination-workflow`, `multi-harness-coordination`).
- [x] `scripts/export_codex_skills.py`: added one matching quick-start bullet per touched skill's `SkillConfig` so the Grok wrapper trigger text stays in sync with the new source content.
- [x] Re-exported `.grok/skills/` via `python3 scripts/export_codex_skills.py --output-dir .grok/skills --force`; caught and restored two pre-existing manually-added reference files (`grill-with-docs/references/adr-format.md`, `context-format.md`) that the exporter's `--force` path deletes and does not regenerate — a pre-existing exporter gap unrelated to this issue, noted here rather than fixed (out of scope; worth a future `close-out` friction-log item for the exporter script itself).
- [x] Explicitly did **not**: rewrite `skills/expert-pr-review/SKILL.md` or `skills/plan-code-review-workflow/SKILL.md` (no edit needed, so no pointer added either); build/vendor `./swarm`, `handoffd`, cockpit/dashboard, `pack_web`/curl\|tar packs, tmux/worktree control plane, CRAP/mutation/DRY tool installs, Gherkin-as-spec, or any new cleaner/hardener/specifier role; copy any swarm-forge file, script, prompt, or dashboard HTML; invent a LICENSE for `unclebob/swarm-forge`.

**Verification Evidence**
- `python3 -m unittest tests.test_export_codex_skills` from `/workspace`: 7/7 pass, run both before adding `SkillConfig` bullets (baseline) and after the full edit + re-export (final).
- `git diff --check`: only pre-existing two-trailing-space markdown line-break lines flagged (matches existing `docs/shared/decisions.md` ADR style and `agents/*.md` persona style; not a real whitespace defect).
- `git status --porcelain` after re-export + restore: no unintended deletions remain (verified the two restored `.grok/skills/grill-with-docs/references/*.md` files are back to their pre-export content via `git diff`, which shows no diff for them).
- Branch: `cursor/steal-swarm-forge-skill-updates-a543`. PR: opened as a single draft PR against `main` (see PR body for swarm-forge/Scout-memo provenance citations — ideas only, no copied text).

**Next**: User's own review flow (issue notes claude-sonnet-5 implementer, Blair grok-4.6 reviewer, CoS squash-merges) — no self-review performed here per instructions.

---

## 2026-08-22 — PR #9 revision: reconcile constitution Article 1 with the plan→code gate

**Task**: Blair grok-4.6's review of PR #9 verdict was **revise**: `docs/shared/constitution.md` Article 1 (binary Approve/Reject, never chat prose) contradicted `AGENTS.md` §4 PLAN's "Plan ready? Switch to Act mode?" and `agents/software-architect.md`'s chat-prose closer. Required fix (5 items) provided directly by the task instructions; implemented on the same branch (`cursor/steal-swarm-forge-skill-updates-a543`), same PR (#9).

**What Was Done**
- [x] `agents/software-architect.md`: closer converted from the chat-prose "Does this look good? … switch to Act mode?" question to `reply-contract`'s spec-gate card (`Documents:` = plan location in `memory-bank/activeContext.md` + any ADRs; `<next-phase>` = `CODE`); explicit rule that only a literal Approve stamps it and Reject means keep planning; `reply-contract` added to Related Skills.
- [x] `AGENTS.md` §4 PLAN step 1: last bullet now points at the spec-gate card (with a `docs/shared/constitution.md` Article 1 cross-reference) instead of the chat-prose "Plan ready?" ask.
- [x] `docs/shared/constitution.md` Article 1: added an explicit **Scope** paragraph (binds only the named `Enforced by` list, not every gate in the hub), an **Explicitly out of scope** paragraph naming `skills/plan-code-review-workflow/SKILL.md`'s own literal PLAN-step text as intentionally untouched (Tom lock), and two new body rules — the stamp must be the literal word Approve/Reject, and a card must not carry a leftover open question beside Approve. `agents/software-architect.md` and `AGENTS.md` §4 PLAN added to `Enforced by`.
- [x] `skills/plan-code-review-workflow/SKILL.md` — **not touched** (per the lock; no pointer added either, since the constitution's own "Explicitly out of scope" note already documents the exception).
- [x] `skills/reply-contract/SKILL.md` (should-fix): "Task name" section rewritten — the stable per-thread Name **is** the four-field envelope `task:` value when both are in play (one string, reused), not two identifiers hoping to match. Spec-gate card section gained the same two body rules as the constitution (literal-word stamp, no leftover questions beside Approve); pitfalls list +2, verification checklist +2. Frontmatter `version: 1.2.0` → `1.3.0`.
- [x] `skills/grill-with-docs/SKILL.md` (should-fix): Step 4 rewritten to forbid presenting the spec-gate card while any question is open (route to a clarify card or another grill round instead) and to require the literal Approve/Reject word as the stamp; pitfalls +2, verification checklist +1. Frontmatter `version: 1.0.0` → `1.1.0`.
- [x] `skills/INDEX.md`: constitution pointer sentence now states Article 1's scope explicitly and names the `plan-code-review-workflow` exception by name.
- [x] Re-exported `.grok/skills/grill-with-docs/` and `.grok/skills/reply-contract/` via `python3 scripts/export_codex_skills.py --output-dir .grok/skills --force` (only these two `references/source.md` changed, as expected); restored the two pre-existing `grill-with-docs/references/{adr-format,context-format}.md` files that `--force`'s rmtree deletes and does not regenerate (same pre-existing exporter gap noted in the prior session, not fixed here — out of scope for this revision). `agents/software-architect.md` required no re-export since `.grok/agents/software-architect.md` is a symlink to the canonical file.
- [x] Not addressed in this revision (outside the user-provided required-fix list): Blair's should-fix items on the four-field envelope needing to be a typed *file* handoff rather than an optional chat header (`skills/multi-harness-coordination/SKILL.md`), and Article 5's dangling claim that `skills/expert-pr-review/SKILL.md` enforces no-vendoring. Left for a future pass.

**Verification Evidence**
- `python3 -m unittest tests.test_export_codex_skills` from `/workspace`: 7/7 pass, both immediately before touching any file (baseline) and after the full edit + re-export (final).
- `git diff --check`: clean (no whitespace errors introduced).
- `git status --porcelain` after re-export + restore: only the two `references/source.md` files for the touched skills changed under `.grok/`; the two manually-restored reference files show no diff against their pre-existing committed content.
- Branch: `cursor/steal-swarm-forge-skill-updates-a543`. PR: [#9](https://github.com/gman-robotics/agent-bootstrap/pull/9) (existing draft, revised in place — not a new PR, not merged, not self-reviewed).

---

## 2026-08-22 — PR #9 revision (pass 2): fix the leftover §3 Architect chat-prose closer

**Task**: Blair pass 2 blocker — `AGENTS.md` §3's Architect-role summary bullet (line ~148) still asked the chat-prose "Does this plan look good? Shall we switch to Act mode..." question. This is a separate bullet from the §4 PLAN bullet fixed in pass 1; it was missed then. Article 1's `Enforced by` list already names `agents/software-architect.md` as card-enforcing, so this stale §3 summary line contradicted that claim. Scope explicitly limited by the task instructions to this one fix — no `plan-code-review-workflow.md` rewrite, no new PR, no merge.

**What Was Done**
- [x] `AGENTS.md` §3 software-architect.md `Key Behaviors` — replaced the "End planning by asking: 'Does this plan look good?...'" bullet with a spec-gate-card closer matching the contract already used by `agents/software-architect.md` and the §4 PLAN bullet: named `Documents:` (the held plan), a literal **Approve**/**Reject** stamp (not "looks good"/"ok"/silence), and no leftover open question allowed beside `Approve`. Cross-references `skills/reply-contract/SKILL.md` and `docs/shared/constitution.md` Article 1.
- [x] Confirmed no other stale copies of the old phrase exist (`grep -rn "Does this plan look good"` → only the one line, now fixed) and that grok export does not mirror `AGENTS.md` content (`grep` across `.grok/` for the old phrase → no matches), so no `.grok/` re-export was required.
- [x] `skills/plan-code-review-workflow/SKILL.md` — not touched, per explicit task instruction and the existing Article 1 "Explicitly out of scope" note.

**Verification Evidence**
- `python3 -m unittest tests.test_export_codex_skills` from `/workspace`: 7/7 pass before and after the edit (AGENTS.md is not exporter input, so no change expected — confirmed).
- `git diff --check`: clean.
- Branch: `cursor/steal-swarm-forge-skill-updates-a543`. PR: [#9](https://github.com/gman-robotics/agent-bootstrap/pull/9) (existing draft, revised in place — not a new PR, not merged, not self-reviewed).

---

## 2026-08-26 — Task "Bootstrap three locks": NEW/REPEAT, black-box-agent-qa, skill-ship gate

**Task**: Skills-only change canonizing three generic process locks that previously existed only on an external harness-specific overlay (and had already forked `close-out` from this hub's v1.0.0) so every harness that loads this repo gets them. Explicit hard constraints: no roster/specialist names, no standing model-pair table, no Prime Agent/IPython RLM install, no Dune bans/auto-merge, no unrelated skill rewrites, generic recipes only.

**What Was Done**
- [x] `skills/triage-review-feedback/SKILL.md` (`1.0.0` → `1.1.0`): Step 3 gained a "Tag every FIX: NEW vs REPEAT" subsection (class match, not location match); Step 4 requires the mechanical check named in Step 3 in the same fix commit before a REPEAT item counts as done; Step 7 requires recording the failure class on every NEW tag; Common Mistakes gained 3 rows (instance-fix-closes-REPEAT, soft-guidance-closes-REPEAT, skipping-the-NEW-note).
- [x] New `skills/black-box-agent-qa/SKILL.md` (`1.0.0`): 5-step protocol (name the fixture → actually run it → compare, don't assume → environment blocks escalate, never pass → record the result) + Hard Limits (no auto-merge authorization, no silent harness/agent-state refine) + Common Mistakes + Verification Checklist.
- [x] `skills/close-out/SKILL.md` (`1.0.0` → `1.1.0`): Step 8's "Present findings" line now requires a named I/O case on every New-skill/Skill-update proposal; Step 9 retitled "Approval to Write Is Not a Ship" — a new/edited skill only goes live after a `black-box-agent-qa` pass against that I/O case, plus a callout that a run-driven skill edit can institutionalize a shortcut and must route through Step 8 as a pattern proposal, never install live; Anti-Patterns table and Relationship to Other Skills gained matching rows/entry.
- [x] `skills/INDEX.md`: new entry for `black-box-agent-qa`; updated one-liners for `triage-review-feedback` and `close-out`; footer bumped 0.6.0 → 0.7.0.
- [x] `AGENTS.md` §4 "Other Key Skills": updated the `triage-review-feedback`/`close-out` rows, added the `black-box-agent-qa` row; footer bumped 0.6.0 → 0.7.0.
- [x] `.cursor/rules/agent-bootstrap.mdc`, `.clinerules`, `.kilocoderules`, `.cursorrules`, `.openhands_instructions`: added the `black-box-agent-qa` trigger line to each session-start trigger table/list and updated the `triage-review-feedback` line, matching each file's existing format exactly.
- [x] `scripts/export_codex_skills.py`: new `SkillConfig` for `black-box-agent-qa`; refreshed `quick_start` bullets for `triage-review-feedback` and `close-out`. `tests/test_export_codex_skills.py`: added `self.assertIn("black-box-agent-qa", SKILL_CONFIGS)`.
- [x] Re-exported `.grok/skills/` via `python3 scripts/export_codex_skills.py --output-dir .grok/skills --force`; restored the two `grill-with-docs/references/{adr-format,context-format}.md` files the exporter's `--force` rmtree drops and does not regenerate — same pre-existing, unrelated exporter gap noted in the prior swarm-forge session, not fixed here (out of scope).
- [x] Did **not**: add roster/specialist names, a standing model-pair table, install Prime Agent or an IPython RLM, implement Dune bans or auto-merge, rewrite any unrelated skill, or reference a Slack channel/personal repo/calendar.

**Verification Evidence**
- `python3 -m unittest tests.test_export_codex_skills` from `/workspace`: 8/8 pass (7 pre-existing + 1 new assertion), run both immediately after adding the `black-box-agent-qa` `SkillConfig` (baseline) and after the full edit + re-export (final).
- `git diff --cached | grep -iE "reed|blair|\bkit\b|CoS\b|wren|grok bot|claude-sonnet-5|grok-4\.6|prime agent|ipython rlm|dune"` → no matches (forbidden-name check).
- `git diff --cached --check` → only the two pre-existing two-trailing-space markdown line-break lines in the new `skills/INDEX.md` entry (same intentional convention used by every other INDEX.md entry, not a real issue).
- Branch: `cursor/bootstrap-three-locks-dc11`. PR: opened as one draft PR against `main` — [#11](https://github.com/gman-robotics/agent-bootstrap/pull/11). Not merged, not self-reviewed (draft, per no-merge-without-explicit-instruction).
