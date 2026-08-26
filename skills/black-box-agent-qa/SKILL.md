---
name: black-box-agent-qa
description: "Use before treating any agent persona, harness (config/wiring/tool registration), verb/command, or skill change as verified. Define a named input fixture and its expected output, then actually run it end-to-end against the real system under test. Reading the PR diff or the skill Markdown is not a pass. A test suite that only mocks the system under test is not sufficient proof on its own. An environment-blocked run escalates for a human decision; it never counts as a pass. Never authorizes auto-merge or a silent refine of harness/agent state from the run's outcome."
version: 1.0.0
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

## Step 1: Name the Fixture

Before running anything, write down two concrete facts:
- **Input fixture** — the exact input the system under test receives: a literal prompt/task string, a literal file diff, a literal CLI invocation, a literal event payload. Not a description of a *kind* of input — the actual content.
- **Expected output** — a specific, checkable outcome: a file exists with content X, a command exits 0 and prints Y, a specific tool call is made, a specific card or format appears in the reply. Not "works correctly" — a fact someone else could check without asking you.

If a concrete fixture and a concrete expected output cannot both be written down, the change is not ready to test yet — make the claim checkable before running anything.

---

## Step 2: Actually Run It

Execute the fixture against the real system under test — the actual agent, harness, verb, or skill as changed. Not a description of it, and not a stand-in for it.

**Reading is not running.** None of these count as a pass on their own, no matter how thorough:
- Reading the PR diff and reasoning that it looks correct
- Reading the skill's Markdown and confirming the steps are well-written
- Re-deriving the expected behavior from the spec instead of observing it happen

**Mocking is not the only proof.** A harness may mock collaborators around the system under test, but at least one run in the evidence must exercise the real system under test end-to-end for the named fixture. A suite that only exercises mocks of the very component being changed is not black-box evidence for that component.

Capture the actual output — log, transcript, screenshot, exit code, or whatever form the Step 1 expected output takes.

---

## Step 3: Compare, Don't Assume

Compare the captured output to the Step 1 expected output, explicitly. A run that produces *some* output is not a pass; the output has to match the named expectation. Note any mismatch, however small — a near-miss is a fail, not a pass with a caveat.

---

## Step 4: Handle Environment Blocks as an Escalation, Not a Pass

If the run cannot execute because the environment blocks it — missing credentials, no compute, a sandboxed tool unavailable, network egress denied, and similar — this is:
- **Not** a pass.
- **Not** a skip.
- **Not** a "verified by inspection" substitute.

Escalate explicitly: state which fixture could not run, why, and what would unblock it (the credential, the access, the missing tool). Do not mark the change as tested, and do not proceed as though it were.

---

## Step 5: Record the Result

State plainly, per fixture: input, expected output, actual output, and verdict (pass / fail / blocked). This record is the evidence — a verdict with no fixture and no captured output is not checkable by anyone else, including the next person who reviews this change.

---

## Hard Limits

This skill's pass never authorizes:
- **Auto-merge.** A pass here is evidence for a human, or an existing review gate, to act on — it is not itself permission to merge anything.
- **Silent trajectory refine of harness or agent state.** If a run's outcome suggests the agent, harness, or skill itself should change — a new default, a new lock, an adjusted persona line — that is a new proposed change, routed through its own review, never a live, unannounced adjustment made because "the run showed it works better this way." Name it explicitly as a candidate pattern to propose, not something the run itself installs.

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

- [ ] Fixture is a literal input, not a description of one
- [ ] Expected output is a specific, checkable fact
- [ ] At least one captured run exercised the real system under test, not only mocks of it
- [ ] Actual output was compared against the expected output; any mismatch is noted, not glossed over
- [ ] Environment-blocked runs are recorded as escalations, never as passes
- [ ] No auto-merge and no silent harness/agent-state refine resulted from this pass

---

Last updated: 2026-08-26
