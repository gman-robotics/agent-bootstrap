---
name: show-me-your-work
description: Use to keep an append-only TSV decision log for auditable agent work.
metadata:
  short-description: TSV decision audit trail
---

# show-me-your-work

Triggers when figure-it-out or ambitious work needs a decision trail.

## Quick Start

1. Read `references/source.md` before acting.
2. One row per decision point: ts, phase, decision, why, evidence, result.
3. Prefer script-produced evidence; commit trail for ambitious PRs.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
