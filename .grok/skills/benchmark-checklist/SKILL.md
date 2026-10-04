---
name: benchmark-checklist
description: Vet a performance number for limiter, tuning, errors, repeats, and end-to-end relevance before reporting or acting on it.
metadata:
  short-description: Refuse an unexplained performance number
---

# benchmark-checklist

Triggers on /benchmark-checklist or any speedup or regression claim.

## Quick Start

1. Read `references/source.md` before acting.
2. Write the claim sentence before the reported runs.
3. Answer the seven questions from a run, not from the code.
4. Lead with faster, slower, no measurable difference, or inconclusive.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
