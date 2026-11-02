# Hub bootstrap hygiene (PR template and harness sync)

Weekly `maintain-verification-skill` step **1c** checks that bootstrapped repos still carry the hub PR template and delimited harness workflow blocks. The **agent-bootstrap** repo itself is the hub source: PR template is installed here; harness blocks are synced **into consumer repos**, not required inside hub `AGENTS.md`.

## Sub-features

- `pr-template-check` — `scripts/hub_pull_request_template.py check` against `.github/PULL_REQUEST_TEMPLATE.md` (body from `Tier:` onward matches `docs/shared/hub-pull-request-template.md`).
- `harness-sync-verify` — `scripts/sync_agent_harness_instructions.py --repo-id <repo-id> --verify` on manifest projects.
- `harness-sync-restore` — selective `--restore` for paths reported missing (maintain skill edit-scope exception only).

## How to get to it (user POV)

- On **agent-bootstrap**: run the PR template check from repo root.
- On a **manifest child repo**: run harness `--verify`; restore only when maintain pass reports drift.

## Driving it with verify-hub

Preconditions:

- Repo root is agent-bootstrap for template check.

- **PR template (hub self).**

```bash
python3 scripts/hub_pull_request_template.py check --file .github/PULL_REQUEST_TEMPLATE.md
```

Expect exit `0` with no stdout on success.

- **Harness verify (hub self).** Running `--repo-id agent-bootstrap --verify` reports `MISSING` for harness blocks — expected on the hub checkout (no `standards-agent-bootstrap` consumer layout). Record as **verified-unreachable** on hub self with prerequisite: run on a bootstrapped project repo from `manifest.yaml`.
- **Proof.** Save check command exit code; for child repos, save verify/restore transcript under `$VERIFY_HUB_ARTIFACTS_DIR`.

## Gotchas

- Re-install template with `hub_pull_request_template.py copy --out .github/PULL_REQUEST_TEMPLATE.md` only when check fails.
- `--restore` may touch `AGENTS.md`, `CLAUDE.md`, `.grok/README.md`, and `.cursor/rules/<repo-id>-harness.mdc` — never run restore on hub self during verify-hub upkeep unless product owners explicitly dogfood blocks here.
- Canonical template edits belong in `docs/shared/hub-pull-request-template.md` first, then copy to `.github/`.
