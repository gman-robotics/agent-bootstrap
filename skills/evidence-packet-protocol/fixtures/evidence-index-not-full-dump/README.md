# Fixture: `evidence-index-not-full-dump` (H-5)

**REPEAT-closure class**: `attack-12-fixture-io` — argv/exit/stdout red-then-green.

**Input fixture**: `python3 scripts/check_evidence_index_is_progressive.py
skills/evidence-packet-protocol/fixtures/evidence-index-not-full-dump/INDEX.sample.md`

**Expected output**: exit code `0`, stdout contains `progressive`.

**What this is evidence for**: H-5 — a progressive-disclosure index (one short summary
row + a pointer per iteration), not a full dump of every packet's fields, modeled on
this hub's own `skills/INDEX.md` convention.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/evidence-packet-protocol/fixtures/evidence-index-not-full-dump \
  --skill evidence-packet-protocol \
  --out skills/evidence-packet-protocol/black-box-run.json
```
