# Fixture: `et-missing-execution-record`

**REPEAT-closure class**: `attack-12-fixture-io` — argv/exit/stdout red-then-green.

**Input fixture**: `python3 scripts/validate_evidence_packet.py
skills/evidence-packet-protocol/fixtures/et-missing-execution-record/E_t.sample.json`

**Expected output**: exit code `1`, stdout contains `execution_records`.

**What this is evidence for**: GB-1's "empty is a gap, not a pass" rule — a record
claiming `status: "verified"` with an empty `execution_records` array must be rejected,
not silently accepted as if the claim were checked.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/evidence-packet-protocol/fixtures/et-missing-execution-record \
  --skill evidence-packet-protocol \
  --out skills/evidence-packet-protocol/black-box-run.json
```
