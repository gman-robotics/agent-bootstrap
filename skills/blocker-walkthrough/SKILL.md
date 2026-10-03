---
name: blocker-walkthrough
description: "Use this when Tom asks to be walked through the blockers or the open decisions. It explains each blocking decision one at a time with context and answer options, until all blockers are clear."
version: 1.0.0
---

# blocker-walkthrough — Explain blocking decisions one at a time

**Purpose**
Tom asks you to walk him through the blockers or the open decisions. Explain each blocking decision one at a time. Give context and answer options. Continue until all blockers are clear.

**Trigger**
Tom asks: "walk me through the blockers" (or the same request in other words).

**Do not use for**
- Deciding whether to ask Tom a question during agreed work → `project-carry-through`

## Steps
1. **Find the blockers.** Collect the decisions that stop automated work. Sources: the project manager's decision bundle, Linear tickets, plans, and open questions in chat. Keep only decisions that block work. Remove decisions that are safe to wait.
2. **Order them.** Put the decision that unblocks the most work first. Number the list. Show the count to Tom (for example, "7 blockers").
3. **Explain blocker 1 fully, then ask.** Write in this order:
   - What this decision blocks.
   - Context: what happened, what is true now, what the risk is.
   - What each option does, in plain words.
   - What happens if Tom does not answer.
   - Your recommendation and the reason.
   - The question, with the answer options at the END of the message. Use a question widget with real options.
4. **Wait for the answer.** Do not explain blocker 2 until Tom answers blocker 1.
5. **Act on the answer.** Record it (ticket, memory). Send the work to the correct specialist. Check what the answer unblocks.
6. **Go to the next blocker.** Repeat steps 3 to 5.
7. **Repeat until all blockers are clear.** At the end, report what is now unblocked and what is still waiting on a manual action.

## Rules
- One blocker at a time. One question at a time.
- Answer options go at the end of the explanation, not at the start.
- Do not hide risk. Do not push for a fast answer.
- Follow skill `asd-ste100-writing` for all text.

## Companions

| Skill | Role here |
|---|---|
| `project-carry-through` | Step 4 of that skill writes the blockers that this skill walks through |
| `asd-ste100-writing` | Writing rule for all text in the walkthrough |

**Verification**
- You explained one blocker and asked one question per message
- The answer options are at the end of the message
- You record each answer and send its unblocked work on

Last updated: 2026-10-03
