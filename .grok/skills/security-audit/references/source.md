---
name: security-audit
description: "Use only for the literal request 'security audit', 'run the Cloudflare security audit', or an explicit full/comprehensive/end-to-end/pen-test request against a codebase. Do NOT use for generic 'security review', 'review this PR', 'what could this break', or unscoped find-vulnerabilities requests — those are `expert-pr-review` / `blast-radius`. Opt-in only: never auto-invoked by plan-code-review-workflow, expert-pr-review's SecurityReviewer spawn, or any always-on pipeline."
version: 1.0.0
---

# security-audit

**Purpose**
Guidance-by-default security methodology and, only on an explicit full-audit/pen-test ask, the vendored Cloudflare six-phase full-audit workflow — with a mandatory capability check against four named execution-safety controls before any target-controlled execution.

**Trigger** (allowlist only)
- The literal phrase "security audit" or "security-audit"
- "run the Cloudflare security audit"
- An explicit full, comprehensive, end-to-end, or pen-test request against a codebase, API, service, CLI tool, library, or daemon

**Do not use for** (denylist — these route elsewhere)
- "security review" (unscoped, no full-audit ask) → `expert-pr-review` (PR-scoped) or `blast-radius` (diff-scoped)
- "review this PR" → `expert-pr-review`
- "what could this break" → `blast-radius`
- Generic, unscoped find-vulnerabilities requests with no explicit full-audit/pen-test ask → `expert-pr-review` for an open PR, `blast-radius` for a diff you don't trust yet
- This skill is **opt-in only**. It is never auto-invoked by `plan-code-review-workflow`, `expert-pr-review`'s Step 4 `SecurityReviewer` spawn, or any other always-on pipeline in this hub — loading it always requires an explicit request matching the allowlist above.

## Companions

| Skill | Role here |
|---|---|
| `expert-pr-review` | The PR-scoped review workflow for an open GitHub PR with threads/CI/posting gates — use that, not this, unless the user explicitly asked for a full security audit |
| `blast-radius` | The diff-scoped "what could this break" workflow — use that, not this, for a small change you don't trust yet |

Neither companion is a substitute for this skill's full-audit mode, and this skill is not a substitute for either of them: `expert-pr-review`'s Step 3 checkout+build/test validates the PR branch in a normal dev environment and does not provide the four Universal execution-safety controls below; `blast-radius` proves one safety fact about a diff, it does not run a six-phase audit.

---

## Operating modes (guidance is the default — read this before doing anything else)

This skill is **guidance by default**, mirroring the vendored upstream's own framing (see
`references/cloudflare/SKILL.md` "Operating modes"). Loading this `SKILL.md` — including
being triggered by the allowlist above — does **not** by itself authorize the complete
six-phase audit workflow, creating an output directory, or writing audit artifacts.

- **Guidance mode (default)**: security questions, methodology, triage, or investigating a
  specific already-known finding. Use only the relevant reference material
  (`references/cloudflare/*.md`) for the question at hand. Do not run all six phases, create
  an output directory, or write audit artifacts.
- **Full audit mode**: only after an explicit full-audit/pen-test/comprehensive-review/
  report-artifact ask matching the Trigger allowlist above, **and** the capability check
  below passes. If the request could mean either mode, ask one focused question before
  creating files or starting the six-phase workflow.

## Universal execution safety — the four controls (name them, do not skip this)

Before Full audit mode executes **any** target-controlled build, test, process, browser,
emulator, or fuzzer, explicitly check the environment against these four named controls —
read verbatim from `references/cloudflare/SKILL.md` "Universal execution safety", the
authoritative detail lives there, this is the house pointer, not a re-derivation:

1. **No external network** — an isolated loopback namespace only, when local client/server
   traffic is needed.
2. **Empty, explicitly allowlisted environment** — safe values only, scratch-local `HOME`,
   temporary directories, and caches.
3. **Read-only target and toolchain, writes confined to `scratch/`** — the target-controlled
   process may write only inside its own assigned `scratch/` directory.
4. **Explicit resource limits** — low CPU, memory, process count, file size, disk, and
   wall-clock limits, all explicit.

**If any one of the four cannot be confirmed, the result stays `needs_validation`** —
upstream's own verdict vocabulary (`confirmed` / `needs_validation` / `rejected`). Do not
invent a different fallback. Report the missing sandbox capability as a needs-validation
blocker and give a safe validation plan instead of executing target code.

### Three things this is not (do not conflate any of these)

- **The harness's own agent sandbox** (Cursor/Claude/Grok's general tool-execution
  isolation) is not the same as, and does not by itself satisfy, the four controls above.
  Those four controls are about the *target-controlled process under audit* — no network,
  allowlisted env, scratch-only writes, resource limits — not about the harness's own
  general tool-call safety.
- **`expert-pr-review`'s Step 3 checkout+build/test** validates the actual PR branch in the
  normal development environment. It is not isolated from the network, does not run in an
  allowlisted environment, is not scratch-write-only, and has no explicit resource limits.
  Running that build/test does not satisfy this capability check.
- **A bare assertion of "we have a sandbox"** is never itself a pass. Check against each of
  the four named controls specifically — a general claim is not a verified capability check.

## Full audit output location (SHOULD_FIX — inherits, does not weaken, upstream's default)

Upstream's own full-audit default output directory is `~/security-audit-skill/<repo-name>/run-<N>` —
**outside** the target repository by default (see `references/cloudflare/SKILL.md` "Full audit
setup"). This house wrapper restates that default rather than weakening it: use an in-repo
output directory only when the user explicitly selects one, and only after confirming it is
`.gitignore`d before any write.

## Installation

This skill is installed by normal hub discovery only: clone this repo, read `AGENTS.md` +
`skills/INDEX.md`, and this `SKILL.md` is available like every other hub skill. **Never**
install it via upstream's own `npx skills add https://github.com/cloudflare/security-audit-skill ...`
solo/global installation path — that is not how a hub user gets this skill.

## Provenance

Vendored from [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill)
(MIT, Copyright (c) 2025-2026 Cloudflare, Inc.) at pinned commit
`c1c8a8c1471069fb0e188eeaff69b8e8db6564a8` (2026-09-14T19:28:54Z). Full attribution trail —
license text, house NOTICE with URL/SHA/date, and the vendored upstream tree (its own
`SKILL.md` included as a companion reference, never as this hub's entry) — lives under
`references/cloudflare/`. See
`docs/projects/agent-bootstrap/gma-56-security-audit-vendor-plan.md` for the full vendor
plan this skill implements (GMA-56).

This house-authored `SKILL.md` is the hub entry. The vendored upstream `SKILL.md` at
`references/cloudflare/SKILL.md` is a companion reference only — it is never linked from
`skills/INDEX.md`, `AGENTS.md`, the exporter's `SkillConfig`, or any rule file as if it were
the hub entry, because its own frontmatter has no `version:` field and its `description:`
auto-matches broad phrases ("security questions", "focused reviews") that this hub's
`expert-pr-review` and `blast-radius` already own.

**Verification**
- `python3 scripts/validate_security_audit_vendor.py security-audit` exits `0`
- `python3 -m unittest tests.test_security_audit_vendor_cjs` exits `0` (execs `node --test`
  against both vendored `.test.cjs` files; a missing or too-old Node fails this test, it is
  never skipped)
- `python3 scripts/check_skill_live.py security-audit` exits `0`
- Note: `check_skill_live.py`'s staleness hash covers only this `SKILL.md`. A future edit to
  `references/cloudflare/*` does not by itself invalidate `black-box-run.json` — re-run the
  `cjs-tests-pass` fixture manually whenever vendored content changes (see
  `references/cloudflare/NOTICE.md` "Staleness note").

---

*Last updated: 2026-09-23 | Vendored opt-in from cloudflare/security-audit-skill (MIT) — GMA-56*
