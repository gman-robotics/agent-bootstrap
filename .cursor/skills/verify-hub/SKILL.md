---
name: verify-hub
description: >-
  Drive the agent-bootstrap hub the way an agent does: Python CLIs under scripts/,
  INDEX live gate, and skill black-box records. Use before shipping hub skill or
  CI changes, or when maintain-verification-skill reports drift.
version: 1.0.0
---

# verify-hub

Verification skill for **gman-robotics/agent-bootstrap** (the multi-agent skills hub). There is no web UI or long-lived server: the user-facing surface is **CLI scripts** agents run from the repo root after `pip install -r requirements-dev.txt`.

## Launch

**Prepare (once per machine / CI job):**

```bash
cd "$(git rev-parse --show-toplevel)"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-dev.txt
```

**Ready when:** `python3 -c "import yaml"` succeeds and `test -f AGENTS.md`.

There is no daemon to keep alive. Each **Drive** step is a fresh subprocess. Set an isolated artifacts directory per run:

```bash
export VERIFY_HUB_RUN_ID="${VERIFY_HUB_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
export VERIFY_HUB_ARTIFACTS_DIR="${VERIFY_HUB_ARTIFACTS_DIR:-/opt/cursor/artifacts/verify-hub/${VERIFY_HUB_RUN_ID}}"
mkdir -p "$VERIFY_HUB_ARTIFACTS_DIR"
```

**Teardown:** This hub does not leave ports or background processes. Cleanup only removes optional scratch dirs you created under `/tmp/verify-hub-*` (see **Cleanup**). Do not stop unrelated Python processes.

## Doctor

Read-only gate: is this checkout worth driving?

```bash
.cursor/skills/verify-hub/bin/verify-hub-doctor
```

Requires exit code `0` and a line `verify-hub doctor: OK`. Run doctor before the first drive, after any failed drive, and whenever a command fails unexpectedly.

## Drive

Harness recipe: **bash helpers + captured transcripts** under `$VERIFY_HUB_ARTIFACTS_DIR`. Prefer stable script paths and documented stdout lines over brittle greps.

| Goal | Helper |
|------|--------|
| INDEX.md live binding | `bin/verify-hub-drive-index-live-gate` |
| One skill live gate | `bin/verify-hub-drive-check-skill-live create-verification-skill` |
| Full PR CI bundle (doctor + drives) | `bin/verify-hub-ci` |

Feature-level recipes and sub-features live in `features/` — read `features/README.md` before driving; a proof that only hits one entry point is incomplete when the map lists others.

**Example (one mapped feature — INDEX live gate):**

```bash
export VERIFY_HUB_RUN_ID="manual-$(date -u +%Y%m%dT%H%M%SZ)"
export VERIFY_HUB_ARTIFACTS_DIR="/opt/cursor/artifacts/verify-hub/${VERIFY_HUB_RUN_ID}"
mkdir -p "$VERIFY_HUB_ARTIFACTS_DIR"
.cursor/skills/verify-hub/bin/verify-hub-doctor
.cursor/skills/verify-hub/bin/verify-hub-drive-index-live-gate
```

## Evidence

Proof standards for this repo:

- Exercise the **real** agent path (`python3 scripts/...` from repo root), not test-only shortcuts.
- Capture **command + exit code + stdout/stderr** for each drive step into `$VERIFY_HUB_ARTIFACTS_DIR` (`*.transcript` files).
- For the INDEX live gate, stdout must include `Every non-grandfathered INDEX.md entry is live-eligible.`
- Side effect check: `scripts/index_skills.py` exit code `0` (no ungated INDEX entries).

Artifacts intentionally survive cleanup. Default location: `/opt/cursor/artifacts/verify-hub/<RUN_ID>/`.

## Cleanup

- Remove only scratch dirs this run created: `rm -rf "/tmp/verify-hub-${VERIFY_HUB_RUN_ID}"` if present.
- **Never** `pkill` by process name.
- Do **not** delete `$VERIFY_HUB_ARTIFACTS_DIR` during cleanup — proofs must remain for review.

## Helpers

All helpers are executable bash scripts in `.cursor/skills/verify-hub/bin/`:

- `verify-hub-doctor` — environment and repo layout checks.
- `verify-hub-drive-index-live-gate` — runs `python3 scripts/index_skills.py`, saves transcript, asserts success line.
- `verify-hub-drive-check-skill-live <skill-name>` — runs `python3 scripts/check_skill_live.py <skill-name>`.
- `verify-hub-ci` — doctor, INDEX live gate drive, and live check for `create-verification-skill` (used by GitHub Actions).

## Maintenance

After hub skill or CI changes, run `maintain-verification-skill` against this directory (`.cursor/skills/verify-hub/`).
