---
name: agent-orchestration-roles
description: Use to orient a new harness or coordinate tasks when multiple agent harnesses (e.g. a planner/reviewer harness and an implementer harness) collaborate across the projects in this hub's manifest.yaml.
metadata:
  short-description: Multi-harness role division
---

# agent-orchestration-roles

Triggers when setting up or clarifying the division of labor between a planning/reviewing harness and an implementing harness.

## Quick Start

1. Read `references/source.md` for the full role split and workflow loop.
2. Resolve the coordination root directory from manifest.yaml, not a hardcoded path.
3. Keep the planner harness out of bulk implementation when an implementer harness is available.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
