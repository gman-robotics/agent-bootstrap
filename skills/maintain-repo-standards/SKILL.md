---
name: maintain-repo-standards
description: "Trigger-only drift pass for a project-local standards-<repo> skill and GitHub templates. At most one PR per run; only standards paths and templates; never product code. Outcome clean, changed, or blocked."
version: 1.0.3
---

# maintain-repo-standards

**Purpose**
Keep `standards-<repo>` and PR/issue templates aligned with how the repository actually works — CI renames, new verify skills, ub-mode adoption, template drift.

**Trigger**
`/maintain-repo-standards`, "audit repo standards", or after `create-repo-standards` when the user or workflow explicitly asks for a drift pass. **No scheduled routine** — this skill runs on a trigger only.

**Do not use for**
- No standards skill yet → `create-repo-standards`
- Product bug fixes → report separately; do not patch product code in this pass

## Companions

| Skill | Role here |
| --- | --- |
| `create-repo-standards` | Generator for the skill under maintenance |
| `maintain-verification-skill` | Parallel pattern; verify skill drift is input, not edited here unless templates reference wrong names |
| `pstack-principles` | prove-it-works, encode-lessons-in-structure, sequence-verifiable-units (cite by name only) |

**Verification**
- Outcome declared: **clean** | **changed** | **blocked**
- Edit scope respected (standards skill dirs + `.github` templates + optional STANDARDS/CONTRIBUTING only)
- At most one PR opened when outcome is **changed**
- Drift checklist (step 1) executed; placeholder self-check clean when outcome is **changed**

---

## Outcomes

| Outcome | Meaning |
| --- | --- |
| **clean** | Templates and skill match repo facts; nothing worth shipping |
| **changed** | One PR updates standards skill copies and/or templates with proven corrections |
| **blocked** | Could not verify facts (no CI access, conflicting templates) — state what blocked |

## Edit scope (hard)

**In scope:** `standards-<repo>/` under harness skill folders (`.cursor/skills`, `.claude/skills`, `.grok/skills`, etc.), `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/*`, optional `STANDARDS.md` / `CONTRIBUTING.md` standards section, optional format-lint workflow for PR headers.

**Out of scope:** application source, tests, dependencies, hub `skills/` in agent-bootstrap unless this run *is* agent-bootstrap maintenance explicitly requested. When citing hub skills from agent-bootstrap, use `skills/<name>/` paths — not `.cursor/skills/` on the hub.

Product regressions or broken workflows discovered during the pass → record in the handback; **do not** fix them in the standards PR.

## Pass

0. **Locate target.** Find `standards-<repo>/SKILL.md` in the project harness paths. None → stop; use `create-repo-standards`.

1. **Re-interview deltas.** Compare skill + templates against current CI workflows, required checks, `AGENTS.md` (or README-inferred agent habits when `AGENTS.md` is absent), recent merged PRs, and `verify-*` / ub-mode mentions. List drift with file:line or workflow name.

   **Pass bar (CI)** — same reconcile detail as `create-repo-standards` step 1: for each required check, confirm the standards skill names the workflow file, job id, and exact step/command that must exit `0`. When CI splits verify (`VERIFY_SKIP_FULL_PYTEST`, spotlight-only env vars, partial pytest jobs), the skill must document each split and match CI step-for-step — not a looser summary.

   **Drift checklist** (mark each item pass/fail in run notes; any fail → candidate **changed** when fixable in scope):

   | Check | Pass when |
   | --- | --- |
   | Angle-bracket placeholders | No `<word>` placeholders remain in skill or template prose (allowed only inside HTML comments — see self-check) |
   | Tier table T0–T3 | Present in the standards skill **PR format** section and matches hub `docs/shared/repo-standards-practice.md` (or pinned hub SHA) |
   | Pass bar vs CI | Every required CI job/step named in the skill matches live workflow YAML (commands, exit codes, env splits) |
   | Test-file cites | Paths to test files or workflow steps cited in the pass bar still exist |
   | PR template | `hub_pull_request_template.py check` passes against `docs/shared/hub-pull-request-template.md` body from `Tier:` (same `copy`/`check` as `create-repo-standards`), including per-header HTML hints and **pstack (Poteto) principles cited** section |
   | PR header order | Template and skill agree on order: Tier → Models → Linear → Summary → Gates → Poteto section → evidence |
   | Issue `config.yml` | Only `blank_issues_enabled` and `contact_links` — no ignored keys like `issue_templates:` |
   | Question template | No `question` issue form unless the `question` label exists |
   | Skill id | `standards-<repo>` id still matches create rules (basename default; manifest/pyproject only when justified) |

   PR template install/verify (same as `create-repo-standards`):

```bash
mkdir -p .github
python3 /path/to/agent-bootstrap/scripts/hub_pull_request_template.py copy --out .github/PULL_REQUEST_TEMPLATE.md
python3 /path/to/agent-bootstrap/scripts/hub_pull_request_template.py check --file .github/PULL_REQUEST_TEMPLATE.md
```

2. **Format-lint vs templates (advisory).** If the repo has a PR-body format-lint workflow or script, compare its required fields to `.github/PULL_REQUEST_TEMPLATE.md` and the standards skill PR section. Report mismatches in the handback. When fields disagree, treat as drift: outcome **changed** when you can fix templates/skill text in scope, or **blocked** when CI rules are unclear or out of scope. The format check itself stays **advisory** — it does not block APPROVE on the standards PR.

3. **Reconcile.** Update all harness copies of the skill to stay identical. Update templates to match the skill PR/issue sections. Bump generated project skill `version:` in frontmatter when substance changes.

4. **Prove read and self-check.** Re-read the skill cold; every section still concrete (**prove-it-works**). When outcome is **changed**, run the placeholder self-check from `create-repo-standards` step 5 on every file you touched (strip HTML comments, then `rg '<[a-zA-Z][a-zA-Z0-9-]*>'` — must be empty).

5. **Ship or stop.**
   - **clean** / **blocked** — no PR; report outcome.
   - **changed** — one PR, standards + templates only; PR body uses the repo's header order (`Tier:`, `Models:`, `Linear:` must be `https://linear.app/...` or `N/A` — never a store or box path, `Summary:`, `Gates:`, then evidence).

Keep run notes in scratch space; do not commit interview logs.

## Local pre-push (optional, honest label)

When updating the standards skill, preserve or add a **local pre-push (project / CI parity)** subsection only when this repo already documents that habit — do not attribute it to hub `AGENTS.md` unless this repo's `AGENTS.md` contains the same steps. Scripted blocks must use `set -euo pipefail` and `tee` as in `create-repo-standards` step 6.

## Provenance

Hub-authored skill modeled on `maintain-verification-skill` structure (not verify logic).

*Last updated: 2026-10-26 | Hub version: 0.14.0*
