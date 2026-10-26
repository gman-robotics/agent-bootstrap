---
name: create-repo-standards
description: "Interview a repository and generate a project-local standards-<repo> skill plus GitHub PR/issue templates so agents follow one PR format, issue format, planning rules, implementation workflow, and verification pointers. Use for /create-repo-standards on a manifest project. Do not run on agent-bootstrap hub-only Markdown unless explicitly asked."
version: 1.0.1
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
- Generated `standards-<repo>/SKILL.md` loads; every section is concrete for **this** repo (no `TODO` / `TBD` / `<placeholder>`)
- One proof read: open the skill cold and confirm each section answers a real fact from the interview

---

## 1. Interview the repository (read-only first)

Gather facts from the checkout and GitHub (use `gh` when the repo is on GitHub). Do not ask the user what the codebase already states unless access is blocked.

| Source | What to extract |
| --- | --- |
| `.github/PULL_REQUEST_TEMPLATE.md`, `PULL_REQUEST_TEMPLATE/*` | Existing PR fields, checklists |
| `.github/ISSUE_TEMPLATE/*`, `ISSUE_TEMPLATE/*` | Issue types, required sections |
| `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, harness rules | Agent instructions already in force |
| CI config (`.github/workflows/*`, Makefile `ci`, etc.) | Required checks, lint/test commands |
| `manifest.yaml` sibling or project `memory-bank/` | Project name, docs path, verify skill if any |
| `skills/verify-*/` or `.cursor/skills/verify-*` | Verification skill name, doctor/drive commands |
| Recent merged PRs (`gh pr list --state merged -L 5`) | Real Tier/Models/Gates lines if used |
| Open issues sample | Acceptance-criteria habits |
| Language / layout | Primary stack, monorepo roots, package manager |

Record interview notes in the run log (not committed) — cite paths and SHAs per **prove-it-works**.

## 2. Choose the standards skill id

Use `standards-<repo>` where `<repo>` is the manifest `name` field or the repository directory basename (lowercase, hyphens). Example: `standards-my-app`.

## 3. Generate the project-local skill

Write the **same** `SKILL.md` into each harness skill folder the project uses (create missing dirs). **Skip** any folder that already loads hub skills via symlinks into that harness path (for example `.cursor/skills/write-tests` → agent-bootstrap `skills/write-tests`); record skipped paths in the handback with a one-line reason — do not duplicate copies there.

| Harness | Typical path (project root) |
| --- | --- |
| Cursor | `.cursor/skills/standards-<repo>/SKILL.md` |
| Claude Code | `.claude/skills/standards-<repo>/SKILL.md` |
| Grok | `.grok/skills/standards-<repo>/SKILL.md` |
| Cline / Roo | On-disk path named in `.clinerules` or `AGENTS.md` (Cline does not load `.cursor/skills/`) |

YAML frontmatter: `name: standards-<repo>`, `description:` one line naming the repo and when to load it.

Required sections (all concrete — **encode-lessons-in-structure**):

1. **PR format** — In order: `Tier:`, `Models:`, `Linear:` (must be `https://linear.app/...` issue URL or `N/A` — never a Cursor store path, box path, or sketch link); `Summary:`; `Gates:` (crapper/dryer/mutator advisory results, `N/A (hub Markdown)`, or project verify command); then verification evidence (commands + exit codes) and checklist aligned with CI.
2. **Issue format** — Problem; acceptance criteria; non-goals; verification plan (how a reviewer knows it is done).
3. **Planning** — When to use `architect` vs `plan-code-review-workflow`; what a plan must contain (files, risks, named checks per **sequence-verifiable-units**).
4. **Implementation** — TDD order (`write-tests`); ub-mode Make it Right **advisory** gates when unclebob tools exist (GMA-411: `rm -f .metrics/dry.edn` before dryer); commit message style.
5. **Verification** — Pointer to `verify-<app>` if present; gate thresholds; required CI jobs by name; local command to run before push.

Mirror hub `docs/shared/ub-mode-practice.md` when the repo adopts ub-mode; state **advisory** unless the project explicitly enables blocking gates.

## 4. Write GitHub templates and optional docs

| Artifact | Action |
| --- | --- |
| `.github/PULL_REQUEST_TEMPLATE.md` | Match PR format section (include `Gates:` line) |
| `.github/ISSUE_TEMPLATE/` | One template per common issue type, or a single `config.yml` + templates |
| `STANDARDS.md` or `CONTRIBUTING.md` section | Optional human-readable mirror; link to the skill path |
| Format-lint CI | Optional workflow that fails when PR body misses required header lines — only if the repo already uses similar lint |

Do not edit product source outside `.github/`, harness skill dirs, and optional `STANDARDS.md` / `CONTRIBUTING.md`.

## 5. Prove the generated skill (required)

Before handover:

1. Read `standards-<repo>/SKILL.md` from cold (as the next agent would).
2. Confirm every section names real commands, check names, and paths from the interview — no placeholders.
3. If any section is generic, fix it and re-read.

This proof is documentation completeness, not a full product test run (**prove-it-works** on the artifact).

## 6. Offer maintenance

Point at `maintain-repo-standards` when CI, templates, or verify skills drift (trigger only — no scheduled routine).

## Provenance

Hub-authored skill modeled on `create-verification-skill` / `maintain-verification-skill` structure (not verify logic). PR/issue header lines align with `docs/shared/ub-mode-practice.md` and `docs/shared/repo-standards-practice.md`.

*Last updated: 2026-10-26 | Hub version: 0.14.0*
