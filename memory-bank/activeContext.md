# Active Context: Multi-Agent Skills Hub

## Current Focus (This Session)
**label-adjudication skill** (2026-09-21, branch `feat/label-adjudication-skill`): New skill for two-model JSONL labeling + adjudicator on disagreements; deterministic merge via `scripts/adjudicate_labels.py`; black-box fixture `merge-agree-and-adjudicated`; live gate `check_skill_live.py label-adjudication` → 0.

**Verification**: `python3 -m unittest discover -s tests` — 119/119 pass after add; `python3 scripts/check_skill_live.py label-adjudication` → live-eligible.

**Next**: Open PR; human review.
