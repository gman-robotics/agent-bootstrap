---
name: subagent-routing
description: Use before any task with independent subtasks to decide what to delegate and which model tier each subagent should use.
metadata:
  short-description: Subagent and model routing
---

# subagent-routing

Triggers before tasks with parallelizable or isolatable subtasks, or when selecting a model for a spawned agent.

## Quick Start

1. Read `references/source.md` for the decomposition checklist and model table.
2. Use the cheap tier for retrieval tasks and the full tier for code and judgment.
3. Editing agents must run in worktree isolation when the checkout may be shared.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
