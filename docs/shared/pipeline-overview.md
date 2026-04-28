# Shared Pipeline Overview

> **Scope**: Team-wide CI/CD, build, and release standards that apply across all projects.  
> For project-specific pipeline details, see `docs/projects/<name>/pipeline-overview.md`.

---

## Standard Development Workflow

```
feature branch → PR → CI checks → code review → squash merge → main → deploy (dev) → release branch → deploy (prod)
```

All projects SHOULD follow this branching and delivery model unless documented otherwise in their project docs.

---

## Branch Strategy

| Branch | Purpose | Protection |
|---|---|---|
| `main` | Production-ready code. Always deployable. | Required PR + review + CI pass |
| `releases/<date>` | Release candidates. Hotfixes via cherry-pick. | Required PR + review |
| `feat/<name>` | Feature branches. Short-lived. | None (auto-delete after merge) |
| `fix/<name>` | Bug fix branches. | None |
| `chore/<name>` | Tooling, deps, non-functional changes. | None |

---

## CI/CD Standards

### Required CI Checks (all projects)

Every PR must pass:
- [ ] **Lint** — code style enforced (ESLint, Prettier, or project equivalent)
- [ ] **Type check** — TypeScript / static analysis where applicable
- [ ] **Unit tests** — all unit tests pass, minimum 80% coverage on changed files
- [ ] **Build** — project builds without errors
- [ ] **Security scan** — dependency vulnerability check (e.g., `npm audit`, Snyk, Dependabot)

### Optional / Project-Specific Checks

Document in `docs/projects/<name>/pipeline-overview.md`:
- Integration tests
- E2E tests
- Performance benchmarks
- Container builds

---

## Release Process (Standard)

See `skills/cherry-pick-to-release-branch.md` for the full automated playbook.

High-level flow:
1. Cut release branch: `releases/YYYY.MM.DD`
2. Cherry-pick merged PRs targeting the release
3. Bump RC version, push, run CI
4. QA on staging → promote to production
5. Tag and create GitHub Release

---

## Deployment Environments

| Environment | Branch | Purpose |
|---|---|---|
| `dev` / `preview` | `main` (auto-deploy on merge) | Latest integrated code for internal testing |
| `staging` | `releases/*` | Pre-release QA and UAT |
| `production` | `releases/*` (after sign-off) | Customer-facing |

---

## Secret & Config Management

- **Never** commit secrets to source control (enforced by `.gitignore` + secret scanning).
- Use environment variables for all config that varies by environment.
- Store secrets in the project's designated secret manager (document in project pipeline docs).
- Rotate secrets at least annually or immediately on suspected exposure.

---

## Dependency Updates

- Review and update dependencies monthly (or via automated PRs from Dependabot/Renovate).
- Security patches: apply and release within 48 hours of critical CVE disclosure.
- Major version upgrades: treat as a feature branch, plan carefully, document in project `decisions.md`.

---

## Monitoring & Alerting Baseline

Every production service SHOULD have:
- [ ] Error rate alerting (alert on spike above baseline)
- [ ] Latency alerting (p95 above SLA threshold)
- [ ] Uptime monitoring (external ping every 1 min)
- [ ] Log aggregation (document tool in project pipeline docs)

---

*Last updated: 2026-04-28 | Update when team-wide CI/CD standards change*
