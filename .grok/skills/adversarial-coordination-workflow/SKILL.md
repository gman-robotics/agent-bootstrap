---
name: adversarial-coordination-workflow
description: Use when an Orchestrator (human or automated) needs to run a planner harness and an implementer harness as adversarial peers through a plan → implement → adversarial-review → PR loop.
metadata:
  short-description: Adversarial plan/implement/review loop
---

# adversarial-coordination-workflow

Triggers when starting multi-agent implementation work that requires a critical, adversarial review pass before any PR is created.

## Quick Start

1. Read `references/source.md` for the full Step A–E loop.
2. Step A: full-context plan, no production code. Step B: TDD on isolated branch.
3. Steps C/D: cumulative `git diff main...HEAD` review, max 3 iterations, then Step E PR if approved.
4. Optional: lead a handoff with the four-field envelope stanza (type/to/priority/task).

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
