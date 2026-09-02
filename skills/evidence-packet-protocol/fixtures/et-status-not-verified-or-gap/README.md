# Fixture: `et-status-not-verified-or-gap` (crossed enum pair)

**REPEAT-closure class**: `attack-12-fixture-io` — argv/exit/stdout red-then-green. A
future REPEAT sighting on this fixture closes only when
`tests/test_evidence_packet_protocol_fixtures.py` (or an extension of it) goes
red-then-green against the real argv/exit/stdout — never with a comment.

**Why two sample packets, not one**: an earlier draft of this fixture shipped a single
packet with a bad packet-level `qa_status` and a bad record-level `status` together,
which only proves the validator can report both mismatches when they happen to occur in
the *same* direction. Blair pass 2 required the crossed case: `qa_status: "partial"`
paired with a record `status: "blocked"` (`E_t.partial-blocked.json`), **and** the
reverse, `qa_status: "blocked"` paired with a record `status: "partial"`
(`E_t.blocked-partial.json"`) — two distinct sample packets, both invalid, run in the
same command.

**Input fixture**: `python3 scripts/validate_evidence_packet.py
skills/evidence-packet-protocol/fixtures/et-status-not-verified-or-gap/E_t.partial-blocked.json
skills/evidence-packet-protocol/fixtures/et-status-not-verified-or-gap/E_t.blocked-partial.json`

**Expected output**: exit code `1`; stdout contains all four literal tokens:
`invalid qa_status: partial`, `invalid record status: blocked`, `invalid qa_status:
blocked`, `invalid record status: partial`.

**What this is evidence for**: GB-1/GB-6 — `qa_status` (packet root) and every record's
`status` are restricted to `verified | gap` only, checked independently at both levels,
in both directions, not just the direction a single fixture happened to test first.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/evidence-packet-protocol/fixtures/et-status-not-verified-or-gap \
  --skill evidence-packet-protocol \
  --out skills/evidence-packet-protocol/black-box-run.json
```
