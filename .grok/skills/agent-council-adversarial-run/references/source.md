---
name: agent-council-adversarial-run
description: "Run a council adversarial workflow: one repo per payload, implement timeout at least 30 minutes, preserve the worktree on error, and do not call an open PR shipped."
version: 1.0.0
---

# agent-council-adversarial-run

**Purpose**
Run an adversarial implement-then-review council job and recover it when the implement seat times out.

**Trigger**
"Run adversarial", a council workflow, or recover after an implement timeout.

**Do not use for**
- A planner and implementer harness without the council runner → `adversarial-coordination-workflow`
- Closing a session with no council run → `close-out`

## Companions

| Skill | Role here |
|---|---|
| `adversarial-coordination-workflow` | Harness-level plan, implement, review loop when no council runner is installed |
| `close-out` | After the run, record what landed |

**Verification**
- One repo per payload
- Implement timeout is at least 1800 seconds
- An open PR is not reported as shipped

---

# Council run

## Preflight
- One repo per payload. Multi-repo work is sequential runs.
- `head_sha` is the agreed base, usually `origin/main`.
- Context is self-contained: plan, exit criteria, pins.
- Implement timeout is at least 1800 seconds.
- `run_id` is unique.

## Launch
Run the council runner from its install directory with the adversarial workflow, an isolated worktree, and a task file. Record the log.

Exit codes: 0 approve, 1 changes requested, 2 error, 3 gate pause.

## Worktree
| Outcome | Worktree |
|---|---|
| Completed | Cleaned |
| Gate pause | Kept for resume |
| Error or timeout | Kept for recovery |

On error, inspect the worktree, copy the work onto a feature branch, then remove the worktree only after that copy exists.

## Status
On a long seat, report stage, dirty file count, and the last log line every 5 to 10 minutes.

## Evidence
An open mergeable PR is not shipped. Cite the PR and SHA. Do not say the work is on main while the PR is open.

## Provenance
Adapted from EstateGuruRepo/agent-bootstrap `agent-council-adversarial-run`. Product names, home paths, and named-seat failover removed.

*Last updated: 2026-10-03*
