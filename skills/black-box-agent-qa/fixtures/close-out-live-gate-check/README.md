# Fixture: close-out Step 9's live-flip gate actually works

**Input fixture**: run `python3 -m unittest tests.test_check_skill_live -v` from the repo root.

**Expected output**: exit code `0`, stderr contains `OK`.

**What this is evidence for**: `skills/close-out/SKILL.md` Step 9 requires
`scripts/check_skill_live.py <skill>` to exit `0` before a new/edited skill is treated as live.
This fixture actually runs the gate's own test suite — no-run-record, non-pass-verdict,
stale-hash-after-a-silent-refine, and the valid-pass case — so the gate is proven to work end
to end, not just asserted in Markdown.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/black-box-agent-qa/fixtures/close-out-live-gate-check \
  --skill close-out \
  --out skills/close-out/black-box-run.json
```
