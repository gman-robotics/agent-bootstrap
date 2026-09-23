# NOTICE

Vendored from: https://github.com/cloudflare/security-audit-skill
Pinned commit:  c1c8a8c1471069fb0e188eeaff69b8e8db6564a8
Commit date:    2026-09-14T19:28:54Z
Vendored on:    2026-09-23
License:        MIT (Copyright (c) 2025-2026 Cloudflare, Inc.) — see ./LICENSE in this directory

## What this directory contains

The entire upstream `skills/security-audit/` tree at the pinned commit, vendored verbatim
byte-for-byte: `SKILL.md` (upstream's own hub-entry frontmatter — **never** used as this
hub's `security-audit` hub entry, see `skills/security-audit/SKILL.md` in the parent
directory for that), 13 domain-attack-class packs, `report-schema.json`, `README.md`, and
the two validator pairs (`validate-findings.cjs` + `.test.cjs`,
`validate-coverage-ledger.cjs` + `.test.cjs`).

## Staleness note (house gap, documented not papered over)

`scripts/check_skill_live.py`'s staleness hash (`skill_sha256`) covers only
`skills/security-audit/SKILL.md` — the house-authored hub entry. It does **not** cover any
file under this `references/cloudflare/` directory. A future edit to the vendored `.cjs`
files, domain packs, or this NOTICE does **not** by itself invalidate
`skills/security-audit/black-box-run.json`. The `cjs-tests-pass` fixture
(`skills/security-audit/fixtures/cjs-tests-pass/`, backed by
`tests/test_security_audit_vendor_cjs.py`) must be re-run manually whenever content under
this directory changes, not only when the hub `SKILL.md` changes.

## House compliance

Vendored under `docs/shared/constitution.md` Article 5's compliant path (a real upstream
MIT LICENSE, not the "no LICENSE, ideas-only" exception case Article 5's own worked example
covers) — see `docs/projects/agent-bootstrap/gma-56-security-audit-vendor-plan.md` §3 for
the full rationale and the live verification this pin was checked against.
