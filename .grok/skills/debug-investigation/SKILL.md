---
name: debug-investigation
description: Use for bug reports, flaky tests, or unexplained regressions that need systematic reproduction, isolation, a failing test, and a verified fix.
metadata:
  short-description: Systematic debugging workflow
---

# debug-investigation

Triggers on requests to diagnose a bug, investigate flaky behavior, or root-cause an incident before fixing it.

## Quick Start

1. Read `references/source.md` before attempting a fix.
2. Do not fix anything until you can reproduce it reliably.
3. Write a failing test that captures the reproduction before changing production code.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
