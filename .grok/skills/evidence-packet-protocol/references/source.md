---
name: evidence-packet-protocol
description: "Use when an implementer/QA-Tester role needs to hand a planner claim-bound, checkable evidence of what actually works (and what still has a gap) instead of a prose status update. Defines the E_t.json evidence packet: typed execution_records, verified|gap statuses only, a required head_sha freeze binding, retry-once-then-escalate on schema failure, the evidence/E_t.json (current) vs evidence/E_<n>.json (priors) path convention the next planner must read, and a progressive-disclosure evidence/INDEX.md. See SCHEMA.md for the runnable validator contract."
version: 1.0.0
---

# evidence-packet-protocol — Claim-Bound Evidence Packets (`E_t.json`)

**Purpose**
An implementer's or a read-only QA/Tester role's report of "what works now" is only as
trustworthy as the checkable evidence behind each claim. This skill defines `E_t.json`
— a JSON evidence packet that binds every claim to typed `execution_records`, restricts
status to `verified | gap` only (never a vague "partial" or "looks good"), freezes the
evidence to one git commit (`head_sha`), and hands the next planner exactly what it must
preserve and what still needs work — on disk, at a fixed path, not summarized into a
chat message or a memory note. Source: `docs/projects/agent-bootstrap/hoh-schema-steal-plan.md`
(cites wiki SoT `ThomasGinter/tmg-wiki` `entities/harness-of-harness.md` @
`0651e608fded1c0676951ff16555b97e2671710d` + arXiv `2609.01481`).

**When to Use This Skill**
- After a Developer/implementer turn, when a QA/Tester role needs to produce evidence of
  what the current commit actually does (not what it was supposed to do).
- Before a Planner starts the next iteration — it must read the current `E_t.json`
  (H-1), not rely on a summarized memory note.
- Any time someone is tempted to write "looks good," "partial," or "blocked" as a QA
  verdict instead of `verified` or `gap`.

**Not a substitute for**: `skills/black-box-agent-qa/SKILL.md` (the general run-it
verification protocol this packet's `fixture`-type `execution_records` reuse) or
`skills/preservation-gate/SKILL.md` (the `## Preservation Gate` heading on the plan
document itself — a different, canonical skill; see that file for the field and its
distinction from REPEAT).

---

## Runnable Contract (not just prose)

| Piece | Where |
|---|---|
| `E_t.json` minimum schema, field rules, exit codes | `SCHEMA.md` in this directory |
| Schema validator (GB-1/GB-3/GB-4/GB-6) | `scripts/validate_evidence_packet.py` |
| H-1 planner-reads-`E_t.json` check | `scripts/check_planner_reads_et.py` |
| H-5 progressive-index check | `scripts/check_evidence_index_is_progressive.py` |
| Worked fixtures (8 of the 9 named fixtures; the 9th, `dt-missing-preservation-gate`, lives in `skills/preservation-gate/fixtures/`) | `fixtures/et-schema-valid/`, `fixtures/et-status-not-verified-or-gap/`, `fixtures/et-missing-execution-record/`, `fixtures/et-living-pii/`, `fixtures/freeze-sha-mismatch/`, `fixtures/schema-retry-then-escalate/`, `fixtures/next-planner-reads-et/`, `fixtures/evidence-index-not-full-dump/` |
| The mechanical fixture-IO check | `tests/test_evidence_packet_protocol_fixtures.py` (`attack-12-fixture-io` — see Common Mistakes) |

---

## GB-1: Claim-Bound Evidence, Typed Records, `verified \| gap` Only

Every claim in `verified_records`/`gap_records` names a `claim_id`, the `claim` text
itself, and a **non-empty** `execution_records` array — an empty array is a gap, not a
pass, even on a record claiming `status: "verified"`. Each execution record is typed
`screenshot | runtime_trace | fixture` (narrowed from the paper's `replay | runtime_trace
| screenshot` — `fixture` is this hub's own `skills/black-box-agent-qa`-style
`case.json` run). `status` (every record) and `qa_status` (packet root) are restricted
to exactly `verified | gap` — never `partial`, `blocked`, or "looks good." See
`SCHEMA.md` for the full field list and `scripts/validate_evidence_packet.py` for the
mechanical check.

## GB-3: Repair a Gap AND Deliver a New Capability

Each increment must both repair an outstanding gap and deliver one observable new
capability — not just one or the other. This is checked structurally, not by prose
promise: `planner_handoff.update_targets` must be non-empty unless `qa_status ==
"verified"` (a gap packet claiming nothing left to update is a contradiction), and
`planner_handoff.preservation_constraints` must be non-empty from iteration 2 onward
(iteration 1 has nothing yet to preserve). `validate_packet()` enforces both.

## GB-4: Frozen Candidate Identity (`head_sha`)

`head_sha` is **required**, not optional, at the packet root — optional would make this
a freeze in name only (see Risks in the plan document). Kit/Lane's evidence is bound to
exactly one candidate commit; `--expect-head-sha <sha>` on
`scripts/validate_evidence_packet.py` fails with `head_sha mismatch` if the packet's
`head_sha` does not equal the SHA the tester was told to hold. This is a "Hardproof"
rhyme only — no plugin or package by that name is installed; the mechanism reuses this
hub's existing `skill_sha256` staleness pattern (`scripts/check_skill_live.py`),
generalized to a product PR's commit identity instead of a skill file's bytes.

## GB-5: Lane Screenshots Are `execution_records` Rows

A screenshot critic's evidence is just a `type: "screenshot"` row inside `E_t.json` —
there is no separate chat or file CoS has to remember to check. This is a consequence of
GB-1's schema shape, not a new mechanism; zero new surface. Lane still never implements
(unchanged from this hub's existing Preservation conventions).

## GB-6: Schema-or-Retry Once, Then Escalate

A packet that fails schema validation gets exactly one retry — never an unbounded,
silent `T=70`-style reinvoke loop. `scripts/validate_evidence_packet.py
--retry-then-escalate <attempt-1> <attempt-2>` validates the first attempt; if invalid,
validates the second (retry); if the retry is also invalid, prints `ESCALATE` and exits
**`1`** — never `2`. Exit code `2` stays reserved for
`scripts/run_black_box_fixture.py`'s own `"blocked"` (environment) verdict; conflating a
real double-invalid escalation with an environment block would hide a genuine schema
failure behind an infrastructure-looking exit code. This reuses the *shape* of
`skills/multi-harness-coordination/SKILL.md`'s max-3-then-escalate adversarial-review
cap, but at 1 retry, not 3, since this is a schema-validity retry, not a review round.

## H-1: The Next Planner Reads the Same `E_t.json` On Disk

Path convention: `evidence/E_t.json` is the **current** iteration's packet;
`evidence/E_<n>.json` holds every prior iteration, **never overwritten in place**. The
next planner must read `evidence/E_t.json` directly before planning — a
mem0/`activeContext.md` summary is explicitly **not** a substitute (the paper's own
Planner prompt template reads the prior evidence bundle directly, not a condensed
memory note). `scripts/check_planner_reads_et.py` checks that a plan/development
template names the exact `evidence/E_t.json` path. These files live **next to the
product branch**, not inside this hub — the hub only ships the schema and the skill/
validators that define the convention.

## H-2: Read-Only Planner/Tester, Single-Writer Developer

Modeled directly on the paper's own role boundaries: the Planner role must not
implement, edit, test, or inspect production code; the QA/Tester role must not modify
production code, only read it and write `E_t.json`; the Developer is the single writer
of production code. Enforce this with a read-only worktree (or a frozen-SHA checkout
with no write remote) for the Planner and QA/Tester roles — not a suggestion, a tooling
boundary. This does **not** steal same-model-for-all-three-roles: keep Sonnet vs. Grok /
Claude Code vs. Codex distinct model pairing, per this hub's existing
`skills/subagent-routing/SKILL.md` / `skills/delegation-patterns/SKILL.md` convention.

## H-3: Warm-Start, Never a Silent Reset

Quoting the paper's own Developer contract directly: "Continue from the artifact already
present... Preserve verified functionality and repair the next observable gap rather
than replacing a working project with a smaller reset." This is the mechanism the
paper's own `w/o Warm-Start` ablation measures (a real, cited regression) — a Developer
that rewrites from empty instead of continuing from the existing artifact is not
following this skill, even if the resulting code technically satisfies the plan.

## H-4: One Commit Per Role Turn

Planner commits the plan document (`Dt`, including its `## Preservation Gate` section);
Developer commits the code; QA/Tester commits `evidence/E_t.json`. This matches this
hub's existing `skills/multi-harness-coordination/SKILL.md` "Orchestrator Checklist"
pattern, extended per-role rather than per-harness-turn.

## H-5: Progressive-Disclosure Evidence Index, Never a Full Dump

`evidence/INDEX.md` (sibling to `evidence/E_t.json` in the product repo) summarizes each
iteration with a one-line status and a pointer to its file — modeled directly on this
hub's own `skills/INDEX.md` progressive-disclosure convention. It never pastes a
packet's own fields (`execution_records`, `claim_id`, `planner_handoff`,
`verified_records`, `gap_records`) inline; `scripts/check_evidence_index_is_progressive.py`
checks both halves of this rule (no raw-field dump, at least one real pointer present).

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Writing `"partial"`, `"blocked"`, or "looks good" anywhere `qa_status`/`status` is checked | Use `verified` or `gap` only, at both the packet root and every record |
| Leaving `head_sha` out because "it's obvious which commit" | It is required, not optional — omitting it makes the freeze theater, not a real binding |
| An empty `execution_records` array on a `"verified"` claim | Empty is a gap, not a pass (GB-1) — add the record or mark the claim a gap |
| Treating GB-6 escalation as exit code `2` | Escalate is exit `1` + `ESCALATE`; `2` is reserved for the runner's own environment-blocked verdict, never a schema failure |
| A `<placeholder>` in a fixture's argv (e.g. `<candidate-sha>`) | Fixture commands must be copy-paste literal — use real, fixed 40-char hex SHAs (see `fixtures/freeze-sha-mismatch/`) |
| Testing only the "packet bad, record good" crossed-pair direction | Test both directions in the same fixture run (see `fixtures/et-status-not-verified-or-gap/`'s two sample packets) |
| Assuming the Grok Bot CoS overlay's Lane/Kit wiring and this hub's schema can drift silently | Name the drift risk explicitly; treat a second sighting of an overlay-vs-hub schema mismatch as REPEAT, not a fresh surprise each time |
| **REPEAT on any of the nine named fixtures closed by editing prose or a comment** | Closes only when `tests/test_evidence_packet_protocol_fixtures.py` (the `attack-12-fixture-io` class: argv/exit/stdout, run for real) goes red-then-green against the regression — never with a comment or a case.json edit alone |

---

## Leftovers (not in this PR)

Named explicitly, matching `docs/projects/agent-bootstrap/hoh-schema-steal-plan.md` §14:
no HoH runtime/scheduler/orchestrator is built here — every artifact in this skill is a
markdown/JSON/validator-script triple, never a daemon or CI trigger. `Flesymeb/
HarnessOfHarness` and a "Hardproof" plugin are not installed or cloned anywhere. The
native-compiled-black-box gap is unresolved: `scripts/run_black_box_fixture.py`'s
subprocess argv/exit-code/stdout contract covers a validator script well, but a
compiled game/GUI artifact is not a clean subprocess in the same way — this skill's
fixtures all target validator scripts, not compiled artifacts. An external "Eleanor"
`reply-contract` `1.3.0` overlay is a separate, named lineage from this hub's own
`reply-contract` `1.4.0` — not reconciled here. Any Grok Bot CoS overlay wiring that
names Lane/Kit by role identity or a specific harness invocation stays local to that
overlay, never in this hub (see `skills/preservation-gate/SKILL.md` "Placement
decision" for the same hub-vs-overlay split applied to GB-2).

---

## Verification Checklist

- [ ] `E_t.json` has a non-empty, real (not placeholder) `head_sha` at the root
- [ ] `qa_status` and every record's `status` are `verified` or `gap`, nothing else
- [ ] Every record's `execution_records` is non-empty and uses only `screenshot \| runtime_trace \| fixture`
- [ ] `planner_handoff.update_targets` is non-empty unless `qa_status == "verified"`; `preservation_constraints` is non-empty from iteration 2 onward
- [ ] No living person's real name or non-`+1555XXXXXXX` phone number appears anywhere in the packet
- [ ] `scripts/validate_evidence_packet.py` was actually run against the packet, not eyeballed
- [ ] The next planner's template names the exact `evidence/E_t.json` path (H-1) and `evidence/INDEX.md` stays a pointer index, not a dump (H-5)

---
