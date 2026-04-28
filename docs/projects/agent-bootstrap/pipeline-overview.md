# Pipeline Overview: agent-bootstrap

> This project is a **documentation-only hub** (Markdown + YAML). There is no build system, compiled output, or deployed service.  
> This file documents the contribution and quality processes used to maintain this repo.

---

## Development Workflow

```
personal branch → plan (PLAN mode) → implement (ACT mode) → self-review → PR → expert-pr-review → squash merge → main
```

All changes follow the `plan-code-review` workflow — even for this documentation repo.

---

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Current stable version of the hub. Always usable. |
| `feat/<name>` | New skills, agents, or features |
| `fix/<name>` | Corrections to existing content |
| `chore/<name>` | Housekeeping (manifest updates, memory-bank sync) |

No release branches — this hub does not have runtime versions.  
Version is tracked in `manifest.yaml` (`version: 0.1.0`) and file footers.

---

## Quality Checks

Since this repo is pure Markdown/YAML (no compilation), "CI" is lightweight:

### Pre-PR Checklist (manual — run before opening PR)
- [ ] All new files follow kebab-case naming convention
- [ ] Absolute paths updated to your local machine in `manifest.yaml` (not committed as machine-specific paths)
- [ ] No sensitive data (tokens, credentials, personal paths) in any committed file
- [ ] AGENTS.md references updated if a new skill or agent was added
- [ ] Memory-bank files updated (`activeContext.md`, `progress.md`)
- [ ] Self-review using the expert-pr-review checklist (at minimum, correctness + style)

### Automated (if configured)
- Markdown lint (optional — see `.markdownlint.json` if present)
- Secret scanning (GitHub Advanced Security if enabled)
- CODEOWNERS review requirement (see `.github/CODEOWNERS`)

---

## Contribution Process

1. **Plan** — open a discussion or start in PLAN mode with your agent harness
2. **Branch** — create a `feat/` or `fix/` branch
3. **Implement** — follow the plan-code-review workflow
4. **Self-review** — use the expert-pr-review skill before opening PR
5. **PR** — open PR against `main`, use the PR template
6. **Review** — at least one team member reviews with expert-pr-review skill
7. **Merge** — squash + merge after approval

---

## Versioning

This hub uses a simple version string (not semver):
- Location: `manifest.yaml` → `version: X.Y.Z` and file footers
- Bump `Y` for new skills, agents, or structural additions
- Bump `Z` for corrections and content updates
- Bump `X` for major restructuring (rare)

---

## Maintenance Tasks

| Task | Frequency | Owner |
|---|---|---|
| Update memory-bank after significant changes | Per task | Any contributor |
| Review and update skills for relevance | Monthly | Maintainer |
| Update ONBOARDING.md for new team members | On process change | Maintainer |
| Sync absolute paths in manifest.yaml | On repo relocation | Individual user |
| Review CONTRIBUTING.md for accuracy | Quarterly | Maintainer |

---

## No Deployment

This repo has no deployment pipeline. "Shipping" means:
1. Merge to `main`
2. Each team member pulls the latest version
3. Update their harness configuration (e.g., re-paste `AGENTS.md` content if needed)

---

*Last updated: 2026-04-28 | Update when contribution or quality processes change*
