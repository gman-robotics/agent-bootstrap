---
name: subagent-routing
description: Use before starting any task with independent subtasks, parallelizable work, or when deciding which Claude model to assign to a spawned agent.
metadata:
  short-description: Subagent use and model selection
---

# subagent-routing

Triggers when deciding whether to delegate work to a subagent or run it inline, and when selecting Haiku vs Sonnet for a spawned agent.

## Quick Start

1. Read `references/source.md` before delegating any subtask.
2. Use Haiku for reads, searches, formatting, and summarisation; use Sonnet for code, analysis, and judgment.
3. Emit all independent Agent calls in one response to run them in parallel.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
