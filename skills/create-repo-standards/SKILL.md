---
name: create-repo-standards
description: "Interview a repository and generate a project-local standards-<repo> skill plus GitHub PR/issue templates so agents follow one PR format, issue format, planning rules, implementation workflow, and verification pointers. Use for /create-repo-standards on a manifest project. Do not run on agent-bootstrap hub-only Markdown unless explicitly asked."
version: 1.0.5
---

# create-repo-standards

**Purpose**
Encode how this repository expects work to be planned, implemented, verified, and described in GitHub — as a durable project-local skill and templates agents load on every session.

**Trigger**
`/create-repo-standards`, "bootstrap repo standards", or when a manifest project has no `standards-<name>` skill and agents keep guessing PR/issue shape.

**Do not use for**
- Drift pass on an existing standards skill → `maintain-repo-standards`
- Hub-only skill authoring in agent-bootstrap → `close-out` + black-box gate
- Running against a repo you are not allowed to write templates into

## Companions

| Skill | Role here |
| --- | --- |
| `maintain-repo-standards` | Trigger-only drift pass after generation |
| `create-verification-skill` | Optional input when `verify-<app>` already exists |
| `plan-code-review-workflow` | Planning section points here when appropriate |
| `pstack-principles` | encode-lessons-in-structure, prove-it-works, sequence-verifiable-units (cite by name only) |

**Verification**
- Interview artifacts named (paths or `gh` commands run)
- Generated `standards-<repo>/SKILL.md` loads; every section is concrete for **this** repo (no `TODO` / `TBD` / angle-bracket placeholders)
- One proof read: open the skill cold and confirm each section answers a real fact from the interview
- Self-check (step 5): no stray angle-bracket placeholders outside HTML comments in generated files

---

## 0. Read agent-bootstrap at a pinned SHA (when needed)

If the run must load hub docs or skills at a specific commit, use **one** of these (then confirm paths came from that full SHA in interview notes):

**(a) contents API or raw file** — `gh api repos/<owner>/<repo>/contents/<path>?ref=<full-40-char-sha>` (base64-decode `content` from the JSON as UTF-8 text), or `https://raw.githubusercontent.com/<owner>/<repo>/<full-sha>/<path>`.

**(b) Tarball** — `gh api repos/<owner>/<repo>/tarball/<full-sha>` (follow redirects; extract the `.tar.gz` to a temp dir) and read files from the extracted tree.

Do **not** use `git fetch` by bare SHA. Hub skills and docs live under `skills/<name>/` and `docs/` — not under `.cursor/skills/` on the hub repo. See `docs/shared/repo-standards-practice.md`.

---

## 1. Interview the repository (read-only first)

Gather facts from the checkout and GitHub (use `gh` when the repo is on GitHub). Do not ask the user what the codebase already states unless access is blocked.

| Source | What to extract |
| --- | --- |
| `.github/PULL_REQUEST_TEMPLATE.md`, `PULL_REQUEST_TEMPLATE/*` | Existing PR fields, checklists |
| `.github/ISSUE_TEMPLATE/*`, `ISSUE_TEMPLATE/*` | Issue types, required sections |
| `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.clinerules`, harness rules | Agent instructions and which harnesses are in use |
| `README.md`, CI config (`.github/workflows/*`, Makefile `ci`, etc.) | Required checks, lint/test commands, **exit code / pass bar** per required job and step |
| `manifest.yaml` (project or hub sibling) | Manifest `name` field when present |
| `pyproject.toml` `[project].name`, `package.json` `name`, `Cargo.toml` `package.name` | Package name when no manifest name |
| `skills/verify-*/`, `.cursor/skills/verify-*`, `.grok/skills/verify-*` | Verification skill name, doctor/drive commands, assertions (hub verify skills are under `skills/verify-<app>/` when cited from agent-bootstrap) |
| `gh label list` (or API) | Labels that exist — for issue forms |
| Recent merged PRs (`gh pr list --state merged -L 5`) | Real Tier/Models/Linear/Gates lines if used |
| Open issues sample | Acceptance-criteria habits |
| Language / layout | Primary stack, monorepo roots, package manager |

**No `AGENTS.md`:** Infer agent expectations from `README.md` (contributing, test commands), CI workflows, and any existing harness skill dirs (`.cursor/skills/`, `.claude/skills/`, `.grok/skills/`). Optionally add a one-line pointer in `README.md` to the generated `standards-<repo>` skill path — only when the README already has a contributing or agent section; do not invent a full `AGENTS.md` unless the user asks.

**Pass bar (CI):** For each required check, record the workflow file, job id, and the exact command or step that must succeed (exit `0`). When a job splits verification (for example env vars like `VERIFY_SKIP_FULL_PYTEST=1`, `SPOTLIGHT_ONLY=1`, or repo-specific spotlight/pytest gates), document each split and what still runs in CI versus what full local verify runs. The generated skill **Verification** section must state the same pass bar **step-for-step** as CI — not a looser summary.

Record interview notes in the run log (not committed) — cite paths and SHAs per **prove-it-works**.

## 2. Choose the standards skill id

**Default:** `standards-<repo>` where `<repo>` is the repository directory basename, lowercased with hyphens (for example checkout folder `packet` → `standards-packet`).

Override only with evidence, in this **order**:

1. `manifest.yaml` project `name` when the target is a manifest entry → `standards-<manifest-name>`
2. Else if `pyproject.toml` `[project].name` (or `package.json` / `Cargo.toml` name) **matches** the repo purpose and naming (same slug or documented product name) → `standards-<that-name>`
3. Else stay on the directory-basename default — do **not** use a mismatched PyPI/package name alone

When you deviate from the default basename rule, say so in the PR body **Summary** (one line: chosen id, source, why).

## 3. Generate the project-local skill

Write the **same** `SKILL.md` into **only** harness skill folders the project already uses (detect existing `.cursor/skills/`, `.claude/skills/`, `.grok/skills/`, or an on-disk path named in `AGENTS.md` / `.clinerules`). **Do not** create absent `.claude/`, `.grok/`, or Cline-only trees just to mirror the hub layout.

**Skip** any folder that already loads hub skills via symlinks (for example `.cursor/skills/write-tests` → agent-bootstrap `skills/write-tests`); record skipped paths in the handback — do not duplicate copies there.

| Harness | Typical path (only if already in use) |
| --- | --- |
| Cursor | `.cursor/skills/standards-<repo>/SKILL.md` |
| Claude Code | `.claude/skills/standards-<repo>/SKILL.md` |
| Grok | `.grok/skills/standards-<repo>/SKILL.md` |
| Cline / Roo | Path named in `.clinerules` or `AGENTS.md` |

YAML frontmatter (required on the generated project skill): `name: standards-<repo>`, `description:` one line naming the repo and when to load it, `version: 1.0.0` (bump on substantive template/skill edits).

Required sections (all concrete — **encode-lessons-in-structure**):

1. **PR format** — Copy the **Tier scale** table (T0–T3) verbatim from `docs/shared/repo-standards-practice.md` (or the hub pin you read at step 0). Install **`.github/PULL_REQUEST_TEMPLATE.md`** from the hub canonical doc body starting at `Tier:` (same header order: `Tier:`, `Models:`, `Linear:` (`https://linear.app/...` or `N/A` only), `Summary:`, `Gates:`, then **pstack (Poteto) principles cited**, then evidence/checklist) — not the H1 title in `docs/shared/hub-pull-request-template.md`:

```bash
mkdir -p .github
python3 /path/to/agent-bootstrap/scripts/hub_pull_request_template.py copy --out .github/PULL_REQUEST_TEMPLATE.md
python3 /path/to/agent-bootstrap/scripts/hub_pull_request_template.py check --file .github/PULL_REQUEST_TEMPLATE.md
```

Do not invent a second template shape in the standards skill prose.
2. **Issue format** — Problem; acceptance criteria; non-goals; verification plan. Note: issue forms must not reference labels the repo lacks (see step 4).
3. **Planning** — When to use `architect` vs `plan-code-review-workflow`; what a plan must contain (files, risks, named checks per **sequence-verifiable-units**).
4. **Implementation** — TDD order (`write-tests` — hub skill at `skills/write-tests/` when bootstrapped from agent-bootstrap); implementer **Pre-PR ub-mode dev flow** (run dryer, crapper, and mutator on new code before the PR via `bash scripts/ub_gates_container.sh`, no host installs; `crapper --threshold 10`, `dryer --threshold 0.8` after `rm -f .metrics/dry.edn`, mutator on changed lines); CI **`ub-gates`** on every `push` / `pull_request` calls `scripts/run_ub_gates_ci.sh`, which defaults to blocking (`UB_GATES_ADVISORY=0`). Advisory mode is only `scripts/run_ub_gates_report.sh` or `UB_GATES_ADVISORY=1`. Scope is changed functions (crapper) and changed lines (dryer, mutator). Test paths, `.pyi`, and `.d.ts` are out of scope. Debt in untouched old functions does not block. A mutator skip is `skipped_mutator` and fails. A 20-minute mutator timeout is reported and does not block. No waiver: fix blocking findings on changed code, or escalate to the CoS. The PR `Gates:` section reports the real results (`docs/shared/ub-mode-practice.md`, GMA-411); commit message style.
5. **Verification** — Pointer to `verify-<app>` if present. **Gates / thresholds:** Run dryer, crapper, and mutator through `bash scripts/ub_gates_container.sh` (`docker run --rm`, no host installs). A missing tool is `skipped_tools_missing` or `tool_error` and fails in blocking mode. Mirror `docs/shared/ub-mode-practice.md` (blocking by default). Cite real test files or workflow steps the pass bar depends on.

Mirror hub `docs/shared/ub-mode-practice.md` when the repo adopts ub-mode. State that ub-gates block by default. State that `run_ub_gates_report.sh` stays advisory.

## 4. Write GitHub templates and optional docs

| Artifact | Action |
| --- | --- |
| `.github/PULL_REQUEST_TEMPLATE.md` | Same `hub_pull_request_template.py copy` / `check` from `docs/shared/hub-pull-request-template.md` starting at `Tier:` (per-header HTML hints are in that body). After copy, run placeholder self-check (step 5) |
| `.github/ISSUE_TEMPLATE/config.yml` | Only keys GitHub honors: `blank_issues_enabled` and `contact_links`. Do **not** use ignored keys such as `issue_templates:` (list templates as files in the same directory instead) |
| `.github/ISSUE_TEMPLATE/` | One template per common issue type; **list repo labels first** — omit `labels:` when a label is missing. Add a `question` form **only** if the `question` label exists |
| `STANDARDS.md` or `CONTRIBUTING.md` section | Optional human-readable mirror; link to the skill path |
| Format-lint CI | Optional workflow for PR headers — only if the repo already uses similar lint |

**CI verify splits:** In the standards skill and/or `CONTRIBUTING.md`, document explicit env toggles the repo uses to split CI verify (for example `VERIFY_SKIP_FULL_PYTEST`, spotlight-only jobs, partial pytest markers). State what each mode skips, what still must pass, and the command a developer runs locally for the full bar.

Do not edit product source outside `.github/`, harness skill dirs, and optional `STANDARDS.md` / `CONTRIBUTING.md`.

## 5. Prove and self-check the generated artifacts (required)

Before handover:

1. Read `standards-<repo>/SKILL.md` from cold (as the next agent would).
2. Confirm every section names real commands, check names, labels, and paths from the interview — no `TODO`, `TBD`, or angle-bracket placeholders left in prose.
3. **Placeholder self-check** — on every generated file you wrote (`SKILL.md` copies, `.github/PULL_REQUEST_TEMPLATE.md`, issue templates, optional `STANDARDS.md` / `CONTRIBUTING.md` section):

```bash
# Strip HTML comments, then fail on angle-bracket placeholders like <repo> or <app>
perl -0777 -pe 's/<!--.*?-->//gs' path/to/file | rg '<[a-zA-Z][a-zA-Z0-9-]*>' && exit 1 || true
```

Run for each file; combined output must be **empty** (no matches). Fix and re-run until clean.

4. If any section is generic, fix it and re-read.

This proof is documentation completeness, not a full product test run (**prove-it-works** on the artifact).

## 6. Local pre-push (optional, honest label)

When the repo already documents a local check before `git push`, mirror it in the standards skill **Verification** or **Implementation** section. Label it **local pre-push (project / CI parity)** — do not claim it is copied from hub `AGENTS.md` unless that file in **this** repo actually contains the same block.

When documenting a scripted pre-push, require fail-fast shell:

```bash
set -euo pipefail
your-verify-command 2>&1 | tee /tmp/pre-push.log
```

(`pipefail` ensures a failing command inside a pipeline is not masked by `tee`.)

## 7. Offer maintenance

Point at `maintain-repo-standards` when CI, templates, or verify skills drift (trigger only — no scheduled routine).

## Provenance

Hub-authored skill modeled on `create-verification-skill` / `maintain-verification-skill` structure (not verify logic). PR/issue header lines align with `docs/shared/ub-mode-practice.md` and `docs/shared/repo-standards-practice.md`.

*Last updated: 2026-10-26 | Hub version: 0.14.0*
