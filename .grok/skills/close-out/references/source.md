---
name: close-out
description: "Two-phase task close-out. Phase 1: verify memory bank + shared memory (mem0, if configured) are accurate so a fresh agent can pick up without reconstruction (completed log, updated todo list, evidence-backed progress entry). Phase 2: scan the session for patterns, friction, and skill gaps and produce specific improvement proposals (new skill / skill update / AGENTS.md rule / feedback memory / docs entry)."
version: 1.0.0
---

# close-out — Task Close-Out & Continuous Improvement

**Purpose**  
A two-phase protocol run at the end of any significant task or conversation thread — not just EOD. Phase 1 ensures the memory state (shared memory + memory bank) is accurate enough that a fresh agent can pick up exactly where this thread left off, with no reconstruction needed. Phase 2 scans the session for patterns, friction, and skill gaps and turns them into concrete improvement proposals.

**When to Use**
- Completing any significant task, feature thread, or investigation before switching context
- When the user says "close this out", "wrap this up", "make sure we're captured"
- After a multi-step implementation session (PR created, infra applied, etc.)
- Differs from `end-of-day-review` (which is day-scoped across all projects); this is task-scoped and also evaluates the quality of the session itself

---

## Phase 1: Handoff — Ensure Continuity

Goal: a fresh agent on a cold session can read shared memory + the memory bank and know exactly what was done, what is pending, and what the next action is — without reading this chat.

### Step 1: Establish the task scope

Identify what was worked on this session:
- Which project (check manifest.yaml if unclear)
- Which PRs, issues, branches, or infra resources were touched
- What the user's original goal was vs. what was actually delivered

### Step 2: Audit the memory bank hot files

Read `memory-bank/activeContext.md` and `memory-bank/progress.md` for the active project.

For **activeContext.md** verify:
- [ ] The task just completed is reflected accurately (state, evidence: SHA/PR/resource ID)
- [ ] Any new open issues, PRs, or todos spawned by this task are listed
- [ ] Load-bearing decisions made this session are in the "Load-Bearing Decisions" section
- [ ] Open questions are current (remove resolved ones, add new ones)
- [ ] The "Current State (as of DATE)" date is today

For **progress.md** verify:
- [ ] A dated entry exists for today's work with a deliverables table and key learnings
- [ ] Evidence rule applied: every "done/merged/deployed" claim has a SHA, PR link, or log reference
- [ ] Nothing was marked "done" that is actually still pending

If any of the above are missing or stale, update them now before proceeding. Follow each project's own memory-bank commit policy (some projects commit `agent-bootstrap`'s memory bank but keep per-project memory banks uncommitted — check the project's own conventions before committing).

### Step 3: Sync shared memory (if configured)

If mem0 or an equivalent shared-memory layer is configured, pull today's bus first to avoid overwriting another agent's updates:

```
search_memories(query="MEM0_TODO_LOG active todos", run_id="coord-YYYYMMDD")
search_memories(query="MEM0_COMPLETED_LOG", run_id="coord-YYYYMMDD")
```

Then write two entries:

**Completed log** (one per significant deliverable, must cite evidence):
```
[MEM0_COMPLETED_LOG YYYY-MM-DD]
- [Project Tag]: What was delivered (PR #N merged / SHA abc123 / resource ID).
[/MEM0_COMPLETED_LOG]
```
Post with `metadata.type = "handoff"`, `run_id = "coord-YYYYMMDD"`.

**Updated todo log** (full current list for this project — not just today's delta):
```json
[MEM0_TODO_LOG]
{
  "synced_at": "YYYY-MM-DD HH:MM",
  "agent_id": "<harness-name>",
  "todos": [
    {
      "id": "task-<slug>",
      "project": "<Project Tag>",
      "content": "<what needs to happen next, with any blocking dependency named>",
      "status": "pending|in_progress|blocked"
    }
  ]
}
[/MEM0_TODO_LOG]
```
Post with `metadata.type = "task_state"`, `run_id = "coord-YYYYMMDD"`.

If no shared-memory layer is configured, skip this step — the memory bank alone is the handoff record.

### Step 4: Spot-check handoff completeness

Ask: if a fresh agent read only the memory bank and today's shared-memory bus, could it:
1. Know what was done this session without guessing? (evidence exists)
2. Know what the next concrete action is? (todo has a named next step)
3. Know what is blocked and on whom? (blocking dependency named)
4. Know what NOT to re-do? (load-bearing decisions captured)

If any answer is "no" — add the missing piece before moving on.

---

## Phase 2: Retrospective — Continuous Improvement

Goal: convert session observations into concrete skill or process improvements. Not a vague "things went well" summary — specific, actionable, filed.

### Step 5: Pattern scan

Review the session for any workflow that ran **without a skill backing it**:
- A multi-step process executed from scratch (no skill loaded, no checklist referenced)
- A lookup or command that had to be figured out each time (credentials, build tool init, CLI flags)
- A decision process that involved ≥2 back-and-forths to land on the right approach

For each: note what the workflow was and roughly how many steps it had.

### Step 6: Friction log

Identify specific friction points — moments where the session slowed down unnecessarily:

| Friction type | Examples |
|---|---|
| **Config lookup** | Had to discover the correct cloud profile, credential export pattern, or project ID |
| **Tool discovery** | Had to figure out a CLI flag or API call that should be documented |
| **Re-derivation** | Re-read a file or re-ran a command to recover info that should have been in memory |
| **Clarification round-trip** | Asked a question that could have been anticipated from context |
| **Skill gap** | Executed a process that should have been a skill but wasn't |

For each friction point, note: (a) what it was, (b) which skill or file should capture it, (c) the specific addition.

### Step 7: Communication evaluation

Assess the interaction quality — not the work quality, but the communication efficiency:
- Were there unnecessary asks for confirmation on things that were clearly implied?
- Were there places where progress updates were too sparse (user was left wondering what was happening)?
- Were there places where the response was too long for what was needed?
- Was the user redirected or corrected at any point? If so, why — and what should be stored as a feedback memory?

### Step 8: Classify findings and propose improvements

For each finding from Steps 5–7, classify and propose the fix:

| Class | When to use | Action |
|---|---|---|
| **New skill** | ≥3 steps, reusable across sessions, not currently in INDEX.md | Draft skill name, trigger sentence, and 3–5 key steps. Propose to user before writing. |
| **Existing skill update** | The pattern is covered but the skill is incomplete or has a wrong step | Identify the file + specific line/section to change. Propose the edit. |
| **AGENTS.md rule** | A constraint or decision that every agent should know by default | Identify which section of AGENTS.md and propose the addition. |
| **Shared-memory feedback** | A user preference or correction that should shape future behavior | Write it immediately with the shared-memory tool (e.g. `add_memory`), if configured. |
| **docs/ entry** | A technical fact (credential pattern, API behavior, config trap) that belongs in the project's `docs/` layer | Identify the target doc file and propose the addition. |

Present findings to the user as a numbered list: **Finding** → **Proposed fix** → **Effort** (one-liner / 5 min / 30 min).

### Step 9: Apply approved improvements

For each finding the user approves:
- **New skill**: Follow the process in `skills/INDEX.md §Adding a New Skill` — write the skill file, update INDEX.md, AGENTS.md, and the exporter config.
- **Skill update**: Edit the skill file in-place. Bump the "Last updated" footer.
- **AGENTS.md rule**: Add to the appropriate section. Keep it under 2 lines.
- **Shared-memory feedback**: Add immediately, if configured.
- **docs/ entry**: Follow `docs-protocol`.

---

## Anti-Patterns

| Anti-pattern | Why it hurts |
|---|---|
| Skipping Phase 1 and going straight to Phase 2 | A brilliant retrospective is worthless if the next agent starts blind |
| Writing "done" without evidence | Violates the evidence rule; creates false records |
| Capturing learnings only in chat | The session is gone; files and shared memory persist |
| Phase 2 producing only vague "could be better" observations | Improvements must be specific enough to act on: file, section, proposed text |
| Proposing a new skill for a one-off workflow | Skills are for reusable patterns; one-offs belong in docs/ or a memory note |
| Running Phase 2 without looking at the actual conversation | Generates hypothetical improvements; the real ones come from what actually happened |

---

## Relationship to Other Skills

- **end-of-day-review** — run at EOD; day-scoped, covers all projects. Close-out is task-scoped and adds the retrospective layer.
- **multi-harness-coordination** — defines cross-harness role assignment and coordination conventions this skill assumes.
- **memory-bank-protocol** — defines the memory bank update protocol used in Steps 2–3.
- **docs-protocol** — governs any `docs/` additions proposed in Phase 2.

*Last updated: 2026-07-01*
