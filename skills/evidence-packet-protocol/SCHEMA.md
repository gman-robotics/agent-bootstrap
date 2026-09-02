# evidence-packet-protocol — `E_t.json` schema (minimum schema, not a framework)

This is the runnable contract behind `SKILL.md`'s GB-1/GB-3/GB-4/GB-6 rules, in the same
"minimum schema, not a framework" style as `skills/black-box-agent-qa/SCHEMA.md`. Source:
`docs/projects/agent-bootstrap/hoh-schema-steal-plan.md` (Et schema section) + the paper's
own Listing 1 structure, narrowed per the plan's steal lock — see that document for the
full citation trail (wiki SoT + arXiv `2609.01481`).

## Directory shape

```
skills/evidence-packet-protocol/fixtures/<case-name>/
  case.json           # required -- the black-box-agent-qa I/O contract (see below)
  README.md           # human-readable provenance, names the attack-12-fixture-io class
  E_t.sample.json      # (or a case-specific name) -- the sample packet(s) the fixture validates
```

## `E_t.json` root object

One `E_t.json` per iteration. Path convention (H-1/H-5): `evidence/E_t.json` is the
**current** iteration's packet, prior iterations are kept as `evidence/E_<n>.json` —
**never overwritten in place** — and summarized progressively in `evidence/INDEX.md`
(never a full dump of the packets' own fields). These files live **next to the product
branch** (Hermes/Eleanor or a Grok Bot product PR), not inside this hub — the hub only
ships this schema and the skill/validators that define it.

```jsonc
{
  "iteration": 2,                       // required, integer >= 1
  "head_sha": "a1b2c3d...",             // REQUIRED (not optional) -- GB-4 freeze binding
  "qa_status": "gap",                   // required, enum: "verified" | "gap" -- NEVER "partial", "blocked", or "looks good"
  "verified_records": [                 // required, array (may be empty)
    {
      "claim_id": "player_control",     // required, stable slug
      "claim": "Player input changes avatar motion.",   // required, string
      "execution_records": [            // required, NON-EMPTY array -- empty is a gap, not a pass (GB-1)
        {
          "type": "screenshot",         // required, enum: "screenshot" | "runtime_trace" | "fixture"
          "path": "screenshots/frame_018.png",           // required, repo-relative path
          "observation": "..."          // required, one-sentence string
        }
      ],
      "status": "verified"              // required, enum: "verified" | "gap" -- never "looks good"
    }
  ],
  "gap_records": [                      // required, array (may be empty)
    {
      "claim_id": "result_state",
      "claim": "Completing the objective produces a visible result.",
      "execution_records": [ /* same shape as above, non-empty */ ],
      "status": "gap",
      "player_impact": "Completion is not visible to the player.",     // required for gap_records only
      "recommended_update": "Add and replay a result state."          // required for gap_records only
    }
  ],
  "planner_handoff": {                  // required object
    "preservation_constraints": ["Preserve verified player movement."],   // required array, may be empty only if iteration == 1
    "update_targets": ["Implement a visible completion state."],          // required array, may be empty only if qa_status == "verified" (GB-3)
    "validation_requirements": ["Replay objective completion through the result screen."]  // required array
  }
}
```

## Field rules

- **`head_sha`** (GB-4): required at the packet root, never optional. This is Kit/Lane's
  freeze binding — evidence is produced against exactly one candidate commit. If a
  packet's `head_sha` does not match the SHA the tester was told to hold, that is a
  `head_sha mismatch` (see `--expect-head-sha` below), not a soft warning.
- **`qa_status` / every record's `status`** (GB-1/GB-6): exactly `verified | gap`, at
  **both** levels. `scripts/validate_evidence_packet.py` rejects any other literal
  string at either level — including the paper's own `"partial"`, a `"blocked"` value,
  and `"looks good"`. This is the mechanical analog of the spec-gate's "the stamp is the
  literal word" rule, applied to QA evidence instead of a human approval. A packet can
  be invalid at **both** levels in **either direction** at once (a bad `qa_status`
  paired with a bad record `status`, or the reverse) — the validator checks both
  independently and reports every mismatch it finds, not just the first.
- **`execution_records`** (GB-1): exactly `screenshot | runtime_trace | fixture`
  (narrowed from the paper's `replay | runtime_trace | screenshot` — `fixture` replaces
  `replay`, meaning the evidence is a named `skills/black-box-agent-qa`-style `case.json`
  run rather than a game replay file). Must be **non-empty** for every record — an empty
  array is a gap, not a pass, even on a record claiming `status: "verified"`.
- **`planner_handoff`** (GB-3): `update_targets` must be non-empty unless
  `qa_status == "verified"` (a gap packet with nothing to update is a contradiction);
  `preservation_constraints` must be non-empty unless `iteration == 1` (iteration 1 has
  nothing yet to preserve). This is the structural half of GB-3 ("each increment repairs
  gaps and delivers a new capability") — checked mechanically, not by prose promise.
- **Forbidden living PII** (its own named mechanical check class): no claim,
  observation, `player_impact`, `recommended_update`, or handoff string may contain a
  living person's real name used as if referring to a real teammate (the forbidden
  fixture pair is `"Lisa"` / `"Tanya"` — named here only as the fixture, never permitted
  content) or a phone number outside the reserved fictitious range `+1555XXXXXXX` (US
  NANP standard for fictional numbers). If this same failure class is already checked
  somewhere in `arm`/wiki tooling, a second sighting is REPEAT
  (`skills/triage-review-feedback/SKILL.md` Step 3), not a new finding each time.

## Validator usage

```bash
# Validate one or more packets independently
python3 scripts/validate_evidence_packet.py <E_t.json> [<E_t.json> ...]

# GB-4 freeze check: fail if the packet's head_sha does not match the held candidate SHA
python3 scripts/validate_evidence_packet.py --expect-head-sha <sha> <E_t.json>

# GB-6 retry-then-escalate: validate the first attempt, retry once on the second,
# ESCALATE if both are invalid
python3 scripts/validate_evidence_packet.py --retry-then-escalate <attempt-1.json> <attempt-2.json>
```

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Every given packet is valid (and matches `--expect-head-sha`, when given). |
| `1` | At least one packet is invalid, or `--retry-then-escalate` exhausted its one retry (prints `ESCALATE`). |
| `2` | **Never emitted by this validator.** Reserved for `scripts/run_black_box_fixture.py`'s own `"blocked"` (environment) verdict — e.g. a missing `python3` executable or a timeout. A GB-6 escalation is a real, checkable schema failure on two real attempts; it is never the same thing as the runner being unable to execute the command at all, and this house convention keeps the two literally distinct exit codes so they are never conflated. |

## Companion checks

| Fixture area | Script | What it checks |
|---|---|---|
| `E_t.json` schema | `scripts/validate_evidence_packet.py` | Everything above |
| `Dt` Preservation Gate heading (GB-2) | `scripts/validate_preservation_gate.py` | See `skills/preservation-gate/SCHEMA.md` equivalent (the heading rule lives in `skills/preservation-gate/SKILL.md`) |
| Planner reads `E_t.json` (H-1) | `scripts/check_planner_reads_et.py` | Plan template names the exact `evidence/E_t.json` path |
| Evidence index is progressive (H-5) | `scripts/check_evidence_index_is_progressive.py` | `evidence/INDEX.md` links to files instead of dumping their contents |

## Worked examples in this repo

Nine named fixtures under `fixtures/<case-name>/` (plus one under
`skills/preservation-gate/fixtures/dt-missing-preservation-gate/` for the Preservation
Gate check) — every one is a real, runnable `case.json` executed end-to-end by
`scripts/run_black_box_fixture.py` and by `tests/test_evidence_packet_protocol_fixtures.py`
(the `attack-12-fixture-io` mechanical check: argv/exit/stdout, red-then-green, never a
comment). See each fixture's own `README.md` for what it proves.
