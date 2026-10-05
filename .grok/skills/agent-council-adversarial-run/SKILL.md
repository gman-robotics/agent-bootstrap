---
name: agent-council-adversarial-run
description: Run a council adversarial job with a 30 minute implement floor and worktree recovery.
metadata:
  short-description: Council adversarial run and recovery
---

# agent-council-adversarial-run

Triggers on run adversarial or recover an implement timeout.

## Quick Start

1. Read `references/source.md` before acting.
2. One repo per payload.
3. Keep the worktree on error.
4. Do not call an open PR shipped.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
