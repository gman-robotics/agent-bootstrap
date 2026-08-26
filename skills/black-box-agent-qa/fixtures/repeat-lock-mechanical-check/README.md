# Fixture: REPEAT-lock mechanical check actually passes

**Input fixture**: run
`python3 -m unittest tests.test_export_codex_skills.ExportCodexSkillsTests.test_force_reexport_preserves_hand_added_reference_files -v`
from the repo root.

**Expected output**: exit code `0`, stderr contains `OK` (Python's default unittest runner
writes its summary, including the final `OK`, to stderr — verified against a real run before
this fixture was written).

**What this is evidence for**:
- `skills/triage-review-feedback/SKILL.md`'s REPEAT lock — the mechanical check named in its
  Step 3 (see `skills/triage-review-feedback/fixtures/repeat-exporter-dropped-references/`)
  really exists and really passes, not just described in prose.
- `skills/black-box-agent-qa/SKILL.md` itself — this fixture is what `scripts/run_black_box_fixture.py`
  actually executes to produce `skills/black-box-agent-qa/black-box-run.json` and
  `skills/triage-review-feedback/black-box-run.json`.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/black-box-agent-qa/fixtures/repeat-lock-mechanical-check \
  --skill black-box-agent-qa \
  --out skills/black-box-agent-qa/black-box-run.json
```
