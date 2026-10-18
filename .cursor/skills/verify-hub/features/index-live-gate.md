# INDEX live gate

Agents and CI use `scripts/index_skills.py` to ensure every non-grandfathered skill listed in `skills/INDEX.md` has a passing black-box run record matching current `SKILL.md`.

## Sub-features

- `index-scan` — parse INDEX.md `###` entries and compare to live gate.
- `index-success-line` — print the all-eligible success message on green runs.
- `index-fail-ungated` — non-zero exit when an ungated listing exists.

## How to get to it (user POV)

- From repo root after installing dev requirements, run the INDEX gate check (documented in `scripts/index_skills.py` header and `.github/workflows/test.yml`).

## Driving it with verify-hub

Preconditions:

- `verify-hub doctor` reports OK.
- `VERIFY_HUB_ARTIFACTS_DIR` exists.

- **Gate check.** Run `.cursor/skills/verify-hub/bin/verify-hub-drive-index-live-gate`. Exit code `0` and stdout contains `verify-hub drive index-live-gate: OK`. Transcript file contains `Every non-grandfathered INDEX.md entry is live-eligible.`
- **Proof.** Confirm `${VERIFY_HUB_ARTIFACTS_DIR}/index-live-gate.transcript` exists and matches the live command output.

## Gotchas

- Grandfathered skills in `scripts/index_skills.py` are intentionally allowed without run records; do not treat them as failures.
- Editing `SKILL.md` without recapturing `black-box-run.json` makes `check_skill_live` fail even when INDEX scan passes — fix the skill record, not INDEX prose.
- Run from repo root; `python3 scripts/index_skills.py` with wrong cwd may import the wrong tree.
