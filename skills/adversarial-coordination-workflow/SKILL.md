---
name: adversarial-coordination-workflow
description: "This skill defines an authoritative multi-agent coordination workflow where a human or automated Orchestrator directs a planning/reviewing harness and an implementing harness as adversarial peers. It ensures extreme code quality, complete test coverage, and security audit alignment before any PR is created or merged."
version: 1.0.0
---

# Adversarial Agent Coordination Workflow

This skill establishes a standardized division of labor and coordination workspace for autonomous agents collaborating on a change. It ensures the planner/reviewer harness and the implementer harness cooperate as adversarial peers rather than rubber-stamping each other's work.

## Workspace & Context

- **Root Directory:** Resolve the coordination root from `manifest.yaml`.
- **Memory Hub:** `agent-bootstrap` (holding cross-agent skills, standard rules, and project-wide context).
- **Shared Memory Bus:** If configured (e.g. mem0), use it as the primary data layer for routing plans, task states, and review approvals between harnesses.

---

## Workflow Sequence (the Orchestrator's Loop)

```
                  ┌────────────────────────────────────────┐
                  │      1. User requests a change         │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │ 2. Step A: Planner harness (Plan mode) │
                  │    Creates plan & writes to shared mem │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │ 3. Step B: Implementer harness (Exec)  │
                  │    Implements code/TDD on branch       │
                  └───────────────────┬────────────────────┘
                                      │
               ┌──────────────────────┴────────────────────┐
               ▼                                           ▼
┌──────────────────────────────┐            ┌──────────────────────────────┐
│  Adversarial Loop: Step C    │            │  Adversarial Loop: Step D    │
│  Planner reviews disk/commits│◄──────────►│  Implementer resolves gaps   │
│  for bugs, security, & tests │            │  until approved by planner   │
└──────────────────────────────┘            └──────────────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │ 4. Step E: Planner harness (PR Create) │
                  │    Creates and submits the GitHub PR   │
                  └────────────────────────────────────────┘
```

### Step A: The Planning Gate (Planner harness)
- **Action:** Ask the planner harness to design the implementation plan for the target issue.
- **Rules:**
  - **Full Context Pulling**: Before starting the planning phase for an issue, the Orchestrator MUST pull the *entire* issue description plus any existing implementation plans, memory-bank records, and shared-memory history related to that issue (from your tracker, wiki, or docs — whatever is available). Bundle this pre-fetched context and pass it to the planner harness as the initial context pool. This ensures the harness starts with a complete system understanding, does not over-claim completion on partial implementations, is strictly audited against the full issue criteria, and avoids wasting reasoning steps rebuilding context from scratch.
  - The planner harness must check the codebase, analyze dependencies, and write a concrete plan based on the *full* description and surrounding context.
  - The planner harness must publish this plan to shared memory (if configured) under a handoff-type entry.
  - The planner harness must NOT write or modify any production code during this step.

### Step B: The Implementation Gate (Implementer harness)
- **Action:** Ask the implementer harness to implement the changes on a dedicated git branch, noting the availability of the plan in shared memory.
- **Rules:**
  - The implementer harness must retrieve the plan from shared memory (or read it directly if no shared-memory layer is configured).
  - The implementer harness must strictly follow the **TDD Red/Green/Refactor standard** (failing test first, then minimal passing code, then refactor).
  - The implementer harness must write code, run local test suites, and commit changes locally.
  - **The implementer harness must NOT attempt to create or submit a pull request.**

### Step C & D: The Adversarial Review & Iteration Loop
- **Action:** The Orchestrator runs the planner harness to review the changes made on disk by the implementer harness.
- **Rules for Diff Review:**
  - **Do NOT review blindly:** The planner harness must always review the *cumulative* branch changes rather than just the latest commit. The canonical diff command is:
    ```bash
    git diff main...HEAD
    ```
    This compares the tip of the feature branch directly to the common ancestor of `main`, ensuring intermediate commits are not overlooked.
- **The Adversarial Roleplay:**
  - **Planner harness (The Auditor):** Acts as a highly critical, adversarial QA and Security Auditor. Its goal is to find bugs, security flaws, missing test assertions, edge cases, and style deviations in the implementer's commits. It writes its findings and code corrections back to shared memory (or directly to the user if no shared-memory layer is configured).
  - **Implementer harness (The Implementer):** Acts as an agile, defense-minded Software Engineer. Its goal is to resolve the auditor's findings, fix bugs, add missing test coverage, and write robust code.
- **Iteration Limit:** The loop continues until the planner harness returns a clear `APPROVE` verdict, or for a maximum of 3 iterations (to prevent infinite loops).

### Step E: Pull Request Submission (Planner harness)
- **Action:** Once both agents approve, the Orchestrator runs the planner harness to create and submit the GitHub PR.
- **Rules:**
  - The planner harness drafts the PR title and description based on the final implemented state.
  - The planner harness pushes the branch and creates the PR via the `gh pr create` CLI.

---

## Optional: four-field envelope stanza

When publishing a plan or finding to shared memory (Step A) or writing a handoff note for the implementer/planner (Steps B–D), lead with a four-field markdown stanza — idea only, from a Scout memo comparing swarm-forge's inter-agent envelope format against this hub (`unclebob/swarm-forge`, no files/scripts copied; that repo has no LICENSE):

```text
> type: handoff
> to: Engineer
> priority: normal
> task: <stable-task-name>
```

- `type` — `handoff`, `review`, `finding`, or similar; keep the vocabulary small.
- `to` — the receiving role or harness.
- `priority` — `low` / `normal` / `high`.
- `task` — the thread's stable task Name (see `reply-contract` "Task name"), unchanged for the thread's life.

This is a descriptive markdown header, not a message-bus contract. Explicitly **not** adopted from swarm-forge: `merge_and_process` semantics, 10-char SHA identity, outbox file paths, helper `TASK:`/`NO_TASK` stdout conventions, or auto-generated envelope bodies.

---

## Operational Guidelines for the Orchestrator

1. **Be the Router:** You are the air traffic controller. Do not write code or design solutions directly. Move the active context, git branch state, and shared-memory pointers between the two agents.
2. **Setup the Branch First:** Before starting Step B, ensure a clean branch is created from `main` (e.g., `feature/issue-<ID>`) so both agents are isolated and working on the exact same commit history.
3. **Verify Git State:** Run `git status` and `git diff` after each agent's turn to understand precisely what has been modified on disk.

*Last updated: 2026-08-22*
