---
name: task-loop-7-phase
description: "This skill should be used when a task should follow the strict 7-Phase Algorithm: OBSERVE, THINK, PLAN, BUILD, EXECUTE, VERIFY, LEARN, with mem0 TaskLoopState updates after each phase, measurable success criteria, automated/live verification, structured Lesson memory in mem0, and optional company-wiki curation when wiki tools are available."
version: 1.0.0
---

# task-loop-7-phase.md — Observe/Think/Plan/Build/Execute/Verify/Learn Loop

**Purpose**
Run substantial agent work through a strict seven-phase loop that gathers current
state, reasons from first principles, plans with measurable criteria, builds,
executes, verifies, and captures reusable lessons.

This is the default loop when the user asks for the "7-Phase Algorithm",
"TaskLoopState", "observe think plan build execute verify learn", or a
verification-and-learning workflow that must update mem0 and the company wiki.

**When to Use This Skill**
- A user explicitly invokes the 7-Phase Algorithm or TaskLoopState.
- A task has enough risk that success criteria and explicit verification need to
  be tracked across phases.
- Multi-harness work needs phase-by-phase handoff state in mem0.
- A completed task should produce reusable lessons, not just a final summary.

---

## Non-Negotiable Rules

- Follow phases strictly in order. Do not skip a phase.
- Output clear phase transitions: `Phase X complete -> Phase Y`.
- Update `TaskLoopState` in mem0 after each phase, or at minimum after VERIFY
  and LEARN if the task is short.
- In LEARN, always search mem0 for similar past tasks before writing a lesson.
- Keep long-task continuation summaries tight: phase, state, blockers, next
  action.
- Use automated verification before memory-derived or manual verification.
- Curate high-value insights into the company wiki when Hermes/wiki tools are
  available; otherwise record the wiki update as a follow-up in `TaskLoopState`.

---

## TaskLoopState Shape

Store compact state in mem0 with `metadata.type = "task_loop_state"`:

```text
TaskLoopState:
task: <short task name>
phase: <OBSERVE|THINK|PLAN|BUILD|EXECUTE|VERIFY|LEARN|COMPLETE>
success_criteria:
- <measurable criterion>
evidence:
- <command, SHA, PR, log line, test result, or wiki link>
blockers:
- <blocker or "none">
next_action: <one concrete next action>
```

Prefer one state update per phase over a long transcript. Evidence must be
specific enough for another harness to resume without trusting chat history.

---

## Phase 1: OBSERVE

Gather current state and relevant past context.

1. Read the task request and identify the active repository/project.
2. Load required project context: AGENTS.md, hot memory-bank files, manifest, and
   the relevant skill files.
3. Search mem0 for similar tasks, prior lessons, current coordination bus state,
   and known traps.
4. Inspect live state with tools: git status, relevant files, issues/PRs, CI,
   logs, docs, or environment facts.
5. Update `TaskLoopState` with observed facts, evidence, and uncertainties.

Transition: `Phase OBSERVE complete -> Phase THINK`

---

## Phase 2: THINK

Reason before planning.

1. State the problem in first-principles terms.
2. Identify risks, constraints, assumptions, and likely failure modes.
3. Consider alternatives, including doing less, sequencing differently, or using
   an existing workflow.
4. Decide the minimal viable approach and why it is preferable.
5. Update `TaskLoopState` with the selected approach and rejected alternatives.

Transition: `Phase THINK complete -> Phase PLAN`

---

## Phase 3: PLAN

Create concrete steps and measurable success criteria.

1. Break the work into ordered steps.
2. Define success criteria that can be checked in VERIFY.
3. Identify required tests, commands, reviews, or external evidence.
4. Name rollback/stop conditions for risky work.
5. Update `TaskLoopState` with the plan and success criteria.

Transition: `Phase PLAN complete -> Phase BUILD`

---

## Phase 4: BUILD

Implement the plan using the appropriate tools and harnesses.

1. Make the smallest changes that satisfy the plan.
2. Follow TDD for code changes: failing test first, then implementation, then
   refactor.
3. Preserve user changes and avoid unrelated refactors.
4. Keep a concise implementation note for handoff.
5. Update `TaskLoopState` with changed files and build status.

Transition: `Phase BUILD complete -> Phase EXECUTE`

---

## Phase 5: EXECUTE

Run the planned commands or workflow.

1. Run the focused tests, scripts, deployments, or operational commands named in
   PLAN.
2. Capture exact outputs that matter: pass/fail status, IDs, SHAs, URLs, log
   snippets, timestamps, or generated artifacts.
3. If execution fails, record the failure, return to THINK or PLAN only after
   stating why the loop needs another iteration.
4. Update `TaskLoopState` with execution evidence.

Transition: `Phase EXECUTE complete -> Phase VERIFY`

---

## Phase 6: VERIFY

Check results against the PLAN success criteria.

1. Verify every success criterion explicitly.
2. Use automated checks first: tests, typechecks, linters, CI, health checks,
   assertions, or scripts.
3. Use live-state checks next: git diff/status, PR state, logs, database reads,
   cloud state, rendered artifacts, or browser checks.
4. Use mem0 recall of similar past verifications only after automated/live checks,
   and mark it as memory-derived if not reverified.
5. Update `TaskLoopState` with pass/fail per criterion and remaining risk.

Transition: `Phase VERIFY complete -> Phase LEARN`

---

## Phase 7: LEARN

Turn the task into durable process memory.

1. Search mem0 for similar past tasks and lessons.
2. Extract concrete lessons: what changed, what trap was avoided, what command or
   workflow should be reused, and what should be done differently next time.
3. Write a structured Lesson memory to mem0 with `metadata.type = "task_learning"`.
4. Curate high-value insights into the company wiki via Hermes/wiki tools when
   available. If the tools are unavailable, record the intended wiki update in
   `TaskLoopState.next_action`.
5. Update the memory bank or docs only when the learning changes durable project
   state, a workflow, or a technical reference.
6. Set `TaskLoopState.phase` to `COMPLETE`, or propose the next loop iteration
   with its starting phase and success criteria.

Transition: `Phase LEARN complete -> COMPLETE`

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Treating OBSERVE as a quick skim | Use tools and mem0 before reasoning |
| Planning without measurable criteria | Add criteria that VERIFY can check |
| Calling execution success verification | EXECUTE runs; VERIFY compares to criteria |
| Writing lessons before searching memory | Search similar tasks first, then write the new lesson |
| Updating chat but not TaskLoopState | Store compact state in mem0 so other harnesses can resume |
| Hand-waving wiki updates | Use Hermes/wiki tools when available or record an explicit follow-up |

---

Last updated: 2026-06-23
