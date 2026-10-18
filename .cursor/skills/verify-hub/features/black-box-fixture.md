# Black-box fixture run

Skills ship `fixtures/<case>/case.json` plus `scripts/run_black_box_fixture.py` to capture real execution evidence into `black-box-run.json`.

## Sub-features

- `fixture-pass` — exit 0 with expected stdout fragments from case.json.
- `fixture-capture` — writes/updates run record used by `check_skill_live.py`.

## How to get to it (user POV)

- From repo root: `python3 scripts/run_black_box_fixture.py skills/<skill>/fixtures/<case>` (see `skills/black-box-agent-qa/SKILL.md`).

## Driving it with verify-hub

Preconditions:

- Fixture path exists under `skills/<skill>/fixtures/`.
- Do not commit scratch run records unless intentionally recapturing.

- **Read-only smoke.** Run `python3 scripts/run_black_box_fixture.py skills/create-verification-skill/fixtures/skill-structure-check` with transcript at `${VERIFY_HUB_ARTIFACTS_DIR}/black-box-create-verification-skill.transcript`. Expect exit `0` and `OK: create-verification-skill` in output.
- **Proof.** Transcript + exit code; optional diff of run record only when recapture is the goal.

## Gotchas

- Recapturing overwrites `black-box-run.json` and changes `skill_sha256` expectations — only recapture when SKILL.md or fixture changed on purpose.
- Some fixtures need Node or other tools; structure-check fixtures for pstack skills are Python-only.
- Never treat reading SKILL.md alone as a pass; the script must execute.
