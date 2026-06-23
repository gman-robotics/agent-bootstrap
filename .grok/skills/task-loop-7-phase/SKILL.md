---
name: task-loop-7-phase
description: Use when a task should follow the strict 7-Phase Algorithm: OBSERVE, THINK, PLAN, BUILD, EXECUTE, VERIFY, LEARN, with TaskLoopState updates in mem0 and durable lessons captured at the end.
metadata:
  short-description: Seven-phase task loop
---

# task-loop-7-phase

Triggers when the user invokes the 7-Phase Algorithm, TaskLoopState, or an observe-think-plan-build-execute-verify-learn workflow.

## Quick Start

1. Read `references/source.md` before starting the loop.
2. Run phases strictly in order and announce each phase transition.
3. Update TaskLoopState in mem0 after each phase, then write a lesson in LEARN.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
