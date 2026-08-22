---
name: codebase-simplification-audit
description: Use when the user wants a whole-repo read-only audit for simpler data structures, state representation, control flow, algorithms, or ownership. Do not edit, test, implement, commit, or push until they accept a recommendation.
metadata:
  short-description: Read-only whole-repo representation audit
---

# codebase-simplification-audit

Triggers on codebase simplification audit, messy state/ownership reviews, or a paste of the Aaron Francis audit-your-codebase gist.

## Quick Start

1. Read `references/source.md` before acting; it is the authoritative workflow.
2. Hard rule: no file edits, tests, implement skills, commits, or pushes until the user accepts a rec.
3. Inventory every subsystem, bound workers to ≤2 material recs or skip, verify, audit the audit, then stop.
4. Ownership rows may use the Architectural Review Phases checklist names (no CRAP/mutation/DRY tooling).

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
