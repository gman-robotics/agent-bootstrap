# Fixture: `schema-retry-then-escalate`

**REPEAT-closure class**: `attack-12-fixture-io` — argv/exit/stdout red-then-green.

**Blair pass 2 should-fix**: the plan's original table used exit code `2` for this
fixture. `scripts/black-box-agent-qa/SCHEMA.md`'s exit-code convention already reserves
`2` for the runner's own `"blocked"` verdict (an environment problem — a missing
executable or a timeout), which is never a pass and never something the script under
test emits itself. Conflating "GB-6 escalate" with "environment blocked" would make an
escalation look like an infrastructure failure instead of what it actually is: two
consecutive invalid packets. This fixture's house convention is **exit code `1`** for
escalate, with `ESCALATE` printed to stdout — documented in
`skills/evidence-packet-protocol/SCHEMA.md` "Exit codes".

**Input fixture**: `python3 scripts/validate_evidence_packet.py --retry-then-escalate
skills/evidence-packet-protocol/fixtures/schema-retry-then-escalate/invalid-1.json
skills/evidence-packet-protocol/fixtures/schema-retry-then-escalate/invalid-2.json`

**Expected output**: exit code `1`, stdout contains `ESCALATE`.

**What this is evidence for**: GB-6 — one retry on a schema-invalid packet, then
escalate to CoS/human review, never an unbounded silent reinvoke loop. Both sample
packets here are deliberately invalid (`qa_status: "blocked"` and `qa_status:
"partial"` respectively) so the one allowed retry is exhausted for real.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/evidence-packet-protocol/fixtures/schema-retry-then-escalate \
  --skill evidence-packet-protocol \
  --out skills/evidence-packet-protocol/black-box-run.json
```
