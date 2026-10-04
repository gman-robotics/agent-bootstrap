---
name: correct
description: Find repeated agent mistake classes and make each one impossible at architecture, types, lint, then tests, with docs last.
metadata:
  short-description: Structural fix for repeated agent mistakes
---

# correct

Triggers on /correct or the second correction of the same mistake class.

## Quick Start

1. Read `references/source.md` before acting.
2. Group evidence into classes that happened twice.
3. Fix at the highest level that works and prove the check fails on a past mistake.
4. Update the rule table in AGENTS.md or docs/shared/constitution.md.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
