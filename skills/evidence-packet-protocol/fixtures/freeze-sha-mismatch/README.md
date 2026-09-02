# Fixture: `freeze-sha-mismatch`

**REPEAT-closure class**: `attack-12-fixture-io` — argv/exit/stdout red-then-green.

**task-instruction should-fix**: an earlier draft of this fixture's `case.json` used a
`<candidate-sha>` placeholder in the argv, which is not something anyone could actually
copy-paste and run. This fixture instead ships two real, distinct, copy-paste-literal
40-character hex SHAs: the packet's own `head_sha` is `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
(all `a`), and the command's `--expect-head-sha` argument is
`bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb` (all `b`) — a real argv someone can paste
verbatim into a shell, not a template.

**Input fixture**: `python3 scripts/validate_evidence_packet.py --expect-head-sha
bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
skills/evidence-packet-protocol/fixtures/freeze-sha-mismatch/E_t.sample.json`

**Expected output**: exit code `1`, stdout contains `head_sha mismatch`.

**What this is evidence for**: GB-4 (Kit/Lane's evidence is frozen to one git SHA) — if
the candidate advances (or the tester was pointed at the wrong commit), the packet's
`head_sha` will not match the SHA the tester was told to hold, and the mismatch is
caught mechanically rather than silently accepted.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/evidence-packet-protocol/fixtures/freeze-sha-mismatch \
  --skill evidence-packet-protocol \
  --out skills/evidence-packet-protocol/black-box-run.json
```
