# Unit test suite

The hub's regression suite lives under `tests/` and runs with the stdlib unittest discovery entrypoint agents already use locally and in CI.

## Sub-features

- `unittest-discover` — full `tests/` package discovery.
- `unittest-summary` — `Ran N tests` and `OK`, `OK (skipped=N)`, or `FAILED` footer.

## How to get to it (user POV)

- From repo root: `python3 -m unittest discover -s tests` after `pip install -r requirements-dev.txt`.

## Driving it with verify-hub

Preconditions:

- Dev requirements installed.
- Repo root cwd.

- **Full suite.** Run `python3 -m unittest discover -s tests` and tee to `${VERIFY_HUB_ARTIFACTS_DIR}/unittest.transcript`. Require exit `0` and a final summary line `OK` or `OK (skipped=N)` (not necessarily the last line of stderr).
- **Proof.** Transcript must include a `Ran ` summary line; keep the real footer line for PR evidence.

## Gotchas

- Some tests emit intentional stderr (evidence-packet escalation fixtures); judge pass/fail on exit code and unittest summary, not stderr silence.
- CI runs discovery in **`unittest-and-live-gate`** (`python -m unittest discover -s tests` plus `python3 scripts/index_skills.py`) and again inside **`verify-hub`** (`verify-hub-ci`, which also runs the INDEX live gate drives, this suite with coverage when `coverage` is installed, then advisory ub-gates).
- Full suite is slow (~3 minutes on a cold VM); `verify-hub-ci` always includes it — plan time accordingly when driving the full bundle locally.
