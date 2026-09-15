---
name: swarm
description: Use to fan out N parallel workers (partition, race, or mix) and return one consolidated report.
metadata:
  short-description: Parallel worker swarm report
---

# swarm

Triggers on swarm this, parallel coverage, races, gauntlets, or exploration.

## Quick Start

1. Read `references/source.md` before acting.
2. Frame done predicate and race rule; spawn cloud workers with isolated outputs.
3. Aggregate compact table; return PASS/ISSUES/BLOCKED evidence per worker.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
