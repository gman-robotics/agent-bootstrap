# Agent-bootstrap hub verification map

This directory is the maintained source for verifying **user-facing hub behavior** — the CLI workflows agents and CI use to prove skills are live and INDEX listings are gated. Read this index before driving; use each feature file as the recipe.

## Baseline preconditions

- Repo root is `agent-bootstrap` with `AGENTS.md` and `skills/INDEX.md` present.
- Dependencies installed: `python3 -m pip install -r requirements-dev.txt`.
- `VERIFY_HUB_RUN_ID` set (or let helpers default one).
- `VERIFY_HUB_ARTIFACTS_DIR` created (default `/opt/cursor/artifacts/verify-hub/<RUN_ID>`).
- Run `.cursor/skills/verify-hub/bin/verify-hub-doctor` and require `verify-hub doctor: OK`.
- No shared long-lived instance: each drive is a subprocess from repo root.

## Driving conventions

- Start every recipe from the baseline unless preconditions say otherwise.
- Run commands from `git rev-parse --show-toplevel`.
- Use the `verify-hub` bin helpers for multi-step drives; they write `*.transcript` evidence.
- Do not report a feature verified if only a different entry point was exercised.

## Proof and skip reporting

- CLI proof includes command, exit code, and stdout/stderr captured in `$VERIFY_HUB_ARTIFACTS_DIR`.
- Mutation-sensitive flows (black-box fixtures) must show `verdict: pass` in the fixture output when applicable.
- Unreachable paths need the concrete prerequisite (missing Node, missing skill dir, etc.).

## Feature entry contract

Each feature file uses H1 title, one behavior paragraph, then four H2 sections: `Sub-features`, `How to get to it (user POV)`, `Driving it with verify-hub`, `Gotchas`.

## Features

- [INDEX live gate](./index-live-gate.md) — `scripts/index_skills.py` binds INDEX.md to black-box live records.
- [Per-skill live check](./check-skill-live.md) — `scripts/check_skill_live.py` for one skill name.
- [Unit test suite](./unittest-suite.md) — `python3 -m unittest discover -s tests` (hub regression suite).
- [Pstack skill structure validation](./pstack-skill-validation.md) — `scripts/validate_pstack_skill.py`.
- [Black-box fixture run](./black-box-fixture.md) — `scripts/run_black_box_fixture.py` for a skill fixture.
