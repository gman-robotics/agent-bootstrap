# Per-skill live check

Before listing a skill in INDEX or trigger tables, the hub requires `scripts/check_skill_live.py <name>` to pass against `skills/<name>/black-box-run.json` and the current `SKILL.md` hash.

## Sub-features

- `live-pass` — exit 0 with `live-eligible` message when record matches.
- `live-stale` — fail when `skill_sha256` mismatches edited SKILL.md.
- `live-missing-record` — fail when no `black-box-run.json`.

## How to get to it (user POV)

- Run `python3 scripts/check_skill_live.py <skill-name>` from repo root after capturing a black-box pass for that skill.

## Driving it with verify-hub

Preconditions:

- `verify-hub doctor` OK.
- Target skill exists under `skills/<name>/` with a captured pass (CI uses `create-verification-skill` as the representative).

- **Representative skill.** Run `.cursor/skills/verify-hub/bin/verify-hub-drive-check-skill-live create-verification-skill`. Exit `0` and transcript contains `live-eligible`.
- **Another skill.** Replace the argument with any live-gated skill name from INDEX.md.
- **Proof.** `${VERIFY_HUB_ARTIFACTS_DIR}/check-skill-live-<name>.transcript` holds stdout.

## Gotchas

- Skill names use hyphens exactly as in INDEX (`create-verification-skill`, not `create_verification_skill`).
- `--skill-dir` exists for non-standard paths; verify-hub helpers use the standard `skills/` layout only.
- Failing live check does not auto-fix; capture a new fixture via `scripts/run_black_box_fixture.py`.
