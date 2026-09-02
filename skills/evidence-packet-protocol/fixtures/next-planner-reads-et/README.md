# Fixture: `next-planner-reads-et` (H-1)

**REPEAT-closure class**: `attack-12-fixture-io` — argv/exit/stdout red-then-green.

**Input fixture**: `python3 scripts/check_planner_reads_et.py
skills/evidence-packet-protocol/fixtures/next-planner-reads-et/plan-template.sample.md`

**Expected output**: exit code `0`, stdout contains `evidence/E_t.json`.

**What this is evidence for**: H-1 — the next planner must read the same `E_t.json` on
disk, not a summarized memory note. The sample plan template names the exact
`evidence/E_t.json` path convention before its own Preservation Gate section.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/evidence-packet-protocol/fixtures/next-planner-reads-et \
  --skill evidence-packet-protocol \
  --out skills/evidence-packet-protocol/black-box-run.json
```
