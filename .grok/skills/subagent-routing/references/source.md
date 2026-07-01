---
name: subagent-routing
description: "This skill should be used before any task with independent subtasks, parallelizable work, or when selecting a model for a spawned agent. Mandates subagent delegation for parallelizable, isolatable, or repetitive work. Defines a model selection table, a task decomposition checklist, parallel spawn pattern examples, and common mistakes to avoid."
version: 1.0.0
---

# subagent-routing.md — Subagent Use & Model Selection

**Purpose**
Mandate when to delegate work to subagents and which Claude model to use. Subagents reduce main-context bloat, enable parallelism, and match compute cost to task complexity.

**When to Use This Skill**
- Before starting any task that has independent subtasks
- When deciding whether to do work inline or spawn an agent
- When selecting a model for a spawned agent

---

## Rule 1 — Use Subagents Wherever Possible

**Mandatory**: Delegate to subagents for any work that is:
- **Parallelizable** — two or more independent lookups, reads, or searches that do not depend on each other's results
- **Isolatable** — a bounded task with a clear input/output that does not need full conversation context
- **Repetitive** — the same operation applied to multiple targets (e.g., reading N files, searching M patterns)

Do not perform these inline when a subagent can do them without blocking the main flow.

---

## Rule 2 — Model Selection

Choose the model by task complexity, not by default:

| Task Category | Model | Rationale |
|---|---|---|
| File reads, directory listings, `grep`/`find` searches | `haiku` | No logic required — fast and cheap |
| Summarization of known content | `haiku` | Pattern extraction, not reasoning |
| Formatting, renaming, simple transforms | `haiku` | Mechanical, deterministic |
| Single-file lookup ("where is X defined?") | `haiku` | Targeted retrieval |
| Research across multiple files (Explore agent) | `haiku` | Breadth search, no synthesis needed |
| Code review of an isolated diff or function | `sonnet` | Requires judgment |
| Architectural analysis, cross-file reasoning | `sonnet` | Requires synthesis |
| Implementation — writing or editing code | `sonnet` | Logic + style judgment required |
| Complex multi-step planning | `sonnet` or `opus` | Full reasoning needed |

**Default rule**: If the subagent is not writing or modifying code and does not need to reason across multiple interdependent concepts, use `haiku`.

---

## Rule 3 — Worktree Isolation Is MANDATORY for Editing Agents

Any spawned agent that **edits files** must run with `isolation: "worktree"` whenever the main checkout could be in use by anything else (another agent, a checked-out PR branch, the user). This is a hard rule, not an optimization:

- The main checkout's branch state is shared mutable state. Concurrent agents on the same checkout have caused branch collisions mid-task.
- Read-only agents (Explore, reviewers) do not need isolation.
- The only exception: the editing agent exclusively owns the checkout for the full task duration AND no other agent or PR-review checkout can run concurrently — if you can't guarantee that, use a worktree.

See `delegation-patterns.md` Pattern 2 for the spawn syntax and merge-back options.

---

## Step 1: Decompose the Task

Before starting, list all subtasks. For each, ask:
1. Does it depend on another subtask's result? → sequential
2. Is it independent? → candidate for parallel subagent
3. Does it require logic, judgment, or code generation? → `sonnet`; otherwise → `haiku`

---

## Step 2: Spawn Subagents

Use the `Agent` tool. Set `model` explicitly:

```
Agent(
  description: "Read and summarize config files",
  subagent_type: "Explore",   // or "general-purpose" for broader tasks
  model: "haiku",
  prompt: "..."
)
```

For parallelizable tasks, emit **all independent Agent calls in a single response** — they run concurrently.

For tasks that need the result before proceeding, run sequentially (wait for result, then proceed).

---

## Step 3: Aggregate Results

Synthesize subagent results in the main context. Do not re-delegate synthesis — that belongs to the main agent.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Doing file reads inline when they could be parallel | Spawn Explore agents with `model: "haiku"` |
| Using `sonnet` for a grep or directory scan | Use `haiku` — it's a retrieval task |
| Spawning a subagent for one trivial Bash command | Use the Bash tool directly — subagent overhead is not worth it for single commands |
| Delegating synthesis ("based on findings, decide X") to a subagent | Synthesis belongs in the main context where full conversation history is available |
| Running independent agents sequentially | Emit all independent Agent calls in one response to run them in parallel |
| Spawning an editing agent against the shared checkout | Use `isolation: "worktree"` — the main checkout may be on another agent's branch (Rule 3) |

---

## Example: Research + Implementation

**Task**: "Add error handling to the upload route."

**Decomposition**:
- Read the upload route file → `haiku` (file read)
- Search for existing error handler patterns in the codebase → `haiku` (grep/search)
- Implement the fix → inline, `sonnet` (code generation)

**Parallel spawn**:
```
Agent(description: "Read upload route", model: "haiku", prompt: "Read src/routes/upload.ts and return full contents")
Agent(description: "Find error handler patterns", subagent_type: "Explore", model: "haiku", prompt: "Find all error handler patterns in src/routes/")
```

Both run concurrently. Implement after both return.

---
