# skills/INDEX.md — Skill Catalog

Agent-readable index of every skill in this hub. Read this file at session start to know what is available and when to apply each skill. When a skill is triggered, **read the full skill file before executing any steps** — do not rely on session memory of its contents.

Grok users automatically receive all skills as slash commands (`/<skill-kebab-name>`) thanks to the `.grok/skills/` packaging in v0.5.0.

New cross-skill invariants (spec-gate/clarify cards, stable task names, the optional envelope stanza, no-vendoring-from-unlicensed-repos) are recorded as short numbered articles in `docs/shared/constitution.md` — read it once; this INDEX and `AGENTS.md` remain the entry points. Article 1 (spec gate) binds only the skills/personas it names under "Enforced by" (`reply-contract`, `grill-with-docs`, `agents/software-architect.md`, `AGENTS.md` §4 PLAN) — it is not a claim that every gate in the hub already uses the card; `skills/plan-code-review-workflow/SKILL.md`'s own literal PLAN-step wording is explicitly out of that article's scope.

---

## Skill Entries

### agent-orchestration-roles
**File**: `skills/agent-orchestration-roles/SKILL.md`  
**Trigger**: Orienting a new harness, or clarifying the division of labor when two or more agent harnesses (e.g. a planner/reviewer harness and an implementer harness) collaborate across manifest.yaml projects.  
**What it does**: Defines the standard planner/reviewer vs. implementer role split, the shared coordination workspace, and the plan → implement → review collaboration loop. Overlaps conceptually with `multi-harness-coordination`; use whichever framing fits your team's terminology.

---

### adversarial-coordination-workflow
**File**: `skills/adversarial-coordination-workflow/SKILL.md`  
**Trigger**: An Orchestrator (human or automated) needs to run a planner harness and an implementer harness as adversarial peers through a full plan → implement → adversarial-review → PR loop.  
**What it does**: Step A–E workflow — full-context planning gate (no production code), TDD implementation on an isolated branch, cumulative `git diff main...HEAD` adversarial review loop (max 3 iterations), then PR submission. Same underlying pattern as `multi-harness-coordination`, framed around an explicit human Orchestrator role. Includes an optional four-field envelope markdown stanza (`type`/`to`/`priority`/`task`) for handoff headers.

---

### close-out
**File**: `skills/close-out/SKILL.md`  
**Trigger**: "Close this out", "wrap this up", or after completing a multi-step implementation session. Task-scoped (contrast with `end-of-day-review`, which is day-scoped).  
**What it does**: Two-phase protocol — Phase 1 verifies memory-bank/shared-memory continuity so a fresh agent can pick up cold; Phase 2 scans the session for friction and skill gaps and proposes concrete, filed improvements (new skill / skill update / AGENTS.md rule / feedback memory / docs entry). Step 8 proposals for a new/updated skill must name a concrete `case.json`; Step 9 requires `scripts/run_black_box_fixture.py` to capture a pass and `scripts/check_skill_live.py <name>` to exit `0` before the skill is treated as live — user approval to write it is not a ship, and re-editing the file invalidates the record (stale `skill_sha256`) until re-run. `tests/test_index_live_binding.py` binds this to the real `skills/INDEX.md` listing on every test run, not just at write time.

---

### plan-code-review-workflow
**File**: `skills/plan-code-review-workflow/SKILL.md`  
**Trigger**: Any non-trivial task touching more than one file or with user-facing impact. Default workflow for all significant work.  
**What it does**: Plan → Code → Review → Iterate cycle with role switching (Architect → Engineer → QA Reviewer). Enforces TDD and expert review before finalizing.

---

### expert-pr-review
**File**: `skills/expert-pr-review/SKILL.md`  
**Trigger**: Any GitHub PR review request ("review PR #N", "look at this PR", "check this diff").  
**What it does**: 8-step review flow — gather context in parallel, resolve prior threads, checkout and build/test, security checklist, summarize findings, post review (with user approval required before posting APPROVE or REQUEST_CHANGES).

---

### triage-review-feedback
**File**: `skills/triage-review-feedback/SKILL.md`  
**Trigger**: A PR **we authored** received review feedback — human reviewer, AI reviewer, or automated scanner (Amazon Inspector, CodeQL, etc.). "Address the review on PR #N."  
**What it does**: Inventory every claim → verify each against the actual code/environment before classifying → FIX / DISMISS-with-evidence / JUDGMENT → TDD fix batch → QA pass before posting → reply to every thread, resolve, re-request review. The inverse of expert-pr-review. Every FIX also gets tagged NEW or REPEAT (same failure class already called on this repo or product family); REPEAT closes only with a mechanical check (lint, compiler diagnostic, failing-then-green test, or CI rule) added in the same fix commit — never with an instance fix or another comment/AGENTS.md/style-guide line. Worked example in-tree: `fixtures/repeat-exporter-dropped-references/`.

---

### pr-shepherd
**File**: `skills/pr-shepherd/SKILL.md`  
**Trigger**: Start of every working day; after opening/un-drafting/pushing fixes to a PR; "what's blocked?", "PR status"; or as a recurring check on merge-heavy days.  
**What it does**: Enumerates open PRs across manifest repos, classifies each (human-blocked / us-blocked / stacked / unassigned / ready), front-loads ALL reviewer-dependent asks in the first hour, proposes reviewer-free work to fill the wait, reacts fast to reviewer responses.

---

### reply-contract
**File**: `skills/reply-contract/SKILL.md`  
**Trigger**: Status after another agent finished; "your turn"; smoke / tap-through; anything the human must do or decide.  
**What it does**: Write as if they just switched projects. Loads `skills/show-me/SKILL.md` for the one visual (tree/stack/diff) — never reimplements those recipes here. Gloss or replace jargon. Leftover vs bug. Who is waiting. Photon: no mermaid/HTML unless asked. Voice/marks from Google+Apple+Red Hat (`references/style-sources.md`). Defines the spec-gate card (held artifact, binary Approve/Reject, named Documents) and the clarify card (question + Submit, never a gate), plus the stable per-thread task Name shared with `grill-with-docs` and `close-out`.

---

### show-me
**File**: `skills/show-me/SKILL.md`  
**Trigger**: "Show the shape" / "show-me" before writing code; auto-loaded by `reply-contract` for a status/your-turn reply that needs more than a one-line answer.  
**What it does**: Owns the visual recipes only — call tree, file/screen tree, stack, and a diff of those shapes, plus an opt-in mermaid recipe. One primary visual per reply; Photon/iMessage default is fenced `text` (mermaid or HTML only if the user asked); never a `Bash(open ...html)`-style command to launch a generated visual. Distinct from `diagram-design` (persisted spec diagrams), `scroll-craft` (prose craft), a Hermes-style humanizer (tone rewrite), and `grill-with-docs` (question rounds before code). Credits the idea behind HumanLayer/Dex Horthy's `show-me` (MIT-licensed concept) — independent rewrite, no copied plugin tree or HTML-open guidance.

---

### codebase-simplification-audit
**File**: `skills/codebase-simplification-audit/SKILL.md`  
**Trigger**: Whole-repo audit for simpler data structures / state / ownership; "codebase simplification audit"; paste of the Aaron Francis audit gist.  
**What it does**: Read-only coordinator + bounded workers. Inventory every subsystem, ≤2 material recs or skip, verify, audit the audit, ranked report. **Hard rule:** no edits, tests, implement skills, commits, or pushes until the user accepts a recommendation. Ownership-boundary rows may frame findings with the Architectural Review Phases checklist names (UI/Core Separation, Dependency Rule, Information Hiding And Encapsulation, Local Code Quality — see `agents/software-architect.md`).

---

### grill-with-docs
**File**: `skills/grill-with-docs/SKILL.md`  
**Trigger**: “Grill this”, align on a plan/design before code, build or update CONTEXT.md.  
**What it does**: Round-based interview (facts vs decisions). Writes glossary-only `CONTEXT.md` as terms resolve; offers ADRs only for hard-to-reverse trade-offs. **Hard rule:** no implement skills until the user confirms shared understanding. Final confirm uses `reply-contract`'s spec-gate card; a single blocking fact-question mid-round uses its clarify card instead.

---

### end-of-day-review
**File**: `skills/end-of-day-review/SKILL.md`  
**Trigger**: End of every working day ("wrap up the day", "EOD", "plan tomorrow") or before an extended break.  
**What it does**: Evidence-based review of the day's outcomes (live gh state, not session memory) → capture learnings → memory-bank update + compaction → write tomorrow's plan with reviewer-dependent asks queued first → optional mem0 sync.

---

### multi-harness-coordination
**File**: `skills/multi-harness-coordination/SKILL.md`  
**Trigger**: Coordinating a task across two or more agent harnesses; "run the multi-harness workflow"; parent agent routing between planner and implementer harnesses.  
**What it does**: Abstract role map (planner/reviewer vs implementer vs orchestrator) + Steps A–E workflow — full-context planning gate, TDD implementation on isolated branch, adversarial review loop with cumulative `git diff`, optional mem0 handoffs, PR submission. Includes an optional four-field envelope markdown stanza (`type`/`to`/`priority`/`task`) for handoff headers.

---

### task-loop-7-phase
**File**: `skills/task-loop-7-phase/SKILL.md`
**Trigger**: User invokes the 7-Phase Algorithm, TaskLoopState, or an OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN workflow.
**What it does**: Strict seven-phase loop with phase transitions, mem0 TaskLoopState updates, measurable success criteria, automated/live verification, and structured lesson capture with optional company-wiki curation.

---

### write-tests
**File**: `skills/write-tests/SKILL.md`  
**Trigger**: Writing any new feature, fixing a bug, or refactoring existing code — invoke *before* writing production code. Also invoke when a PR review flags missing tests.  
**What it does**: Step-by-step Red/Green/Refactor TDD playbook with framework commands for Jest, Bun test, and pytest. Includes mocking decision guide, retrofitting guide for legacy code, extraction-refactor characterization guide, and common mistake table. Implements `docs/shared/tdd-standard.md`.

---

### debug-investigation
**File**: `skills/debug-investigation/SKILL.md`  
**Trigger**: User reports a bug, unexpected behavior, or asks to "fix" something without a clear diagnosis. Also invoke for flaky test investigation.  
**What it does**: Reproduce → Isolate (git bisect / binary call-stack search) → Write failing test → Fix → Verify. Stack-specific tips for Node.js inspector, queue debugging, database `EXPLAIN ANALYZE`, pytest `--pdb`, and React DevTools.

---

### performance-profiling
**File**: `skills/performance-profiling/SKILL.md`  
**Trigger**: User says "slow", "latency", "timeout", "optimize", "taking too long", or complains about response time. Also invoke when monitoring shows p95/p99 spikes.  
**What it does**: Define target metric → Measure baseline (clinic.js, EXPLAIN ANALYZE, queue job timing, React DevTools Profiler, py-spy, CloudWatch) → Identify bottleneck type → Fix one thing → Measure again. Includes bottleneck classification table.

---

### feature-flag-lifecycle
**File**: `skills/feature-flag-lifecycle/SKILL.md`  
**Trigger**: Creating a feature flag, enabling a flag for rollout, or cleaning up / graduating a flag. Also invoke during any PR review that introduces a conditional code path labeled as a flag.  
**What it does**: Create (naming convention, default-off, cleanup date required) → Roll out (staged: internal → beta → gradual → GA) → Graduate (remove flag and dead code path). Includes open-flag tracking table in `memory-bank/progress.md`.

---

### cherry-pick-to-release-branch
**File**: `skills/cherry-pick-to-release-branch/SKILL.md`  
**Trigger**: User needs to hotfix or backport a merged PR to a release branch (`releases/YYYY.MM.DD`).  
**What it does**: Fetch and checkout release branch → identify PR commits → cherry-pick in order → bump RC version suffix → push. Parameters: RELEASE_BRANCH, PR_NUMBER, VERSION_FILES.

---

### memory-bank-protocol
**File**: `skills/memory-bank-protocol/SKILL.md`  
**Trigger**: Session start (always), switching projects via manifest.yaml, onboarding a new project, or any significant task completion (to update the bank).  
**What it does**: Lean tiered read protocol — hot files (activeContext + progress) every session; foundation files conditionally. Optional mem0 integration, end-of-task update rules, evidence rule (status claims must cite SHA/PR/log), and compaction rule (activeContext ≤ ~150 lines, archive superseded sections).

---

### docs-protocol
**File**: `skills/docs-protocol/SKILL.md`  
**Trigger**: Creating or updating technical documentation, adding an ADR, or updating `docs/projects/<name>/` or `docs/shared/`.  
**What it does**: Full playbook for the two-layer docs model (`docs/shared/` vs `docs/projects/<name>/`), how to create and update ADRs, and how agents reference docs via the `docs_path` field in manifest.yaml.

---

### subagent-routing
**File**: `skills/subagent-routing/SKILL.md`  
**Trigger**: Before any task with independent subtasks, parallelizable work, or when selecting a model for a spawned agent. Always consult when deciding whether to delegate or run inline.  
**What it does**: Mandates subagent delegation for parallelizable/isolatable work. Defines model selection table: Haiku for non-logic tasks (reads, searches, formatting, summarization), Sonnet for code, analysis, and judgment. Includes worktree isolation Rule 3, decomposition checklist, parallel spawn examples, and common mistakes.

---

### delegation-patterns
**File**: `skills/delegation-patterns/SKILL.md`  
**Trigger**: Planning how to delegate work across subagents in Claude Code or Grok, selecting the right model, or designing parallel execution with worktree isolation.  
**What it does**: Three canonical delegation patterns (parallel analysis, isolated parallel edits, two-tier pipeline) with mandatory worktree isolation for editing agents on shared checkouts.

---

### black-box-agent-qa
**File**: `skills/black-box-agent-qa/SKILL.md`  
**Trigger**: Before treating any change to an agent persona, harness config/wiring, verb/command, or skill file as tested, passing, or ready to ship. Required by `close-out` Step 9 before a new or edited skill goes live.  
**What it does**: Name a literal input fixture as `fixtures/<case-name>/case.json` (schema: `SCHEMA.md`; a generic subprocess argv/exit-code/stdout contract, with a non-`unittest` worked example in `fixtures/check-skill-live-cli/`), actually run it with `scripts/run_black_box_fixture.py`, and write a captured run record (`skills/<name>/black-box-run.json`). Reading the PR or the skill Markdown is not a pass; a suite that only mocks the system under test is not sufficient proof on its own. An environment-blocked run escalates (`"verdict": "blocked"`) — it never counts as a pass. `scripts/check_skill_live.py` reads the run record's `skill_sha256` to detect a stale record (the skill edited since capture, including a silent trajectory refine) and refuses to call it live until re-run; never authorizes auto-merge.

---

### evidence-packet-protocol
**File**: `skills/evidence-packet-protocol/SKILL.md`  
**Trigger**: After an implementer/QA-Tester turn needing checkable evidence of what actually works; before a planner starts the next iteration and must read the prior evidence packet.  
**What it does**: Defines `E_t.json` — a claim-bound evidence packet with a required `head_sha` freeze binding (GB-4), `qa_status`/record `status` restricted to `verified | gap` only at both levels (GB-1/GB-6, never partial/blocked/"looks good"), non-empty typed `execution_records` (`screenshot | runtime_trace | fixture`, GB-1), structural gap-repair-and-new-capability rules (GB-3), a forbidden living-PII check, and the `evidence/E_t.json` (current) vs. `evidence/E_<n>.json` (priors) path convention the next planner must read (H-1), never a full-dump `evidence/INDEX.md` (H-5). Real validators: `scripts/validate_evidence_packet.py`, `scripts/check_planner_reads_et.py`, `scripts/check_evidence_index_is_progressive.py` (schema: `SCHEMA.md`).

---

### preservation-gate
**File**: `skills/preservation-gate/SKILL.md`  
**Trigger**: Writing or reviewing a `Dt` (plan/development document) for iteration 2 or later of a warm-started, evidence-driven workflow.  
**What it does**: Defines the exact `## Preservation Gate` heading — a required section listing the previous iteration's verified claims the Developer must not regress. Explicitly distinct from REPEAT (positive/never-closes vs. negative/mechanically-closed — see the skill's comparison table). Real validator: `scripts/validate_preservation_gate.py`. One-line pointer lives in `skills/multi-harness-coordination/SKILL.md`; `skills/reply-contract/SKILL.md` is not touched.

---

## Adding a New Skill

1. Create `skills/<name>/SKILL.md` following the style of existing skills: YAML frontmatter (`name`, `description`, `version`; quote the description or avoid inner `: ` — unquoted YAML breaks on colon+space), then purpose, trigger, when to use, numbered steps, stack-specific tips, last updated footer.
2. **Gate before any listing below**: write a `fixtures/<case-name>/case.json` for the skill (schema: `skills/black-box-agent-qa/SCHEMA.md`), run `python3 scripts/run_black_box_fixture.py --fixture <dir> --skill <name> --out skills/<name>/black-box-run.json`, then confirm `python3 scripts/check_skill_live.py <name>` exits `0`. A skill with no passing, current run record is not discoverable yet — do not proceed to step 3 until this gate is green. See `skills/close-out/SKILL.md` Step 9 for the same sequence when the skill came from a close-out proposal.
3. Add an entry to this INDEX.md. **This is enforced, not just instructed**: `tests/test_index_live_binding.py::test_every_non_grandfathered_index_entry_is_live` re-checks every `###` entry here against `scripts/check_skill_live.py` on every test run — listing a skill here with no current pass fails that test (see `scripts/index_skills.py`). Do not add the new skill's name to `GRANDFATHERED_SKILLS` to route around a failure; that allowlist is only for the 20 skills that predate this gate (2026-08-26) and a new skill must gate at write time via step 2.
4. Add a one-line entry to AGENTS.md §4 "Other Key Skills" with trigger.
5. Update `.clinerules`, `.kilocoderules`, `.cursorrules`, `.openhands_instructions`, and `.cursor/rules/agent-bootstrap.mdc` to include the new skill in the skill-trigger lists.
6. Add a `SkillConfig` entry in `scripts/export_codex_skills.py` (the exporter hard-fails on missing configs), run `python3 -m unittest tests.test_export_codex_skills`, then re-export: `python3 scripts/export_codex_skills.py --output-dir .grok/skills --force`.
7. If any later edit changes `SKILL.md`, re-run step 2 before the edit ships — `check_skill_live.py` (and therefore `tests/test_index_live_binding.py`) will fail on the stale `skill_sha256` until you do.

*Last updated: 2026-09-02 | Hub version: 0.10.0*
