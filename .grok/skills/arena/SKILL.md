---
name: arena
description: Use to spawn N parallel candidates at the same task, pick a base, graft the strongest parts of losers, and verify the synthesized artifact.
metadata:
  short-description: Parallel candidates, pick and graft
---

# arena

Triggers on arena this, throw it in the arena, or when one attempt would lock in the wrong shape.

## Quick Start

1. Read `references/source.md` before acting.
2. Frame artifact + rubric + isolated output paths per candidate.
3. Fan out parallel subagents, cross-judge, pick base, graft best ideas, verify.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
