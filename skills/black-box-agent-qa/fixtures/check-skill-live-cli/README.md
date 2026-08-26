# Fixture: a non-unittest system under test

**Why this fixture exists**: the first two worked examples in this directory
(`repeat-lock-mechanical-check/`, `close-out-live-gate-check/`) both run
`python3 -m unittest ...`. On their own, that narrows what the runner has actually been
shown to exercise — a reviewer could reasonably ask whether `scripts/run_black_box_fixture.py`
only knows how to score `unittest`'s specific stdout/stderr/exit-code shape, or whether it
really works against an arbitrary subprocess as the schema claims.

**Input fixture**: run `python3 scripts/check_skill_live.py black-box-agent-qa` from the
repo root — a plain CLI script, no test runner in the loop at all.

**Expected output**: exit code `0`, stdout contains `live-eligible`.

**What this is evidence for**: `scripts/run_black_box_fixture.py`'s I/O contract is generic —
any `argv` + any exit-code/stdout/stderr expectation, not specifically a `unittest` wrapper.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/black-box-agent-qa/fixtures/check-skill-live-cli \
  --skill black-box-agent-qa \
  --out skills/black-box-agent-qa/black-box-run.json
```
