---
name: maintain-repo-standards
description: "Periodic drift pass for a project-local standards-<repo> skill and GitHub templates. At most one PR per run; only standards paths and templates; never product code. Outcome clean, changed, or blocked."
version: 1.0.0
---

# maintain-repo-standards

**Purpose**
Keep `standards-<repo>` and PR/issue templates aligned with how the repository actually works — CI renames, new verify skills, ub-mode adoption, template drift.

**Trigger**
`/maintain-repo-standards`, "audit repo standards", or scheduled upkeep after `create-repo-standards`.

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

---

## Outcomes

| Outcome | Meaning |
| --- | --- |
| **clean** | Templates and skill match repo facts; nothing worth shipping |
| **changed** | One PR updates standards skill copies and/or templates with proven corrections |
| **blocked** | Could not verify facts (no CI access, conflicting templates) — state what blocked |

## Edit scope (hard)

**In scope:** `standards-<repo>/` under harness skill folders (`.cursor/skills`, `.claude/skills`, `.grok/skills`, etc.), `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/*`, optional `STANDARDS.md` / `CONTRIBUTING.md` standards section, optional format-lint workflow for PR headers.

**Out of scope:** application source, tests, dependencies, hub `skills/` in agent-bootstrap unless this run *is* agent-bootstrap maintenance explicitly requested.

Product regressions or broken workflows discovered during the pass → record in the handback; **do not** fix them in the standards PR.

## Pass

0. **Locate target.** Find `standards-<repo>/SKILL.md` in the project harness paths. None → stop; use `create-repo-standards`.

1. **Re-interview deltas.** Compare skill + templates against current CI workflows, required checks, `AGENTS.md`, recent merged PRs, and `verify-*` / ub-mode mentions. List drift with file:line or workflow name.

2. **Reconcile.** Update all harness copies of the skill to stay identical. Update templates to match the skill PR/issue sections.

3. **Prove read.** Re-read the skill cold; every section still concrete (**prove-it-works**).

4. **Ship or stop.**
   - **clean** / **blocked** — no PR; report outcome.
   - **changed** — one PR, standards + templates only; PR body uses the repo's own header lines including **`Gates:`**.

Keep run notes in scratch space; do not commit interview logs.

## Provenance

Hub-authored skill modeled on `maintain-verification-skill` structure (not verify logic).

*Last updated: 2026-10-26 | Hub version: 0.14.0*
