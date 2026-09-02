# Fixture: `et-schema-valid`

**REPEAT-closure class**: `attack-12-fixture-io` — argv/exit/stdout red-then-green. A
future REPEAT sighting on this fixture (e.g. the validator silently starts accepting an
invalid packet again) closes only when `tests/test_evidence_packet_protocol_fixtures.py`
(or an extension of it) goes red on the regression and green after the fix — never with
a comment or a prose note.

**Input fixture**: `python3 scripts/validate_evidence_packet.py
skills/evidence-packet-protocol/fixtures/et-schema-valid/E_t.sample.json`

**Expected output**: exit code `0`, stdout contains `valid`.

**What this is evidence for**: GB-1 (claim-bound evidence packet, typed
`execution_records`, `verified|gap` only) and GB-4 (a real 40-char `head_sha` at the
packet root) — a packet that fully satisfies `skills/evidence-packet-protocol/SCHEMA.md`
is accepted, not just rejected packets.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/evidence-packet-protocol/fixtures/et-schema-valid \
  --skill evidence-packet-protocol \
  --out skills/evidence-packet-protocol/black-box-run.json
```
