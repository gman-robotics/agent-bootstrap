---
name: multi-harness-coordination
description: Use when coordinating work across two or more agent harnesses with separated planner/reviewer and implementer roles and an adversarial review loop.
metadata:
  short-description: Cross-harness coordination
---

# multi-harness-coordination

Triggers when routing tasks between harnesses, running the multi-harness workflow, or establishing planner vs implementer roles across agents.

## Quick Start

1. Read `references/source.md` before acting.
2. Step A: full-context plan, no production code. Step B: TDD on isolated branch.
3. Steps C/D: cumulative git diff review, max 3 iterations, then Step E PR if approved.
4. Optional: lead a handoff with the four-field envelope stanza (type/to/priority/task).

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
