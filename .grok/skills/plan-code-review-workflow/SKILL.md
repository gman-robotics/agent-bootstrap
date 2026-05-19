---
name: plan-code-review-workflow
description: Use when work is non-trivial and should follow the team workflow of planning with the user, implementing cleanly, critically reviewing, and iterating before finalizing.
metadata:
  short-description: Plan, code, review workflow
---

# plan-code-review-workflow

Triggers on requests to follow the main team workflow, co-create a plan for substantial work, or run a full plan-to-review delivery loop.

## Quick Start

1. Read `references/source.md` before acting; it is the authoritative workflow.
2. Run the phases in order: PLAN, CODE, REVIEW, ITERATE, FINALIZE.
3. Preserve all user-approval gates before posting reviews, committing, or pushing.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
