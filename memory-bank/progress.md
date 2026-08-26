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

---

## 2026-08-26 — PR #11 revision: adversary found the locks were prose, made them mechanical

**Task**: Adversary review of PR #11 revised with 4 blockers, all marked NEW: (1) the REPEAT lock had no in-tree fixture + red check, only a skill sentence; (2) `black-box-agent-qa` had no runnable I/O contract, directory was SKILL.md-only; (3) this skill-authoring change had never itself passed a black-box run — the exporter unittest + forbidden-name grep from the prior revision was reading Markdown, not a black-box pass; (4) `close-out` Step 9 / INDEX "Adding a New Skill" never defined the mechanical live-flip, and did not block a silent trajectory refine from shipping. Stay on the same branch/PR, no second PR, no merge.

**What Was Done**
- [x] **REPEAT fixture (blocker 1)**: `skills/triage-review-feedback/fixtures/repeat-exporter-dropped-references/{README.md,hand-added-reference.md}` — a real, in-tree fixture reproducing the exact failure class already logged 3x in this file (2026-08-22: NEW in the swarm-forge session, REPEAT in PR #9 pass 1, REPEAT again in PR #9 pass 2 — same exporter `--force` rmtree dropping hand-added `references/` files, never mechanically checked). Added `tests/test_export_codex_skills.py::test_force_reexport_preserves_hand_added_reference_files` — confirmed **red** against the unfixed exporter (ran it standalone before touching `scripts/export_codex_skills.py`), then fixed the exporter for real (`collect_preserved_files()` + restore-after-rmtree in `export_skills()`) and confirmed **green**. Bonus: this session's own `.grok/skills/` re-export needed **zero manual restoration** of `grill-with-docs/references/{adr-format,context-format}.md` for the first time ever in this repo — verified with `git diff --stat -- .grok/skills/grill-with-docs/` (empty).
- [x] **Runnable I/O contract (blocker 2)**: `skills/black-box-agent-qa/SCHEMA.md` (minimum `case.json` schema: `input.command` argv + `expected` exit_code/stdout_contains/stderr_contains), `scripts/run_black_box_fixture.py` (the invoker — loads a `case.json`, runs it as a real subprocess, compares output, writes a run record with a `skill_sha256`), and two worked fixtures: `skills/black-box-agent-qa/fixtures/repeat-lock-mechanical-check/` and `.../fixtures/close-out-live-gate-check/` (each `case.json` + `README.md`). TDD: `tests/test_run_black_box_fixture.py` (6 tests: case loading, pass, fail-on-mismatch, fail-on-exit-code, blocked-on-missing-executable, run-record-writing) — confirmed red (`ModuleNotFoundError`) before the module existed, green after.
- [x] **Captured run record for this change (blocker 3)**: ran `python3 scripts/run_black_box_fixture.py` for real, three times, producing genuine (not hand-written) `skills/black-box-agent-qa/black-box-run.json`, `skills/triage-review-feedback/black-box-run.json`, and `skills/close-out/black-box-run.json` — each with a real captured `stderr_tail`, a real `skill_sha256` of the exact shipped `SKILL.md`, and `"verdict": "pass"`. Confirmed `scripts/check_skill_live.py <name>` exits `1` ("no run record") before capture and `0` ("live-eligible") after, for all three.
- [x] **Live-flip defined + gated (blocker 4)**: new `scripts/check_skill_live.py` — a skill is live only when it exits `0` against a `black-box-run.json` with `verdict: pass` and a `skill_sha256` matching the *current* `SKILL.md` byte-for-byte. TDD: `tests/test_check_skill_live.py` (5 tests, including `test_fails_when_skill_md_changed_since_the_run_record_was_captured` — the mechanical silent-refine guard: editing `SKILL.md` after capture invalidates the hash and the gate fails until a fresh pass is captured). `skills/close-out/SKILL.md` Step 9 rewritten to name this exact 4-step sequence (write → `run_black_box_fixture.py` → `check_skill_live.py` exits 0 → only then list it); `skills/INDEX.md §Adding a New Skill` gained the same gate as a numbered step before any INDEX/AGENTS.md/trigger-table listing; `CONTRIBUTING.md` §1 "Adding or Improving a Skill" gates the same way.
- [x] **Should-fix items**: worked REPEAT fixture in-tree (blocker 1 covers this); minimum I/O contract documented (`SCHEMA.md`); INDEX.md and CONTRIBUTING.md both gate discoverability on the run record; the `.grok/skills/triage-review-feedback/references/source.md` wrapper's "goes red on a fixture reproducing the old bug" claim is now backed by a real fixture pointer (added a "Worked example in this repo" paragraph naming `fixtures/repeat-exporter-dropped-references/` and the exact `memory-bank/progress.md` history) instead of being an unbacked assertion.
- [x] Version bumps: `skills/triage-review-feedback/SKILL.md` `1.1.0` → `1.2.0`, `skills/close-out/SKILL.md` `1.1.0` → `1.2.0`, `skills/black-box-agent-qa/SKILL.md` `1.0.0` → `1.1.0`. `skills/INDEX.md`/`AGENTS.md` footers: hub version `0.7.0` → `0.8.0`.
- [x] Did **not**: open a second PR, merge, add roster/specialist names, a model-pair table, install Prime Agent/IPython RLM, implement Dune bans/auto-merge, or touch any unrelated skill.

**Verification Evidence**
- `python3 -m unittest discover -s tests` from `/workspace`: **20/20 pass** (3 test modules: `test_export_codex_skills.py` [9, +1 new], `test_check_skill_live.py` [5, new], `test_run_black_box_fixture.py` [6, new]).
- Each new mechanical check was confirmed **red before, green after** its corresponding implementation, run standalone: the REPEAT regression test failed against the unfixed exporter; `test_check_skill_live` and `test_run_black_box_fixture` failed with `ModuleNotFoundError` before their modules existed.
- Real captured run records exist at `skills/black-box-agent-qa/black-box-run.json`, `skills/triage-review-feedback/black-box-run.json`, `skills/close-out/black-box-run.json` — each `verdict: pass`, each with a real `stderr_tail` and `skill_sha256`.
- `scripts/check_skill_live.py <name>` exits `0` for all three skills, and was observed exiting `1` for all three immediately before the run records existed (same session, same terminal).
- `git diff --stat -- .grok/skills/grill-with-docs/` after re-export: empty — the exporter fix preserved the hand-added reference files with no manual restoration, for the first time in this repo's history.
- `git diff --cached | grep -iE "reed|blair|\bkit\b|\bcos\b|wren|grok bot|claude-sonnet-5|grok-4\.6|prime agent|ipython rlm|\bdune\b"`: no forbidden-roster/model-pair matches.
- `git diff --cached --check`: clean.
- Branch: `cursor/bootstrap-three-locks-dc11`. PR: same PR, updated in place — [#11](https://github.com/gman-robotics/agent-bootstrap/pull/11). No second PR opened. Not merged.

---

## 2026-08-26 — PR #11 revision (pass 2): bind INDEX listings to the live gate

**Task**: Adversary pass 2 revised with one REPEAT blocker (same class as prior blocker #4): `scripts/check_skill_live.py` worked correctly when typed by hand, but nothing bound it to the real `skills/INDEX.md` listing — reviewer counted 23 `###` entries, 3 live-eligible, 20 "not live: no run record," and no test/CI/hook caught that gap. Investigated this repo's CI: confirmed via `gh api repos/gman-robotics/agent-bootstrap/actions/workflows` (0 workflows) and no `.github/` directory at all — there is no CI. The place tests "actually run" in this repo is `python3 -m unittest discover -s tests`, the exact command every prior session in this file cites as its verification step; that is where the bind had to go. Stayed on the same branch/PR (#11 @ `8671c3e` at task start), no second PR, no merge.

**What Was Done**
- [x] New `scripts/index_skills.py`: `list_index_skill_names()` (parses `### <name>` entries from `skills/INDEX.md`), `GRANDFATHERED_SKILLS` (named allowlist of the 20 pre-gate skills, not a silent exemption), `find_ungated_entries()` (the actual bind — returns one failure message per listed, non-grandfathered skill that is not live per `check_skill_live`).
- [x] New `tests/test_index_live_binding.py` (4 tests): `test_every_non_grandfathered_index_entry_is_live` runs `find_ungated_entries` against the real `skills/INDEX.md` — this is the bind that fails a test if INDEX lists a skill live without a current pass. `test_binding_catches_an_index_entry_with_no_run_record` is the REPEAT-class fixture required by the review: a synthetic INDEX.md + skill dir with no run record, not grandfathered, run through the real production `find_ungated_entries` function (not a re-implementation). Confirmed **red** (`ModuleNotFoundError`) by temporarily moving `scripts/index_skills.py` out of the way before writing it; confirmed **green** after. Also confirmed, as a direct real-world reproduction of the adversary's own diagnosis: calling `find_ungated_entries(INDEX_PATH, SKILLS_DIR, allowlist=frozenset())` against the *actual* `skills/INDEX.md` returns exactly 20 failures (matches the reviewer's count precisely) — this is the exact "old class" the fixture and the real test both close.
- [x] Should-fix: narrowed the black-box-agent-qa "worked examples" claim — added a third fixture, `skills/black-box-agent-qa/fixtures/check-skill-live-cli/`, that runs a plain CLI script (`python3 scripts/check_skill_live.py black-box-agent-qa`, no `unittest` involved) instead of only ever running `python3 -m unittest ...`. Captured a real evidence run to `fixtures/check-skill-live-cli/example-run.json`. `SCHEMA.md` and `SKILL.md`'s "Runnable Contract" table updated to name all three fixtures and state the contract is generic, not `unittest`-specific.
- [x] Should-fix: named allowlist for the other 20 INDEX skills (`GRANDFATHERED_SKILLS` above) — explicit by name, with an in-code comment warning against adding a *new* skill's name to it to dodge a gate failure.
- [x] Should-fix: `skills/close-out/SKILL.md` Step 9's exit-code sentence now lists the stale-hash case explicitly (it previously enumerated "no run record / not pass / JSON-invalid" and silently omitted "stale `skill_sha256`", even though the stale-hash rule was stated elsewhere in the same step).
- [x] `skills/INDEX.md §Adding a New Skill` step 3 and `CONTRIBUTING.md` §1 both now state the binding test exists and explicitly warn against adding a new skill to `GRANDFATHERED_SKILLS` to route around a gate failure.
- [x] Versions bumped again (both skills were touched to reference the new binding/fixture): `close-out` `1.2.0` → `1.3.0`, `black-box-agent-qa` `1.1.0` → `1.2.0`. `triage-review-feedback` **not touched** this pass — confirmed via `git diff skills/triage-review-feedback/SKILL.md` (empty) — so its run record needed no re-capture. Hub version `0.8.0` → `0.9.0`.
- [x] Re-captured run records for the two touched skills after all edits landed: `skills/black-box-agent-qa/black-box-run.json` and `skills/close-out/black-box-run.json`, both fresh `verdict: pass` against the final `SKILL.md` content. Directly observed the staleness guard fire for real mid-session: after editing both `SKILL.md` files, `python3 -m unittest discover -s tests` failed `test_every_non_grandfathered_index_entry_is_live` with both skills reported "stale — SKILL.md changed since capture" — proof the mechanism catches its own maintainer, not just a hypothetical one — then went green again immediately after re-capturing.
- [x] Re-exported `.grok/skills/` after the edits; confirmed (again) zero manual restoration needed for `grill-with-docs/references/{adr-format,context-format}.md`.
- [x] Did **not**: reopen the REPEAT fixture, black-box I/O contract, or captured-run-record work from pass 1 (found intact, not broken); open a second PR; merge; add roster/specialist names, a model-pair table, or a new product install.

**Verification Evidence**
- `gh api repos/gman-robotics/agent-bootstrap/actions/workflows`: `{"total_count":0,"workflows":[]}` — no CI exists on this repo; confirms the bind belongs in `tests/`, the actual local verification path.
- `python3 -m unittest tests.test_index_live_binding` before `scripts/index_skills.py` existed: `ModuleNotFoundError` (red).
- Manual reproduction of the adversary's exact diagnosis: `find_ungated_entries(INDEX_PATH, SKILLS_DIR, allowlist=frozenset())` against the real `skills/INDEX.md` → 20 failures listed by name, matching the review's reported count exactly.
- `python3 -m unittest discover -s tests` from `/workspace`: **24/24 pass** (20 pre-existing + 4 new in `test_index_live_binding.py`).
- `python3 scripts/check_skill_live.py <name>` exits `0` for all three of `black-box-agent-qa`, `triage-review-feedback`, `close-out`.
- `git diff --stat -- .grok/skills/grill-with-docs/` after re-export: empty (fix from pass 1 still holds).
- `git diff --cached | grep` for forbidden roster/model-pair names: no matches. `git diff --cached --check`: clean.
- Branch: `cursor/bootstrap-three-locks-dc11`. PR: same PR, updated in place — [#11](https://github.com/gman-robotics/agent-bootstrap/pull/11). No second PR opened. Not merged.

---

## 2026-08-26 — Bootstrap leftover gates: three pass-3 should-fix items on merged PR #11

**Task**: Follow-up to [PR #11](https://github.com/gman-robotics/agent-bootstrap/pull/11) (merged into `main` at `377cfd8`). A pass-3 review of the merged state found three should-fix leftovers, distinct from the pass-2 "INDEX bind" blocker already closed in #11. New branch, new PR (`cursor/bootstrap-leftover-gates-6517`) — #11 itself not reopened, not merged.

**What Was Done**
- [x] **Leftover 1 (grandfather list can't grow silently)**: investigated first — `scripts/index_skills.py`'s `GRANDFATHERED_SKILLS` was **already** `frozenset[str]` with exactly the original 20 names as of `377cfd8` (confirmed via `git show 377cfd8:scripts/index_skills.py`), so no code change was needed there. What was missing was a test pinning that invariant: added `test_grandfathered_skills_is_frozen_at_the_original_twenty` to `tests/test_index_live_binding.py`, asserting `isinstance(..., frozenset)` and `len(...) == 20` — a future addition now requires touching this test's expected count in the same diff, turning silent growth into a visible review point.
- [x] **Leftover 2 (bare CLI invocation)**: reproduced the reported bug first — `python3 scripts/index_skills.py` from repo root, no `PYTHONPATH`, raised `ModuleNotFoundError: No module named 'scripts'` (the script's own directory lands on `sys.path[0]`, not the repo root, so its `from scripts.check_skill_live import check_skill_live` failed). Fixed in `scripts/index_skills.py` with a guarded `sys.path.insert(0, str(REPO_ROOT))` before the import (skipped if already present, so importing the module normally — e.g. from `tests/test_index_live_binding.py` — doesn't get a duplicate path entry). Added `test_bare_cli_invocation_works_from_repo_root_with_no_pythonpath`, a real `subprocess.run` of the literal documented command with `PYTHONPATH` stripped from the child env — confirmed **red** (`ModuleNotFoundError`) against the unfixed script via `git stash push -- scripts/index_skills.py`, confirmed **green** after.
- [x] **Leftover 3 (CONTRIBUTING/close-out overclaim)**: confirmed the parser gap first — `list_index_skill_names()` matches only `^### (.+)$` against `skills/INDEX.md`; it does not read `AGENTS.md` §4 or any of the five per-harness trigger-list files (`.clinerules`, `.cursorrules`, `.kilocoderules`, `.openhands_instructions`, `.cursor/rules/agent-bootstrap.mdc`), which use three mutually different formats (bullet-arrow lists in three files, two different table layouts in the other two) — not a case where the existing single-file `### <name>` regex has a clean extension. Took the smaller honest fix per the task instruction: reworded `CONTRIBUTING.md` §1 and `skills/close-out/SKILL.md` Step 9.4 (+ `.grok/skills/close-out/references/source.md` mirror, regenerated via the real exporter, not hand-copied) to state plainly that `tests/test_index_live_binding.py` mechanically binds `skills/INDEX.md` only, and that AGENTS.md/trigger-table placement ahead of the gate is a review-discipline point, not something the suite catches. The `skills/close-out/SKILL.md` YAML frontmatter description and `skills/INDEX.md §Adding a New Skill` step 3 were already scoped correctly (verified, not touched beyond what's listed).
- [x] Bumped `close-out` `1.3.0` → `1.3.1` (both trees) for the Step 9.4 wording fix; re-captured its `black-box-run.json` via `scripts/run_black_box_fixture.py --fixture skills/black-box-agent-qa/fixtures/close-out-live-gate-check --skill close-out` after the edit (the staleness guard fired as expected — `check_skill_live.py close-out` went from exit `1` "stale" to exit `0` "live-eligible" after recapture). Hub version `0.9.0` → `0.9.1` (`AGENTS.md`, `skills/INDEX.md` footers).
- [x] Did **not**: touch `triage-review-feedback` or `black-box-agent-qa` `SKILL.md` (no wording issue found in either, confirmed via targeted grep before editing — their run records stayed valid, no recapture needed); reopen any of PR #11's four closed blockers (re-verified `test_every_non_grandfathered_index_entry_is_live` and the REPEAT exporter fixture both still pass, untouched); reopen or merge #11; open more than one new PR; add roster/specialist names, a model-pair table, or a new product install.

**Verification Evidence**
- Reproduction: `python3 scripts/index_skills.py` on unfixed `377cfd8` → `ModuleNotFoundError` (exit 1). Grep confirmed `GRANDFATHERED_SKILLS` already a `frozenset` of 20 at `377cfd8`, and the AGENTS.md/trigger-table overclaim's exact wording in `CONTRIBUTING.md`:21 and `skills/close-out/SKILL.md`:165 before editing.
- `python3 -m unittest discover -s tests`: **26/26 pass** (24 pre-existing + 2 new in `test_index_live_binding.py`).
- `python3 scripts/index_skills.py` from `/workspace` and from `/tmp` (different cwd), and via `python3 /workspace/scripts/index_skills.py`: exit `0` in all three, no `PYTHONPATH` set.
- `python3 scripts/check_skill_live.py close-out`: exit `0`, `"live-eligible: run record verdict is pass and matches the current SKILL.md"`.
- `git diff --stat .grok/skills/close-out/references/source.md` after running `python3 scripts/export_codex_skills.py --output-dir .grok/skills --force`: only `close-out` changed (3 lines), byte-identical to the canonical `skills/close-out/SKILL.md` edit — confirms the dual-tree mirror was regenerated, not hand-drifted.
- Branch: `cursor/bootstrap-leftover-gates-6517`. New PR opened against `main`; #11 not reopened, not merged.

---

## 2026-08-26 — PR #12 revision: leftover 1's frozen+len==20 pin was a same-length swap away from useless

**Task**: Adversary review of [PR #12](https://github.com/gman-robotics/agent-bootstrap/pull/12) at `068f6c8` found a must-fix regression in leftover 1 only (L2 bare-CLI-invocation and L3 CONTRIBUTING/close-out wording stayed closed, not reopened; PR #11's four blockers stayed closed too, re-verified not reopened): `test_grandfathered_skills_is_frozen_at_the_original_twenty`'s `isinstance(frozenset)` + `len() == 20` check cannot distinguish the real `GRANDFATHERED_SKILLS` from a same-length swap (one real name removed, one brand-new fake name added) — both checks stay green either way.

**Reproduced the exploit for real before writing the fix** (temporarily, on the actual production files, reverted immediately after — not committed): swapped `delegation-patterns` for a fake `a-totally-new-example-skill` in both `scripts/index_skills.py`'s `GRANDFATHERED_SKILLS` and the matching `skills/INDEX.md` `### <name>` entry (old entry removed, fake one added in its place). Ran the full suite: **all 26 prior-revision tests passed**, including `test_grandfathered_skills_is_frozen_at_the_original_twenty` (frozenset+len==20 still true) and `test_every_non_grandfathered_index_entry_is_live` (`find_ungated_entries` returned `[]`, because the swapped-in name is allowlisted and skipped before `check_skill_live` ever runs on it, and the swapped-out entry no longer exists in INDEX.md to be checked at all) — exactly the adversary's reported gap, confirmed live against the real files, not a hypothetical.

**What Was Done**
- [x] **Must-fix**: Added `ORIGINAL_GRANDFATHERED_SKILLS` — an independent, hand-maintained pin of the exact 20 names in `tests/test_index_live_binding.py` (deliberately not derived from the production constant, so it can't drift in lockstep with it). `test_grandfathered_skills_is_frozen_at_the_original_twenty` now asserts `GRANDFATHERED_SKILLS == ORIGINAL_GRANDFATHERED_SKILLS` (exact-set equality) instead of `len(...) == 20`; kept the `isinstance(frozenset)` assertion. New `test_swapping_one_grandfathered_name_for_a_new_one_is_caught` fixture: builds `(GRANDFATHERED_SKILLS - {"delegation-patterns"}) | {"a-totally-new-example-skill"}`, asserts it still satisfies `frozenset` + `len() == 20` (proving those checks alone are insufficient) and asserts it fails the new equality pin (`assertNotEqual` against `ORIGINAL_GRANDFATHERED_SKILLS`).
- [x] **Red-then-green confirmed against the real files** (same swap as the exploit reproduction above, reverted after): with the swap applied, `test_grandfathered_skills_is_frozen_at_the_original_twenty` failed with a clear symmetric-difference message (`{'delegation-patterns', 'a-totally-new-example-skill'}`) while `test_every_non_grandfathered_index_entry_is_live` and `test_grandfathered_allowlist_only_names_currently_listed_skills` stayed green (confirming those two still don't catch this class on their own — the new equality pin is what closes it). Reverted both files; full suite green again (27/27).
- [x] **Should-fix**: `scripts/index_skills.py` module docstring no longer implies the module (or `tests/test_index_live_binding.py`) binds `AGENTS.md` §4 or the trigger-list files — now states plainly it binds only `skills/INDEX.md`'s `### <name>` entries, matching the wording already fixed in `CONTRIBUTING.md`/`close-out` last pass.
- [x] **Should-fix**: Reworded the `GRANDFATHERED_SKILLS` code comment and `test_every_non_grandfathered_index_entry_is_live`'s failure message — both previously read as "add it to GRANDFATHERED_SKILLS if it predates the gate," which the adversary flagged as still inviting an addition. Now state the set is **closed**, not a route around a failing new skill, and point at the new equality pin as what actually blocks that route.
- [x] Did **not**: touch `scripts/check_skill_live.py`, `CONTRIBUTING.md`, `skills/close-out/SKILL.md`, any `.grok/` mirror, any `black-box-run.json`, or any version footer — leftover 1 is the only thing in scope this pass, and none of those files needed a `SKILL.md` staleness recapture since no `SKILL.md` was edited.
- [x] Did **not**: reopen PR #11's four blockers or leftovers 2/3; open a second PR; merge; add roster/specialist names, a model-pair table, or a new product install.

**Verification Evidence**
- Exploit reproduction (temporary, reverted, not committed): swap applied to real `scripts/index_skills.py` + `skills/INDEX.md` → `python3 -m unittest discover -s tests` → **26/26 pass** (the bug, confirmed).
- Fix applied, same swap re-applied to real files → `python3 -m unittest tests.test_index_live_binding` → **1 failure** (`test_grandfathered_skills_is_frozen_at_the_original_twenty`, red) while `test_every_non_grandfathered_index_entry_is_live` and `test_grandfathered_allowlist_only_names_currently_listed_skills` stayed green (proving they alone don't close this gap).
- Swap reverted → `python3 -m unittest discover -s tests` → **27/27 pass** (26 pre-existing + 1 new fixture; the type+count test was replaced in place, net +1).
- `python3 scripts/index_skills.py` (bare CLI, no `PYTHONPATH`) and `python3 scripts/check_skill_live.py` for `close-out`/`black-box-agent-qa`/`triage-review-feedback`: all exit `0`, unchanged — confirms leftovers 2/3 and #11's blockers stayed closed.
- `git diff --stat`: exactly `scripts/index_skills.py` and `tests/test_index_live_binding.py` — no other file touched.
- `git diff | grep` for forbidden roster/model-pair/product names: no matches.
- Branch: `cursor/bootstrap-leftover-gates-6517` (unchanged). PR updated in place — [#12](https://github.com/gman-robotics/agent-bootstrap/pull/12). No second PR opened. Merged into `main` at `d5643a3` (confirmed via `gh pr view 12`).

---

## 2026-08-26 — Task "show-me-native-skill": new native show-me skill, reply-contract pairing line fixed to a real path

**Task**: Implement a thin native `show-me` skill (locked design, not a fold into `reply-contract`, not `npx skills add humanlayer/skills`). `show-me` owns recipes only (call tree, file/screen tree, stack, diff of those shapes, opt-in mermaid); `reply-contract` keeps voice/marks/leftover-vs-bug/spec-gate/clarify/task-name and now *loads* `skills/show-me/SKILL.md` instead of naming a fictional, path-less "show-me" in its pairing line. Hub gates are mandatory, not grandfathered: `show-me` must not be added to `GRANDFATHERED_SKILLS`, must pass a real `black-box-agent-qa` fixture + `check_skill_live.py show-me` before its INDEX.md entry, and must exist in both `skills/` and `.grok/skills/` (no `plugin/` tree in this repo). MIT credit to HumanLayer/Dex Horthy's `show-me` idea, independent rewrite (no copied plugin tree, no `Bash(open ...html)` guidance). New, independent task — not a follow-up to #11/#12 (confirmed both merged/closed, not reopened).

**What Was Done**
- [x] New `skills/show-me/SKILL.md` (`1.0.0`): Purpose/Trigger/Do-not-use-for, "One primary visual per reply" rules (fenced-text Photon default, mermaid/HTML opt-in only, never a `Bash(open ...html)`-style command, no multi-visual dumps), five recipes (call tree, file/screen tree, stack, diff of a shape, opt-in mermaid) each with a worked fenced example, MIT credit section naming HumanLayer/Dex Horthy's `show-me` announcement (`https://x.com/dexhorthy/status/2087569590268391897`) as an independent rewrite, and an explicit Disambiguation/Do-not-use-for list (`diagram-design`, `scroll-craft`, a Hermes-style humanizer, `grill-with-docs` — none of which exist in this repo; named for external clarity per the task's lock).
- [x] `skills/reply-contract/SKILL.md` (`1.3.0` → `1.4.0`): Purpose line now reads "Load `skills/show-me/SKILL.md` for the one visual ... this file only decides *whether* a visual belongs and *which* one, `show-me` owns *how* to build it" — replacing the old fictional, path-less "Pair with **show-me** (trees / stacks / diffs)." Table header renamed "Pick one visual — load show-me" with an explicit pointer to `skills/show-me/SKILL.md` for the recipe behind each row. Pitfall #4 and the show-me verification checklist item now name the real path too. Nothing else in reply-contract's voice/marks/leftover-vs-bug/spec-gate/clarify/task-name machinery touched.
- [x] `skills/reply-contract/references/photon-show-me.md`: "Load `show-me`" → "Load `skills/show-me/SKILL.md`" — kept as the channel constraint + picker only, still does not copy show-me's recipes.
- [x] Mechanical gate evidence (per `black-box-agent-qa`, not grandfathered): new `tests/test_show_me_skill.py` (7 tests) checks, against the real committed files: `skills/show-me/SKILL.md` exists with `name: show-me`/`version: 1.0.0`; `skills/reply-contract/SKILL.md` contains the literal `skills/show-me/SKILL.md` string and no longer contains the old fictional pairing sentence; reply-contract says it *loads* (not reimplements) show-me; `references/photon-show-me.md` also names the real path; `.grok/skills/show-me/SKILL.md` exists (dual tree); and show-me's recipe headings vs. reply-contract's voice/task-name/spec-gate headings stay on their own file (no duplication either direction). New fixture `skills/show-me/fixtures/reply-contract-link-check/{case.json,README.md}` runs `python3 -m unittest tests.test_show_me_skill -v` and expects exit `0` / stderr containing `OK`. Ran `scripts/run_black_box_fixture.py --fixture skills/show-me/fixtures/reply-contract-link-check --skill show-me --out skills/show-me/black-box-run.json` for real — genuine captured `verdict: pass`, real `skill_sha256`, real `stderr_tail`. `python3 scripts/check_skill_live.py show-me` exits `0` ("live-eligible").
- [x] `skills/INDEX.md`: new `### show-me` entry added **after** the gate above went green (not before); `reply-contract`'s one-liner updated to say it loads `skills/show-me/SKILL.md`. Footer hub version `0.9.1` → `0.9.2`. Confirmed `python3 scripts/index_skills.py` reports "Every non-grandfathered INDEX.md entry is live-eligible" and `tests/test_index_live_binding.py` (all 7 tests, unchanged) still passes with `show-me` now a real, non-grandfathered, live-gated entry — **not** added to `GRANDFATHERED_SKILLS` (confirmed via `git diff scripts/index_skills.py tests/test_index_live_binding.py` — empty, neither file touched).
- [x] `AGENTS.md` §4 "Other Key Skills": `reply-contract` row updated (loads show-me), new `show-me` row added; footer version `0.9.1` → `0.9.2`.
- [x] Dual-tree/trigger-table registration, same convention as every prior skill addition: `.clinerules`, `.kilocoderules`, `.cursorrules`, `.openhands_instructions`, `.cursor/rules/agent-bootstrap.mdc` all gained a `show-me` trigger line next to `reply-contract`'s. Per the task's explicit instruction, these five files (plus `AGENTS.md`/`CONTRIBUTING.md`) are **not** claimed to be mechanically parsed by any test — only `skills/INDEX.md`'s `### <name>` entries are (`tests/test_index_live_binding.py`); no wording anywhere claims otherwise for this change.
- [x] `scripts/export_codex_skills.py`: new `SkillConfig` for `show-me`. `tests/test_export_codex_skills.py`: added `self.assertIn("show-me", SKILL_CONFIGS)`. Re-exported `.grok/skills/` via `python3 scripts/export_codex_skills.py --output-dir .grok/skills --force`; `git status --porcelain` after re-export showed only `.grok/skills/reply-contract/references/source.md` (expected — reply-contract's source changed) and the new `.grok/skills/show-me/` — no hand-added reference files dropped anywhere else (confirmed via `git diff --stat` on `grill-with-docs`/`close-out` `.grok` trees: empty).
- [x] Did **not**: fold show-me's recipes into `reply-contract`; run or reference `npx skills add humanlayer/skills`; copy HumanLayer's plugin directory tree or its `Bash(open ...html)` guidance; add `show-me` to `GRANDFATHERED_SKILLS`; touch `EstateGuruRepo`, `genealogy-wiki`, or `arm` (not present in this checkout — verified no such paths exist in the diff); merge or self-review the PR; add a GitHub closing keyword next to any unrelated issue.

**Verification Evidence**
- `python3 -m unittest tests.test_show_me_skill -v` (standalone): 7/7 pass.
- `python3 scripts/run_black_box_fixture.py --fixture skills/show-me/fixtures/reply-contract-link-check --skill show-me --out skills/show-me/black-box-run.json`: real captured `{"verdict": "pass", "out": "skills/show-me/black-box-run.json"}`.
- `python3 scripts/check_skill_live.py show-me`: `live-eligible: run record verdict is pass and matches the current SKILL.md` (exit `0`).
- `python3 scripts/index_skills.py`: `Every non-grandfathered INDEX.md entry is live-eligible.` (exit `0`).
- `python3 -m unittest discover -s tests` from `/workspace`: **34/34 pass** (27 pre-existing + 7 new in `test_show_me_skill.py`).
- `git diff --cached | grep -iE "reed|blair|\bkit\b|\bcos\b|wren|grok bot|claude-sonnet-5|grok-4\.6|prime agent|ipython rlm|\bdune\b|estateguru|genealogy|\barm\b"`: no matches.
- `git diff --cached --check`: only the pre-existing two-trailing-space markdown line-break convention (matches every other `**Purpose**  ` / `**Trigger**  ` line already in the repo — not a new issue).
- Branch: `cursor/show-me-native-skill-6d8c`. PR: opened as one draft PR against `main`. Not merged, not self-reviewed (per task instructions — user's own review flow owns the review).
