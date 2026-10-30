---
name: create-verification-skill
description: >-
  Generate a project-local verification skill that drives your app the way a
  user does. Use when a project has no scripted way to prove UI/CLI/service
  behavior.
version: 1.2.0
---

# create-verification-skill

**Purpose**
Generate a project-local verification skill that drives the app the way a user does and seeds an initial feature map.

**Trigger**
"make a control skill for this repo" or when a project has no scripted way to prove UI/CLI/service behavior.

**Do not use for**
- Auditing an existing verify skill → `maintain-verification-skill`
- One-off manual test without a durable skill → run the test directly

## Companions

| Skill | Role here |
|---|---|
| `maintain-verification-skill` | Periodic upkeep loop offered after generation |
| `black-box-agent-qa` | Live-gate pattern when the generated skill ships in this hub |
| `pstack-principles` | prove-it-works — generated skill must be executed once before handover; build-the-lever — repeated launch, doctor, and drive steps ship as rerunnable helpers |

**Verification**
- Repo interviewed (surface, run, drive, observe, isolate)
- Generated skill launched, doctored, drove one feature, captured evidence, cleaned up
- Feature map seeded under `skills/verify-<app>/features/`
- Any launch, doctor, or drive step of more than one command ships as an executable helper (build-the-lever)

---

# create-verification-skill

Generate a project-local verification skill that drives your app the way a user does — any language, framework, or platform. Use for /create-verification-skill, \"make a control skill for this repo\", or when a project has no scripted way to prove UI/CLI/service behavior.

Every serious project needs a scripted way to drive the real app and prove behavior: launch it, exercise a feature the way a user would, and capture evidence. This skill generates that as a project-local skill (`skills/verify-<app>/`) tailored to the repo. You write the generator's output for the next agent, not for a human: it will be read cold, mid-task, by an agent that has never seen the app.

## 1. Interview the repo, not the user

Answer these from the codebase and only ask the user what you cannot observe:

- **Surface:** what does a user actually touch? A web UI, a CLI/TUI, a desktop app, an API, a mobile app, a library? A repo can have several; pick the primary one and note the rest.
- **Run:** how does the app start locally? Prefer the repo's own documented dev command (package scripts, Makefile, README quickstart). Note ports, env vars, seed data, auth.
- **Drive:** how can an agent interact with it programmatically? Existing harnesses first — Playwright/Cypress specs, expect scripts, PTY helpers, curl-able endpoints, a debug port. Only then pick a generic recipe: browser/CDP for web and Electron, a tmux/PTY harness for CLI/TUI, plain HTTP for services.
- **Observe:** what evidence can be captured? Screenshots, terminal transcripts, response bodies, logs, exit codes, DB state.
- **Isolate:** can two instances run side by side (ports, data dirs, profiles)? If not, say so in the generated skill: refusing to double-drive a shared instance beats corrupting the user's session.

If the checkout doesn't build or start as-is, fix that first (or report it precisely) before generating; a skill written against a broken base teaches wrong steps. When an irrelevant missing asset blocks startup (a static dir the API never serves, a sample config), the generated skill may create it, clearly marked as verification scaffolding, and remove it in cleanup.

## 2. Generate the skill

Write `skills/verify-<app>/SKILL.md` with YAML frontmatter (`name: verify-<app>` and a `description` that names the app, the surface, and when to reach for it — without frontmatter the skill never registers) and these sections, each grounded in what the interview actually found (no placeholders left):

- **Launch:** the exact command that starts the app for verification, and how to tell it's ready (a log line, a port answering, a prompt). Include teardown. For a short-lived CLI or TUI there is no server to keep alive: launch means build the binary (or install deps) once, then start each drive in its own isolated PTY or tmux session.
- **Doctor:** one read-only check that answers "is this instance worth driving?" — process up, right version/build, port owned by us, auth valid. An agent runs this first whenever anything looks off.
- **Drive:** the harness recipe with real selectors/commands from this repo, not examples. Prefer stable handles (ARIA labels, data attributes, prompt strings, route paths) over coordinates and tab order.
- **Evidence:** what to capture for a proof and where it goes. State the proof standards: exercise the real user path, not internal setters or test-only endpoints; capture the action and the resulting state, not just the final screen; verify side effects (files written, rows inserted, messages sent) alongside what's visible; mocks only where a production boundary already isolates the external system. When the safe path is a dry-run or test mode, verify what it actually skips by observing (files, network, git refs) rather than trusting its name: some dry-runs still touch the network or open a browser.
- **Cleanup:** how to tear down instances the run created. Never kill by process name; kill what you started. Cleanup removes instances and scratch state, never the evidence: proof artifacts survive the teardown, in a location the skill names.
- **Helpers:** any script the skill ships is executable and its invocation is shown in the skill body. A helper the reader has to reverse-engineer is not a helper. A step the next agent would otherwise retype (launch, doctor, a drive of more than one command) ships as a helper script, per the **pstack-principles** (build-the-lever) principle. Prose alone is not a lever.
- **CI bundle (`bin/verify-<app>-ci`):** one script that runs doctor, coverage-backed tests, drives, and the **advisory** ub-mode report wrapper. The verify bundle calls `scripts/run_ub_gates_report.sh` (`UB_GATES_ADVISORY=1`) and exits 0 on gate debt. The separate **`ub-gates`** CI job calls `scripts/run_ub_gates_ci.sh` and is blocking by default (`UB_GATES_ADVISORY=0`). Copy and adapt [`references/verify-ci-ub-gates.sh`](references/verify-ci-ub-gates.sh) or call the repo's `scripts/run_ub_gates_report.sh` when bootstrapped from agent-bootstrap.

### ub-mode gates in verify-ci (GMA-410, report wrapper only)

Ship these in every generated `verify-<app>-ci` (or document why the stack has no unclebob gates):

| Step | Rule |
| --- | --- |
| Coverage | Run the stack's coverage command before gates (`pytest --cov` / `pytest-cov`, `coverage run`, JaCoCo, `go test -coverprofile`, etc.) so **crapper** and **mutator** can read profiles when tools exist (`docs/shared/ub-mode-practice.md`). |
| Scope | Build the merge-base path list (`git merge-base` → `git diff --name-only --diff-filter=ACMRT`); pass explicit paths to **crapper** and **dryer**. Do **not** use upstream `--changed` for committed PR scope (it reads `git status`). |
| crapper | `crapper --threshold 10` on scope paths. |
| dryer | `rm -f .metrics/dry.edn` then `dryer --threshold 0.8` on scope; parse `.metrics/dry.edn` for `:score` ≥ 0.8. |
| mutator | The report wrapper may skip mutator when `CURSOR_AGENT` is set and `GITHUB_ACTIONS` is unset. In the blocking **`ub-gates`** job that skip is `skipped_mutator` and fails. Run mutator via `bash scripts/ub_gates_container.sh` before the PR. |
| Outcomes | Reuse hub names: `ran_clean`, `ran_with_findings`, `skipped_no_scope`, `skipped_tools_missing`, `skipped_mutator`, `tool_error` (see `scripts/run_ub_gates_ci.sh`). Write to `.metrics/verify-ub-outcome.txt` or `.metrics/ub-gates-outcome.txt`. |
| Exit code | verify-ci **always exits 0** because it uses the report wrapper (`UB_GATES_ADVISORY=1`). Record outcomes in the skill **Evidence** section and PR **`Gates:`** line. The blocking `ub-gates` job exits 1 on findings in changed scope. |

## 2.5. Wire agent harness files (GMA-410)

After generating `skills/verify-<app>/`, ensure agent harness entrypoints tell every harness to load project standards, run verify/ub checks before a PR, and use the PR template. **Never skip a file because it already exists** — edit in place.

Run (from the target repo root; `repo-id` defaults to the directory basename):

```bash
python3 /path/to/agent-bootstrap/scripts/sync_agent_harness_instructions.py \
  --repo-root . \
  --repo-id <repo-id>
```

The script is idempotent: it upserts a single delimited block (`<!-- agent-bootstrap-hub:BEGIN harness-workflow -->` … `END`) in `AGENTS.md`, `CLAUDE.md`, `.grok/README.md`, and `.cursor/rules/<repo-id>-harness.mdc`. Missing files are created with minimal safe defaults; existing prose outside the block is unchanged.

Copy the hub PR template when `.github/PULL_REQUEST_TEMPLATE.md` is missing (body starts at `Tier:` — same as the hub `.github/PULL_REQUEST_TEMPLATE.md`, not the doc title in `docs/shared/hub-pull-request-template.md`):

```bash
mkdir -p .github
python3 /path/to/agent-bootstrap/scripts/hub_pull_request_template.py copy --out .github/PULL_REQUEST_TEMPLATE.md
```

Verify after copy (or on maintain passes):

```bash
python3 /path/to/agent-bootstrap/scripts/hub_pull_request_template.py check --file .github/PULL_REQUEST_TEMPLATE.md
```

(`create-repo-standards` uses the same commands; do not maintain a second template shape.)

Fixture proof: `skills/create-verification-skill/fixtures/agent-harness-sync/` (pre-existing `AGENTS.md` content preserved; second run is a no-op).

## 3. Seed the feature map

Create `skills/verify-<app>/features/README.md` plus one file per user-facing feature you can identify (aim for the top 3-5 to start, from routes, commands, menus, or docs). Follow the shape in [`references/feature-map-example/`](references/feature-map-example/), with a README index and one file per feature. Each file answers, from the user's point of view: what the feature is, how to reach it, how to drive it with the harness, and what observable end state proves it works. The four H2s are `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, and `Gotchas`. The map is the repo's maintained verification source; a proof that drives one convenient entry point is incomplete when the map lists others.

## 4. Prove the generated skill before handing it over

Run its own instructions end to end once: launch, doctor, drive ONE mapped feature (one is enough; the map exists so later runs can cover the rest), capture evidence, clean up. After cleanup, confirm the evidence still exists at the named location — a cleanup that eats the proof fails this step. Fix what fails, and run the generated cleanup after every failed iteration too, so broken attempts don't strand processes and ports. A generated skill that was never executed is a draft, not a deliverable.

## 5. Offer the maintenance loop

Point the user at `maintain-verification-skill` for keeping the map honest as the app changes. Suggest a cadence only if they ask.

## Provenance

Adapted from [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT). Native multi-harness hub playbook — not a marketplace plugin copy. Cursor-only harness names stripped per `skills/subagent-routing/SKILL.md`.

*Last updated: 2026-10-26 | Hub version: 0.14.0*
