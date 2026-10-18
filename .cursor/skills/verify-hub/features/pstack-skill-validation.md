# Pstack skill structure validation

Pstack-ported skills must satisfy mechanical structure rules enforced by `scripts/validate_pstack_skill.py` (companions, provenance, forbidden phrases).

## Sub-features

- `pstack-ok-line` — prints `OK: <skill-name>` on success.
- `pstack-structure-fail` — non-zero when SKILL.md violates validators.

## How to get to it (user POV)

- Run `python3 scripts/validate_pstack_skill.py <skill-name>` for a pstack-listed skill (see `tests/test_pstack_skills.py` for the set).

## Driving it with verify-hub

Preconditions:

- Repo root, dev deps installed.

- **Example skill.** Run `python3 scripts/validate_pstack_skill.py create-verification-skill` and save transcript to `${VERIFY_HUB_ARTIFACTS_DIR}/validate-pstack-create-verification-skill.transcript`. Expect exit `0` and `OK: create-verification-skill` in stdout.
- **Proof.** Transcript captures command output; exit code 0.

## Gotchas

- Not every hub skill is a pstack skill — running the validator on arbitrary names may error; pick from the pstack set in tests.
- Validator edits require updating companion reverse pointers; see `skills/close-out` Step 9 for live gate after SKILL.md changes.
