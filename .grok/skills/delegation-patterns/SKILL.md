---
name: delegation-patterns
description: Use when planning how to delegate work across subagents in Claude Code, selecting the right model for a spawned agent, or deciding between parallel and sequential execution patterns.
metadata:
  short-description: Multi-agent delegation patterns
---

# delegation-patterns

Triggers when decomposing a task into parallel subtasks, selecting a model tier for a spawned agent, or designing a two-tier delegation flow.

## Quick Start

1. Read `references/source.md` before designing a delegation flow.
2. Classify each subtask as Tier 1 (Haiku, simple retrieval) or Tier 2 (Sonnet, analysis/code).
3. Emit all independent Task() calls in a single message so they run concurrently.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
