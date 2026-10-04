---
name: shared-memory-coordination
description: "Share and pull the active to-do list and completed-task log across harnesses on a Mem0 bus (coord-YYYYMMDD run ids)."
version: 1.0.0
---

# shared-memory-coordination.md — Cross-Agent Shared Memory Task Coordination

**Purpose**  
Define the standard syntax and protocol for sharing, pulling, and updating the active to-do list and log of completed tasks across different agent harnesses (Claude, Codex, Hermes) using the Mem0 shared memory platform. This ensures real-time task visibility and seamless daily close-out reconciliation.

**When to Use This Skill**  
- **Session Start / Pull:** Retrieve and reconcile the active to-do list from the coordination bus (`run_id: coord-YYYYMMDD`).
- **Task State Changes / Sync:** Immediately after a task's status changes (e.g., from `pending` to `in_progress`).
- **Task Completion / Log:** When any agent completes a task, log it immediately to Mem0 so others can see.
- **End of Day (EOD) / Close-out:** Pull and reconcile all logged completions into the master standup log (`tracking/standup.md`).

---

## Mem0 Schema Standards

All shared coordination memories must be saved under the shared user scope with:
- **`user_id`:** the hub's shared coordination user (set in the project memory-bank; do not hard-code a person)
- **`run_id`:** `coord-YYYYMMDD` (where `YYYYMMDD` is the current date in Mountain Time, e.g. `coord-20260625`)

### Per-ticket threads
Work scoped to a single issue additionally uses **`run_id: ticket-<issue-id-first-8>`** so any agent can pull that ticket's history without scanning day buses.
- Milestones and handoffs go to both the day bus and the ticket thread.
- Ticket threads are permanent. Never reuse a run id for a different issue.

---

## Step 1: Sharing the Active To-Do List (Sync)

When the active to-do list is updated in the wiki, the active agent MUST publish the updated state to Mem0 as a single, easily parseable memory.

### Mem0 Configuration:
*   **`metadata.type`:** `task_state`
*   **`agent_id`:** Name of the active agent harness (e.g., `claude`, `codex`, `hermes`)

### Memory Text Format:
```markdown
[MEM0_TODO_LOG]
JSON:
{
  "synced_at": "YYYY-MM-DD HH:MM MT",
  "agent_id": "claude",
  "todos": [
    {
      "id": "task-1",
      "project": "<project>",
      "content": "PR #N: awaiting re-review",
      "status": "in_progress"
    },
    {
      "id": "task-2",
      "project": "<project>",
      "content": "Review the open plan.",
      "status": "pending"
    }
  ]
}
[/MEM0_TODO_LOG]
```

---

## Step 2: Logging Completed Tasks (Handoff)

When any agent completes a task, they MUST immediately post a `MEM0_COMPLETED_LOG` entry to the coordination bus. Do not wait for the EOD run.

### Mem0 Configuration:
*   **`metadata.type`:** `handoff`
*   **`agent_id`:** Name of the active agent harness (e.g., `codex`)

### Memory Text Format:
```markdown
[MEM0_COMPLETED_LOG YYYY-MM-DD]
- **[Project Tag]:** Completed work description (must cite SHA, PR link, or log line).
[/MEM0_COMPLETED_LOG]
```

*Example:*
```markdown
[MEM0_COMPLETED_LOG 2026-06-25]
- **[<project>]:** PR #N reviewed, verified, and merged.
[/MEM0_COMPLETED_LOG]
```

---

## Step 3: Pulling and Reconciling (Pull)

At the beginning of any session, the agent MUST:
1.  Query Mem0 for `[MEM0_TODO_LOG]` and `[MEM0_COMPLETED_LOG` under the current and previous day's `run_id`.
2.  Parse the to-do list JSON block and cross-reference it with any logged completed tasks.
3.  Update their local CLI `todo` list to reflect the absolute latest state of the universe before taking any action.

---

## Step 4: End of Day Reconciliation (EOD Close-out)

During the **EOD close-out** (following `end-of-day-review.md`):
1.  Query Mem0 for all `[MEM0_COMPLETED_LOG YYYY-MM-DD]` entries.
2.  Aggregate all completed entries under the `## Completed History` section for the target date in the hub standup log named by the project memory-bank (do not hard-code a home path).
3.  Remove those completed items from the active to-do list section.
4.  Publish the clean, updated `[MEM0_TODO_LOG]` to the next day's run ID (`coord-YYYYMM(DD+1)`).

---

## Anti-Patterns

| Anti-pattern | Why it hurts |
| :--- | :--- |
| **Omitting the JSON block** | Other agents cannot systematically parse the to-do list, leading to missed updates. |
| **Waiting until EOD to log completions** | Causes parallel agents to duplicate work or operate on stale assumptions. |
| **Failing to cite evidence in completed logs** | Violates the **Evidence Rule** (no status without a verifiable SHA/PR/log). |

*Last updated: 2026-06-25*
