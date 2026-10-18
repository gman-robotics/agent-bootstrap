# Unit test suite

The hub's regression suite lives under `tests/` and runs with the stdlib unittest discovery entrypoint agents already use locally and in CI.

## Sub-features

- `unittest-discover` — full `tests/` package discovery.
- `unittest-summary` — `Ran N tests` and `OK` or `FAILED` footer.

## How to get to it (user POV)

- From repo root: `python3 -m unittest discover -s tests` after `pip install -r requirements-dev.txt`.

## Driving it with verify-hub

Preconditions:

- Dev requirements installed.
- Repo root cwd.

- **Full suite.** Run `python3 -m unittest discover -s tests` and tee to `${VERIFY_HUB_ARTIFACTS_DIR}/unittest.transcript`. Require exit `0` and final line `OK`.
- **Proof.** Transcript must include a `Ran ` summary line; keep the real footer line for PR evidence.

## Gotchas

- Some tests emit intentional stderr (evidence-packet escalation fixtures); judge pass/fail on exit code and unittest summary, not stderr silence.
- CI runs this in the separate `unittest-and-live-gate` job; verify-hub CI focuses on script-level drives — run unittest when validating broader hub changes.
- Long runtime (~minutes on cold VM); not part of `verify-hub-ci` to avoid duplicating the main job.
