# Fixture: `dt-missing-preservation-gate`

**REPEAT-closure class**: `attack-12-fixture-io` — argv/exit/stdout red-then-green. A
future REPEAT sighting on this fixture closes only when
`tests/test_evidence_packet_protocol_fixtures.py` (or an extension of it) goes
red-then-green against the real argv/exit/stdout — never with a comment or another
prose note in a plan document.

**Input fixture**: `python3 scripts/validate_preservation_gate.py
skills/preservation-gate/fixtures/dt-missing-preservation-gate/Dt.sample.md`

**Expected output**: exit code `1`, stdout contains `Preservation Gate`.

**What this is evidence for**: GB-2 — a development-document markdown (`Dt`) from
iteration 2 onward must have the exact `## Preservation Gate` heading naming the
previous iteration's verified claims to protect. `Dt.sample.md` has a `## Summary`,
`## Update Targets`, and `## Validation Requirements` section but no `## Preservation
Gate` section, so it must be rejected — this is a distinct mechanism from REPEAT
(`skills/triage-review-feedback/SKILL.md` Step 3), which tracks recurring *failure*
classes in PR review, not verified-good behavior in a plan document.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/preservation-gate/fixtures/dt-missing-preservation-gate \
  --skill preservation-gate \
  --out skills/preservation-gate/black-box-run.json
```
