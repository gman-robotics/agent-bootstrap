---
name: preservation-gate
description: "Use when writing a development-document markdown (Dt) from iteration 2 onward: every such document needs an exact '## Preservation Gate' heading listing the previous iteration's verified claims the current Developer must not regress. Distinct from REPEAT (skills/triage-review-feedback/SKILL.md Step 3) -- Preservation Gate tracks verified-good behavior to protect (positive, never closes), REPEAT tracks a recurring failure class to block (negative, closes on a mechanical check)."
version: 1.0.0
---

# preservation-gate — The `## Preservation Gate` Field on Plan Documents

**Purpose**
A plan/development document (`Dt`) that only lists what to build next silently invites a
Developer to regress what already works while chasing the new target. This skill
defines the canonical `## Preservation Gate` field: a required section, from iteration 2
onward, naming the previous iteration's verified claims as a positive list of behavior
that must not break. Source: `docs/projects/agent-bootstrap/hoh-schema-steal-plan.md`
(GB-2).

**When to Use This Skill**
- Writing or updating a `Dt` (plan/development document) for iteration 2 or later of any
  warm-started, evidence-driven workflow (see `skills/evidence-packet-protocol/SKILL.md`).
- Reviewing a `Dt` before a Developer turn starts — confirm the exact heading is present
  and lists at least one real, previously verified claim.
- Anyone tempted to fold this into REPEAT, or into `skills/reply-contract/SKILL.md`'s
  spec-gate/clarify cards — see "Placement decision" below for why this is a distinct,
  small skill instead.

**Not a substitute for**: `skills/triage-review-feedback/SKILL.md`'s REPEAT lock (a
different mechanism entirely — see the comparison table below), or
`skills/reply-contract/SKILL.md`'s spec-gate card (a human-approval mechanism on a held
artifact, not a field inside a plan document consumed by a Developer role).

---

## The Exact Heading

```markdown
## Preservation Gate

- Player input changes avatar motion (`player_control`, verified iteration 1).
- Left/right controls navigate the main menu (`menu_nav`, verified iteration 1).
```

**Rules**:
- The heading text is exactly `## Preservation Gate` — a differently worded heading
  (e.g. `## Preserved Behaviors`) does not satisfy this requirement, the same way the
  spec-gate card's stamp must be the literal word Approve/Reject, not "looks good."
- Required from iteration 2 onward (iteration 1 has nothing yet to preserve).
- At least one bullet, drawn from the *previous* iteration's `E_t.verified_records`
  (see `skills/evidence-packet-protocol/SKILL.md` GB-1) — each bullet is a **positive
  assertion of working behavior**, never a bug report or a to-do.
- Checked mechanically by `scripts/validate_preservation_gate.py` — see
  `fixtures/dt-missing-preservation-gate/`.

## Distinct from REPEAT (the exact distinction, stated once, precisely)

| | Preservation Gate | REPEAT |
|---|---|---|
| **What it tracks** | Verified-**good** behavior from the last loop | A recurring **failure class** across reviews |
| **Where it lives** | The plan/development document (`Dt`), one section per iteration | `skills/triage-review-feedback/SKILL.md` Step 3, inside a PR-feedback triage |
| **Polarity** | Positive — "this works, do not break it" | Negative — "this class of bug keeps happening, block it" |
| **Closes when** | Never — carried forward and re-verified every iteration until deliberately superseded | Closed permanently by a mechanical check (lint/test/CI) added in the fix commit |
| **Who reads it** | Developer (must not regress), QA/Tester (re-verifies) | Whoever is triaging the next review |

Never treat a Preservation Gate bullet as "closed" once the Developer's turn ends — it
is re-verified and (if still true) re-listed every iteration. Never treat a REPEAT
finding as satisfied by adding it to a Preservation Gate bullet — the two mechanisms
solve opposite problems and do not substitute for each other.

## Placement Decision (why this is its own skill, not a `reply-contract` patch)

The Preservation Gate is a field on the **plan artifact itself** (`Dt`), consumed by the
Developer role before any human approval step — it is not part of the human-stamp
mechanism (`spec-gate card` / `clarify card`) that `skills/reply-contract/SKILL.md`
owns. Folding it into `reply-contract` would conflate "what the plan document must
contain" with "how a human approves a held artifact." A one-line pointer (no mechanism
copy) lives in `skills/multi-harness-coordination/SKILL.md`, next to that skill's
existing four-field-envelope subsection — that is where this hub already documents
optional plan-document conventions for cross-harness handoffs.
`skills/reply-contract/SKILL.md` is **not touched** by this skill. Note: this hub's
`reply-contract` is at `1.4.0`, a separate lineage from an external "Eleanor"
`reply-contract` `1.3.0` overlay — named here only so neither is mistaken for the other;
reconciling them is out of scope for this skill.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| A differently worded heading (`## What We Preserved`, `## Do Not Break`) | Use the exact literal `## Preservation Gate` heading |
| Section present but empty (no bullets) | Add at least one bullet naming a previously verified `claim_id` |
| Treating a Preservation Gate bullet as a completed task, dropped next iteration | Carry it forward and re-verify every iteration until deliberately superseded |
| Closing a REPEAT finding by adding a Preservation Gate bullet instead of a mechanical check | REPEAT closes only via a lint/test/CI check in the fix commit — Preservation Gate is a different, non-substitutable mechanism |
| Folding this heading's definition into `skills/reply-contract/SKILL.md` | Keep it here — see "Placement decision" above for why |
| **REPEAT on the `dt-missing-preservation-gate` fixture closed by editing prose** | Closes only when `tests/test_evidence_packet_protocol_fixtures.py` (the `attack-12-fixture-io` class: argv/exit/stdout, run for real) goes red-then-green against the regression — never with a comment |

---

## Verification Checklist

- [ ] `Dt` from iteration 2 onward has the exact `## Preservation Gate` heading
- [ ] The section lists at least one bullet naming a previously verified claim
- [ ] Every bullet is a positive assertion of working behavior, not a bug report
- [ ] `scripts/validate_preservation_gate.py` was actually run against the document
- [ ] No REPEAT finding was "closed" by adding a Preservation Gate bullet instead of a mechanical check

---
