---
name: multi-harness-coordination
description: "This skill should be used when multiple agent harnesses (Claude Code, Codex, Cline, etc.) are collaborating on the same repository and need a shared role assignment and an adversarial plan/implement/review loop. Defines cross-harness role assignment and the coordination workspace conventions for handing work between harnesses."
version: 1.0.0
---

# multi-harness-coordination.md — Cross-Harness Role Assignment & Adversarial Implementation Workflow

**Purpose**
Coordinate work across **two or more agent harnesses** when planning/review quality benefits from separating those roles from implementation. The parent agent (or human) acts as **orchestrator** — routing context, branch state, and handoffs — without writing production code directly.

This skill complements `plan-code-review-workflow.md`, which assumes one harness switches roles inline. Use this skill when, for example, Claude Code plans and reviews while Codex implements, or Grok's parent session routes to `task(Engineer)` for TDD work.

**When to Use**
- Coordinating a task across multiple harnesses ("run the multi-harness workflow")
- A team has designated planner/reviewer and implementer harnesses
- Quality gates require adversarial review before PR submission
- At session start when establishing which harness owns which role (§1)

---

## §1 Harness Roles

### Coordination workspace

Resolve from `manifest.yaml`:
- **Hub**: `agent-bootstrap/` (skills, AGENTS.md, shared rules)
- **Project repos**: each `projects[].path`, resolved to absolute paths from the manifest location

All harnesses read canonical skills from `skills/*.md` in the hub — never fork playbooks per harness.

### Abstract role map

Configure your team's harness names in the table below. One harness should not own plan + implement + final adversarial review on the same change when this workflow is in use.

| Abstract role | Duties | Example harnesses |
|---|---|---|
| **Planner / Reviewer** | Full-context planning, adversarial QA, security audit, PR narrative | Claude Code (parent), Grok (parent), Architect agent |
| **Implementer** | TDD code changes on an isolated branch; no PR creation | Codex CLI, Grok `task(Engineer)`, Cline implement mode |
| **Orchestrator** | Routes context and git state between harnesses; verifies git after each turn | Parent agent session or human operator |

### Collaboration loop (overview)

```
User/Orchestrator initiates
        ↓
Planner: design + publish plan (Step A)
        ↓
Implementer: TDD on branch (Step B)
        ↓
Adversarial loop: Planner audits ↔ Implementer fixes (Steps C/D)
        ↓
Planner/Orchestrator: open PR (Step E)
```

### Optional mem0 handoff bus

When mem0 is configured, publish plans (`type: "handoff"`), review findings, and iteration state to `run_id: coord-YYYYMMDD`. When not configured, use `memory-bank/activeContext.md` under a `## Multi-Harness Handoff` section and tell the next harness which file to read.

---

## §2 Coordination Workflow (Steps A–E)

### Prerequisites

1. Target issue or task identified (GitHub issue, memory-bank plan, or user request).
2. Clean feature branch from default branch: `feature/<task-id>` (orchestrator creates before Step B).
3. **Worktree isolation** if the shared checkout may be in use — see `subagent-routing.md` Rule 3 and `delegation-patterns.md` Pattern 2.

---

### Step A: Planning Gate (Planner harness)

**Action:** Planner designs the implementation plan. **No production code.**

**Full-context pull (mandatory before planning):**
1. Full task description — `gh issue view <N>` for GitHub issues, or the user's complete request
2. Existing plans — `memory-bank/activeContext.md`, `docs/projects/<name>/decisions.md`, prior ADRs
3. Hot memory-bank files for the target project
4. **If mem0 configured:** semantic search + today's coordination bus for prior work on this task

**Rules:**
- Plan against the **entire** task scope — not a convenient subset. Partial plans lead to false "complete" claims.
- Publish the plan to mem0 (`type: "handoff"`) or `activeContext.md` before Step B.
- Planner does **not** modify production code in this step.

---

### Step B: Implementation Gate (Implementer harness)

**Action:** Implementer executes the approved plan on the feature branch.

**Rules:**
- Retrieve the plan from mem0 or `activeContext.md` — do not rely on chat history.
- Follow **TDD Red/Green/Refactor** (`write-tests.md`) — failing test before production code.
- Run the relevant test suite; commit locally.
- Implementer does **not** create or submit the pull request.

---

### Steps C & D: Adversarial Review & Iteration Loop

**Action:** Orchestrator runs the Planner harness to audit implementer's branch; Implementer resolves findings.

**Cumulative diff (mandatory):**
```bash
git diff <default-branch>...HEAD
```
Review the **full branch delta**, not just the latest commit. Intermediate commits are easy to miss.

**Adversarial posture:**
- **Planner (auditor):** Critical QA + security lens. Find bugs, missing tests, edge cases, style deviations. Publish findings to mem0 or `activeContext.md`.
- **Implementer:** Fix findings with TDD; re-run tests after each batch.

**Iteration limit:** Continue until Planner returns `APPROVE`, or **maximum 3 rounds** (then escalate to the user).

For review semantics, align with `expert-pr-review.md` (read-only on the branch) and `write-tests.md` for fix batches.

---

### Step E: Pull Request Submission (Planner or Orchestrator)

**Action:** Once approved, Planner or orchestrator opens the PR.

**Rules:**
- PR title and body reflect the **final** implemented state (cite test evidence, link issue).
- Push branch, then `gh pr create` (or equivalent).
- User confirmation before push if not already authorized.

Some teams prefer the human to open the PR — note that in project docs and skip automated Step E.

---

## Orchestrator Checklist

1. **Be the router** — move context, branch pointers, and handoff artifacts; do not implement or design solutions directly.
2. **Branch first** — create `feature/<task-id>` from default branch before Step B.
3. **Verify git state** after each harness turn: `git status`, `git diff --stat`, confirm correct branch.
4. **Never skip Step A context pull** — rebuilding context mid-implementation wastes tokens and misses requirements.
5. **Enforce separation** — implementer does not review their own work as the final gate.

---

## Anti-Patterns

| Anti-pattern | Why it hurts |
|---|---|
| Planning from a partial issue description | False completion claims; missed acceptance criteria |
| Reviewing only `git show HEAD` | Misses issues introduced in earlier commits on the branch |
| Implementer opens their own PR | Collapses review independence |
| Skipping worktree isolation on a shared checkout | Branch collisions between concurrent agents |
| Infinite C/D loops | Cap at 3; escalate with a summary of unresolved findings |

---

## Integration

| Skill | Relationship |
|---|---|
| `plan-code-review-workflow.md` | Single-harness alternative — use when one agent switches roles |
| `subagent-routing.md` / `delegation-patterns.md` | Worktree isolation, parallel review spawn |
| `expert-pr-review.md` | Review checklist for Step C |
| `triage-review-feedback.md` | After PR is open and reviewers respond |
| `memory-bank-protocol.md` | Durable state layer; mem0 optional on top |

**Last updated**: 2026-06-15
