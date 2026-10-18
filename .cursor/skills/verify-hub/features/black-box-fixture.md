# Black-box fixture run

Skills ship `fixtures/<case>/case.json` plus `scripts/run_black_box_fixture.py` to capture real execution evidence into `black-box-run.json`.

## Sub-features

- `fixture-pass` — exit 0 with expected stdout fragments from case.json.
- `fixture-capture` — writes/updates run record used by `check_skill_live.py`.

## How to get to it (user POV)

- From repo root: `python3 scripts/run_black_box_fixture.py --fixture skills/<skill>/fixtures/<case> --skill <skill>` (optional `--out`; see `skills/black-box-agent-qa/SKILL.md`).

## Driving it with verify-hub

Preconditions:

- Fixture path exists under `skills/<skill>/fixtures/`.
- `VERIFY_HUB_ARTIFACTS_DIR` exists (set by doctor or drive helpers).

- **Read-only smoke.** Run from repo root (writes the run record under the artifact dir, not under `skills/`):

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/create-verification-skill/fixtures/skill-structure-check \
  --skill create-verification-skill \
  --out "${VERIFY_HUB_ARTIFACTS_DIR}/black-box-create-verification-skill-run.json"
```

Expect exit `0`, stdout JSON with `"verdict": "pass"`, and `"out"` pointing at the `--out` path. Without `--out`, the script defaults to `skills/<skill>/black-box-run.json` (mutates the tree — use `--out` for smoke).

- **Proof.** Capture stdout JSON + exit code; transcript optional. Do not commit artifact-dir run records.

## Gotchas

- Recapturing into `skills/<skill>/black-box-run.json` overwrites the live gate record and changes `skill_sha256` expectations — only recapture when SKILL.md or fixture changed on purpose.
- Some fixtures need Node or other tools; structure-check fixtures for pstack skills are Python-only.
- Never treat reading SKILL.md alone as a pass; the script must execute.
