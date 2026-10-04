---
name: shared-memory-coordination
description: Share the active to-do list and completed-task log across harnesses on a Mem0 day bus.
metadata:
  short-description: Cross-harness Mem0 task bus
---

# shared-memory-coordination

Triggers on session start, task state change, or end-of-day reconciliation.

## Quick Start

1. Read `references/source.md` before acting.
2. Use the project coordination user, not a hard-coded person.
3. Publish the todo JSON and completed log on the day bus.
4. Reconcile at end of day into the hub standup log.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
