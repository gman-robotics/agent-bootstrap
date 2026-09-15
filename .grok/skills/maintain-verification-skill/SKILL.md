---
name: maintain-verification-skill
description: Use to reconcile and live-pass a verify-<app> skill against product drift.
metadata:
  short-description: Maintain verify-<app> skills
---

# maintain-verification-skill

Triggers when a verification skill needs hygiene, reconciliation, or live pass.

## Quick Start

1. Read `references/source.md` before acting.
2. Index hygiene; readonly source wave per feature; reconcile recipes.
3. Coordinator live-pass every feature; triage doc vs harness vs product gaps.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
