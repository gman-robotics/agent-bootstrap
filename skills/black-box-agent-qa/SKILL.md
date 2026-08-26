---
name: black-box-agent-qa
description: "Use before treating any agent persona, harness (config/wiring/tool registration), verb/command, or skill change as verified. Define a named input fixture and its expected output, then actually run it end-to-end against the real system under test using scripts/run_black_box_fixture.py (see SCHEMA.md for the case.json contract; the contract is a generic subprocess argv/exit-code/stdout check, not unittest-specific). Reading the PR diff or the skill Markdown is not a pass. A test suite that only mocks the system under test is not sufficient proof on its own. An environment-blocked run escalates for a human decision; it never counts as a pass. Never authorizes auto-merge or a silent refine of harness/agent state from the run's outcome."
version: 1.2.0
---

# black-box-agent-qa — Black-Box Verification for Agent, Harness, Verb, and Skill Changes

**Purpose**
A change to an agent persona, a harness (configuration, tool wiring, registration), a verb/command definition, or a skill file is a black box the moment it ships — prose and wiring, not application code with a compiler to catch mistakes. The only thing that counts as evidence it works is an actual run against a named input, compared against a named expected output. This skill is the minimum bar for calling any such change "verified."

**When to Use This Skill**
- Before marking any change to `agents/*.md`, harness configuration/tool wiring, a verb/command definition, or `skills/*/SKILL.md` as tested, passing, or ready to ship.
- `skills/close-out/SKILL.md` Step 9 requires a pass from this skill before a new or edited skill is treated as live, not merely written.
- Any time a reviewer or a self-review is tempted to treat "I read the diff" or "I read the skill Markdown and it's well-written" as the test.

**Not a substitute for**: `skills/write-tests/SKILL.md` (Red/Green/Refactor TDD on ordinary application code). This skill exists specifically because agent/harness/verb/skill artifacts have no compiler or type-checker of their own — an actual run is the only check available.

---

## Runnable Contract (not just prose)

This skill ships with a real, executable I/O contract, not only these steps in Markdown:

| Piece | Where |
|---|---|
| Minimum schema for a fixture's `case.json` | `SCHEMA.md` in this directory |
| Worked example fixtures | `fixtures/repeat-lock-mechanical-check/`, `fixtures/close-out-live-gate-check/`, `fixtures/check-skill-live-cli/` (non-`unittest` example) |
| The runner ("a way to invoke it") | `scripts/run_black_box_fixture.py` |
| The live-flip gate this feeds (`close-out` Step 9) | `scripts/check_skill_live.py` |

A fixture directory is never just a description — it is `case.json` (a literal `input.command` argv + a literal `expected` outcome) that `scripts/run_black_box_fixture.py` actually executes and scores. See `SCHEMA.md` for the full contract.

---

## Step 1: Name the Fixture

Before running anything, write a `case.json` (schema in `SCHEMA.md`) with two concrete facts:
- **Input fixture** — `input.command`: the exact argv the system under test receives. Not a description of a *kind* of input — the actual argv.
- **Expected output** — `expected`: a specific, checkable outcome (an exit code, and optionally literal substrings the real stdout/stderr must contain). Not "works correctly" — a fact someone else could check without asking you.

If a concrete `case.json` cannot be written, the change is not ready to test yet — make the claim checkable before running anything.

---

## Step 2: Actually Run It

Run the fixture with `scripts/run_black_box_fixture.py --fixture <dir> --skill <name> --out skills/<name>/black-box-run.json`. This executes the fixture's `input.command` against the real system under test — the actual agent, harness, verb, or skill as changed. Not a description of it, and not a stand-in for it.

**Reading is not running.** None of these count as a pass on their own, no matter how thorough:
- Reading the PR diff and reasoning that it looks correct
- Reading the skill's Markdown and confirming the steps are well-written
- Re-deriving the expected behavior from the spec instead of observing it happen

**Mocking is not the only proof.** A harness may mock collaborators around the system under test, but at least one run in the evidence must exercise the real system under test end-to-end for the named fixture. A suite that only exercises mocks of the very component being changed is not black-box evidence for that component.

The runner captures the actual output (`stdout_tail`/`stderr_tail`/`exit_code`) into the run record it writes — no hand transcription needed.

---

## Step 3: Compare, Don't Assume

`run_black_box_fixture.py` does this mechanically: it compares the real `exit_code`/`stdout`/`stderr` against `expected` and reports every mismatch by name in the run record's `mismatches` list. A run that produces *some* output is not a pass; the output has to match the named expectation — the runner enforces this, it is never eyeballed.

---

## Step 4: Handle Environment Blocks as an Escalation, Not a Pass

If the run cannot execute because the environment blocks it — missing credentials, no compute, a sandboxed tool unavailable, network egress denied, and similar — `run_black_box_fixture.py` records `"verdict": "blocked"` and exits `2`. This is:
- **Not** a pass.
- **Not** a skip.
- **Not** a "verified by inspection" substitute.

Escalate explicitly: state which fixture could not run, why, and what would unblock it (the credential, the access, the missing tool). Do not mark the change as tested, and do not proceed as though it were. `scripts/check_skill_live.py` never treats a `blocked` (or `fail`) run record as live-eligible.

---

## Step 5: Record the Result

`run_black_box_fixture.py` writes the record for you: per fixture, it captures the input, expected output, actual output, and verdict (pass / fail / blocked) into `skills/<name>/black-box-run.json`, tagged with a `skill_sha256` of the skill's current `SKILL.md`. This record is the evidence — a verdict with no fixture and no captured output is not checkable by anyone else, including the next person who reviews this change. `scripts/check_skill_live.py` reads this exact file to decide whether the skill may be treated as live (see `skills/close-out/SKILL.md` Step 9).

---

## Hard Limits

This skill's pass never authorizes:
- **Auto-merge.** A pass here is evidence for a human, or an existing review gate, to act on — it is not itself permission to merge anything.
- **Silent trajectory refine of harness or agent state.** If a run's outcome suggests the agent, harness, or skill itself should change — a new default, a new lock, an adjusted persona line — that is a new proposed change, routed through its own review, never a live, unannounced adjustment made because "the run showed it works better this way." Name it explicitly as a candidate pattern to propose, not something the run itself installs. This is also enforced mechanically, not just by convention: a run record's `skill_sha256` is tied to one exact `SKILL.md` byte-for-byte. Edit the skill afterward — silently or not — and `scripts/check_skill_live.py` reports the record stale and refuses to call the skill live until a fresh pass is captured against the new content.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Calling a PR read-through a pass | Run the actual fixture; a diff read is not evidence |
| Testing only with mocks of the system under test | Include at least one real end-to-end run in the evidence |
| Treating a sandbox/credential block as a pass | Escalate; state exactly what is blocked and what would unblock it |
| Vague expected output ("should work", "looks right") | Rewrite as a checkable fact before running anything |
| Letting a good run auto-adjust harness or agent state | Propose the change separately; route it through its own review |
| Treating this pass as merge authorization | This skill produces evidence, not a merge decision |
| Skipping this before marking a skill ship-ready | `close-out` Step 9 requires a pass here first |

---

## Verification Checklist

- [ ] `case.json` exists under `fixtures/<case-name>/` matching `SCHEMA.md` (literal `input.command`, literal `expected`)
- [ ] `scripts/run_black_box_fixture.py` was actually invoked — not simulated, not described
- [ ] `skills/<name>/black-box-run.json` exists with `"verdict": "pass"` and a `skill_sha256` matching the current `SKILL.md`
- [ ] `python3 scripts/check_skill_live.py <name>` exits `0`
- [ ] Environment-blocked runs are recorded as `"verdict": "blocked"`, never as `"pass"`
- [ ] No auto-merge and no silent harness/agent-state refine resulted from this pass (verified: editing `SKILL.md` after capture invalidates the record via the sha mismatch)

---

Last updated: 2026-08-26
