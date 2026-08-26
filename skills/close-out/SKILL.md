---
name: close-out
description: "Two-phase task close-out. Phase 1: verify memory bank + shared memory (mem0, if configured) are accurate so a fresh agent can pick up without reconstruction (completed log, updated todo list, evidence-backed progress entry). Phase 2: scan the session for patterns, friction, and skill gaps and produce specific improvement proposals (new skill / skill update / AGENTS.md rule / feedback memory / docs entry). A new or edited skill only goes live once scripts/check_skill_live.py <name> exits 0 against a black-box-agent-qa run record captured by scripts/run_black_box_fixture.py — user approval to write it is not a ship, and editing the file after capture invalidates the record."
version: 1.2.0
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
- If a `reply-contract` spec-gate or clarify card set a stable task Name earlier in the thread, reuse that exact Name in the completed-log entry below so cross-references line up

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

Present findings to the user as a numbered list: **Finding** → **Proposed fix** → **Effort** (one-liner / 5 min / 30 min). For a **New skill** or **Existing skill update** finding, the **Proposed fix** must also name one concrete I/O case as a real `fixtures/<case-name>/case.json` (schema: `skills/black-box-agent-qa/SCHEMA.md`) — a literal `input.command` and a literal `expected` outcome — that Step 9 will actually run with `scripts/run_black_box_fixture.py` before that skill goes live. A skill proposal with no named `case.json` path is not ready to present.

### Step 9: Apply Approved Improvements — Approval to Write Is Not a Ship

A user's **Approve** on a Step 8 finding authorizes writing or editing the skill file. It does **not** authorize treating that skill as live. **The live-flip is defined mechanically, not by judgment call**:

1. Write or edit `skills/<name>/SKILL.md` (see the per-finding steps below).
2. Capture a real run against the Step 8 I/O case:
   ```bash
   python3 scripts/run_black_box_fixture.py \
     --fixture <fixture-dir-from-step-8> \
     --skill <name> \
     --out skills/<name>/black-box-run.json
   ```
   This is `skills/black-box-agent-qa/SKILL.md` end to end — it actually runs the fixture's command and writes `skills/<name>/black-box-run.json` with a real `verdict` and a `skill_sha256` of the file just written.
3. Run the gate: `python3 scripts/check_skill_live.py <name>`. **The skill is live only when this exits `0`.** It exits non-zero (never live) when: no run record exists yet, the record's verdict is not `pass`, or the record is JSON-invalid.
4. Only after step 3 exits `0` may the skill be added to `skills/INDEX.md`, `AGENTS.md` §4, the session-start trigger tables, and the exporter config (`skills/INDEX.md §Adding a New Skill` gates on this same check — see there for the full listing sequence).

Reading the finished skill Markdown back to the user, or getting a second "looks good," is not step 2 or step 3 — nothing substitutes for actually running `run_black_box_fixture.py` and seeing `check_skill_live.py` exit `0`.

**The stale-record guard is the same mechanism, not a separate rule.** `check_skill_live.py` ties the run record to one exact `SKILL.md` by content hash (`skill_sha256`). Edit the skill again after capturing a pass — for any reason, including a well-intentioned trajectory refine — and the hash no longer matches; the gate reports the record stale and fails until a fresh run is captured against the new content. There is no code path where an edited skill stays live on an old pass.

For each finding the user approves, before running the gate above:
- **New skill**: Follow the process in `skills/INDEX.md §Adding a New Skill` — write the skill file, then run the black-box-agent-qa gate above, and only then update INDEX.md, AGENTS.md (and the session-start trigger tables), and the exporter config.
- **Skill update**: Edit the skill file in-place. Bump the version and the "Last updated" footer. Then run the black-box-agent-qa gate above before treating the update as live — an edited skill with a stale or missing run record is no more trustworthy than a brand-new one.
- **AGENTS.md rule**: Add to the appropriate section. Keep it under 2 lines.
- **Shared-memory feedback**: Add immediately, if configured.
- **docs/ entry**: Follow `docs-protocol`.

**Watch for the failure class this step can institutionalize**: a skill edited because *this one session's run* happened to go a certain way can quietly turn a one-off shortcut into a standing rule for every future run. Treat a run-driven skill edit as a candidate **pattern** to cite and route through Step 8 like any other finding — never as a live rule installed straight from the run's outcome just because it was convenient this time. If the edit really is only this session's convenience, say so and leave the skill alone. The `skill_sha256` staleness check above is what makes this mechanical: a run-driven edit applied without a fresh gate pass simply does not ship as live.

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
| Treating the user's Approve on a Step 8 finding as the skill going live | Only `scripts/check_skill_live.py <name>` exiting `0` authorizes calling it live |
| Presenting a skill proposal in Step 8 with no named `case.json` path | Add the literal `input.command` + `expected` before presenting; an un-checkable proposal is not ready |
| Editing a skill straight from one run's outcome without flagging it | Cite it as a pattern proposal through Step 8, not a silent live install of this session's shortcut |
| Listing a skill in INDEX.md/trigger tables before running the gate | `skills/INDEX.md §Adding a New Skill` requires `check_skill_live.py` to exit `0` first |
| Assuming an old run record still counts after editing the skill again | It doesn't — `skill_sha256` ties the record to one exact file; re-run after every edit |

---

## Relationship to Other Skills

- **end-of-day-review** — run at EOD; day-scoped, covers all projects. Close-out is task-scoped and adds the retrospective layer.
- **multi-harness-coordination** — defines cross-harness role assignment and coordination conventions this skill assumes.
- **memory-bank-protocol** — defines the memory bank update protocol used in Steps 2–3.
- **docs-protocol** — governs any `docs/` additions proposed in Phase 2.
- **reply-contract** — if this thread used a spec-gate/clarify card, its stable task Name is the identifier to reuse in the completed-log entry (Step 1).
- **black-box-agent-qa** — required gate before Step 9 treats a new or edited skill as live; run `scripts/run_black_box_fixture.py` against the Step 8 `case.json`, then confirm `scripts/check_skill_live.py <name>` exits `0`, and escalate (verdict `blocked`) rather than pass if the environment blocks the run.

*Last updated: 2026-08-26*
