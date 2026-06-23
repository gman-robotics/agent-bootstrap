# skills/INDEX.md — Skill Catalog

Agent-readable index of every skill in this hub. Read this file at session start to know what is available and when to apply each skill. When a skill is triggered, **read the full skill file before executing any steps** — do not rely on session memory of its contents.

Grok users automatically receive all skills as slash commands (`/<skill-kebab-name>`) thanks to the `.grok/skills/` packaging in v0.5.0.

---

## Skill Entries

### plan-code-review-workflow.md
**File**: `skills/plan-code-review-workflow.md`  
**Trigger**: Any non-trivial task touching more than one file or with user-facing impact. Default workflow for all significant work.  
**What it does**: Plan → Code → Review → Iterate cycle with role switching (Architect → Engineer → QA Reviewer). Enforces TDD and expert review before finalizing.

---

### expert-pr-review.md
**File**: `skills/expert-pr-review.md`  
**Trigger**: Any GitHub PR review request ("review PR #N", "look at this PR", "check this diff").  
**What it does**: 8-step review flow — gather context in parallel, resolve prior threads, checkout and build/test, security checklist, summarize findings, post review (with user approval required before posting APPROVE or REQUEST_CHANGES).

---

### triage-review-feedback.md
**File**: `skills/triage-review-feedback.md`  
**Trigger**: A PR **we authored** received review feedback — human reviewer, AI reviewer, or automated scanner (Amazon Inspector, CodeQL, etc.). "Address the review on PR #N."  
**What it does**: Inventory every claim → verify each against the actual code/environment before classifying → FIX / DISMISS-with-evidence / JUDGMENT → TDD fix batch → QA pass before posting → reply to every thread, resolve, re-request review. The inverse of expert-pr-review.

---

### pr-shepherd.md
**File**: `skills/pr-shepherd.md`  
**Trigger**: Start of every working day; after opening/un-drafting/pushing fixes to a PR; "what's blocked?", "PR status"; or as a recurring check on merge-heavy days.  
**What it does**: Enumerates open PRs across manifest repos, classifies each (human-blocked / us-blocked / stacked / unassigned / ready), front-loads ALL reviewer-dependent asks in the first hour, proposes reviewer-free work to fill the wait, reacts fast to reviewer responses.

---

### end-of-day-review.md
**File**: `skills/end-of-day-review.md`  
**Trigger**: End of every working day ("wrap up the day", "EOD", "plan tomorrow") or before an extended break.  
**What it does**: Evidence-based review of the day's outcomes (live gh state, not session memory) → capture learnings → memory-bank update + compaction → write tomorrow's plan with reviewer-dependent asks queued first → optional mem0 sync.

---

### multi-harness-coordination.md
**File**: `skills/multi-harness-coordination.md`  
**Trigger**: Coordinating a task across two or more agent harnesses; "run the multi-harness workflow"; parent agent routing between planner and implementer harnesses.  
**What it does**: Abstract role map (planner/reviewer vs implementer vs orchestrator) + Steps A–E workflow — full-context planning gate, TDD implementation on isolated branch, adversarial review loop with cumulative `git diff`, optional mem0 handoffs, PR submission.

---

### task-loop-7-phase.md
**File**: `skills/task-loop-7-phase.md`
**Trigger**: User invokes the 7-Phase Algorithm, TaskLoopState, or an OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN workflow.
**What it does**: Strict seven-phase loop with phase transitions, mem0 TaskLoopState updates, measurable success criteria, automated/live verification, and structured lesson capture with optional company-wiki curation.

---

### write-tests.md
**File**: `skills/write-tests.md`  
**Trigger**: Writing any new feature, fixing a bug, or refactoring existing code — invoke *before* writing production code. Also invoke when a PR review flags missing tests.  
**What it does**: Step-by-step Red/Green/Refactor TDD playbook with framework commands for Jest, Bun test, and pytest. Includes mocking decision guide, retrofitting guide for legacy code, extraction-refactor characterization guide, and common mistake table. Implements `docs/shared/tdd-standard.md`.

---

### debug-investigation.md
**File**: `skills/debug-investigation.md`  
**Trigger**: User reports a bug, unexpected behavior, or asks to "fix" something without a clear diagnosis. Also invoke for flaky test investigation.  
**What it does**: Reproduce → Isolate (git bisect / binary call-stack search) → Write failing test → Fix → Verify. Stack-specific tips for Node.js inspector, queue debugging, database `EXPLAIN ANALYZE`, pytest `--pdb`, and React DevTools.

---

### performance-profiling.md
**File**: `skills/performance-profiling.md`  
**Trigger**: User says "slow", "latency", "timeout", "optimize", "taking too long", or complains about response time. Also invoke when monitoring shows p95/p99 spikes.  
**What it does**: Define target metric → Measure baseline (clinic.js, EXPLAIN ANALYZE, queue job timing, React DevTools Profiler, py-spy, CloudWatch) → Identify bottleneck type → Fix one thing → Measure again. Includes bottleneck classification table.

---

### feature-flag-lifecycle.md
**File**: `skills/feature-flag-lifecycle.md`  
**Trigger**: Creating a feature flag, enabling a flag for rollout, or cleaning up / graduating a flag. Also invoke during any PR review that introduces a conditional code path labeled as a flag.  
**What it does**: Create (naming convention, default-off, cleanup date required) → Roll out (staged: internal → beta → gradual → GA) → Graduate (remove flag and dead code path). Includes open-flag tracking table in `memory-bank/progress.md`.

---

### cherry-pick-to-release-branch.md
**File**: `skills/cherry-pick-to-release-branch.md`  
**Trigger**: User needs to hotfix or backport a merged PR to a release branch (`releases/YYYY.MM.DD`).  
**What it does**: Fetch and checkout release branch → identify PR commits → cherry-pick in order → bump RC version suffix → push. Parameters: RELEASE_BRANCH, PR_NUMBER, VERSION_FILES.

---

### memory-bank-protocol.md
**File**: `skills/memory-bank-protocol.md`  
**Trigger**: Session start (always), switching projects via manifest.yaml, onboarding a new project, or any significant task completion (to update the bank).  
**What it does**: Lean tiered read protocol — hot files (activeContext + progress) every session; foundation files conditionally. Optional mem0 integration, end-of-task update rules, evidence rule (status claims must cite SHA/PR/log), and compaction rule (activeContext ≤ ~150 lines, archive superseded sections).

---

### docs-protocol.md
**File**: `skills/docs-protocol.md`  
**Trigger**: Creating or updating technical documentation, adding an ADR, or updating `docs/projects/<name>/` or `docs/shared/`.  
**What it does**: Full playbook for the two-layer docs model (`docs/shared/` vs `docs/projects/<name>/`), how to create and update ADRs, and how agents reference docs via the `docs_path` field in manifest.yaml.

---

### subagent-routing.md
**File**: `skills/subagent-routing.md`  
**Trigger**: Before any task with independent subtasks, parallelizable work, or when selecting a model for a spawned agent. Always consult when deciding whether to delegate or run inline.  
**What it does**: Mandates subagent delegation for parallelizable/isolatable work. Defines model selection table: Haiku for non-logic tasks (reads, searches, formatting, summarization), Sonnet for code, analysis, and judgment. Includes worktree isolation Rule 3, decomposition checklist, parallel spawn examples, and common mistakes.

---

### delegation-patterns.md
**File**: `skills/delegation-patterns.md`  
**Trigger**: Planning how to delegate work across subagents in Claude Code or Grok, selecting the right model, or designing parallel execution with worktree isolation.  
**What it does**: Three canonical delegation patterns (parallel analysis, isolated parallel edits, two-tier pipeline) with mandatory worktree isolation for editing agents on shared checkouts.

---

## Adding a New Skill

1. Create `skills/<name>.md` following the style of existing skills (purpose, trigger, when to use, numbered steps, stack-specific tips, last updated footer).
2. Add an entry to this INDEX.md.
3. Add a one-line entry to AGENTS.md §4 "Other Key Skills" with trigger.
4. Update `.clinerules`, `.kilocoderules`, `.cursorrules`, `.openhands_instructions`, and `.cursor/rules/agent-bootstrap.mdc` to include the new skill in the skill-trigger lists.
5. Add a `SkillConfig` entry in `scripts/export_codex_skills.py` (the exporter hard-fails on missing configs), run `python3 -m unittest tests.test_export_codex_skills`, then re-export: `python3 scripts/export_codex_skills.py --output-dir .grok/skills --force`.

*Last updated: 2026-06-15 | Hub version: 0.5.0*
