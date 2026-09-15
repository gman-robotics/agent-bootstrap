---
name: interrogate
description: Use for multi-model adversarial review: parallel reviewers, synthesized verdict, no auto-apply.
metadata:
  short-description: Multi-model adversarial review
---

# interrogate

Triggers on interrogate, adversarial review, stress test this code, or find blind spots.

## Quick Start

1. Read `references/source.md` before acting.
2. State intent; spawn parallel readonly reviewers with shared rubric.
3. Companion: expert-pr-review for open PRs with threads/CI/posting gates.
4. Synthesize Act On / Consider / Noted / Dismissed; do not auto-apply fixes.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
