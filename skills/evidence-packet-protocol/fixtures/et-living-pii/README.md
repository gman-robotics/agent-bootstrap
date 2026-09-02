# Fixture: `et-living-pii`

**REPEAT-closure class**: `attack-12-fixture-io` — argv/exit/stdout red-then-green.

**Input fixture**: `python3 scripts/validate_evidence_packet.py
skills/evidence-packet-protocol/fixtures/et-living-pii/E_t.sample.json`

**Expected output**: exit code `1`, stdout contains `living-pii`.

**What this is evidence for**: the forbidden living-PII check class
(`skills/evidence-packet-protocol/SCHEMA.md` "Forbidden living PII") — no claim or
observation may contain a living person's real name used as if referring to a real
teammate. `E_t.sample.json` puts `"Lisa confirmed the avatar moved as expected..."` in
one `execution_records[].observation` field. `"Lisa"`/`"Tanya"` are named here only as
the forbidden fixture pair per the task instructions — this repo does not contain a real
person's phone number anywhere (the reserved `+1555XXXXXXX` fictitious range is the only
phone-shaped value used in any sample, see the `et-schema-valid` and this fixture's
sibling samples).

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/evidence-packet-protocol/fixtures/et-living-pii \
  --skill evidence-packet-protocol \
  --out skills/evidence-packet-protocol/black-box-run.json
```
