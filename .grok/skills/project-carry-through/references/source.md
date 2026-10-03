---
name: project-carry-through
description: "Use this when a project or plan was agreed with Tom, and you must decide whether to ask him a question or keep working. Standing rule: carry agreed projects to completion without Tom unless a new decision or a manual action is necessary."
version: 1.0.0
---

# project-carry-through — Carry agreed projects to completion

**Purpose**
Tom and the team plan a project together. After that, the team carries the project to completion. Tom does not need to push it. Tom speaks only when a NEW decision or a MANUAL action is necessary.

**Trigger**
Use this when a project or plan was agreed with Tom, and you must decide whether to ask him a question or keep working.

**Do not use for**
- Explaining the open blockers to Tom one at a time → `blocker-walkthrough`

## Steps
1. Keep the plan moving. Do the next step. Hand work to the correct specialist.
2. Before you ask Tom, check each item:
   - Did Tom already decide this? Look in the plan, tickets, memory and chat.
   - Can you choose a safe, reversible option? If yes, choose it. Write the choice in the ticket.
   - Is it a new decision? Is it a manual action only Tom can do (sign in, an access key, a payment, or approval of a decision that is on hold)? If yes, ask.
3. Do not ask Tom:
   - for status,
   - for confirmation of agreed work,
   - or for a go on a step that the plan already approved.
4. When a step is blocked by Tom, write the blocker in the blocker list (see skill `blocker-walkthrough`). Continue all work that the blocker does not stop.
5. Never skip a safety rule. Merges need a saved review. Outside messages need Tom's send. Live changes need the plan's gate.
6. Report to Tom only: a new decision, a manual action, a blocker, a merge-ready result, or a verified-live result.

## Companions

| Skill | Role here |
|---|---|
| `blocker-walkthrough` | Step 4 writes blockers for this skill; it explains them to Tom one at a time |
| `asd-ste100-writing` | Writing rule for every report and ticket entry |

## Writing
Follow skill `asd-ste100-writing`.

**Verification**
- No question to Tom is about status, agreed work, or a step the plan already approved
- Each choice you made alone is safe, reversible, and written in the ticket
- Each blocker is in the blocker list, and unblocked work continues
