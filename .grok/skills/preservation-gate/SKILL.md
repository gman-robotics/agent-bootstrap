---
name: preservation-gate
description: Use when writing a development-document markdown (Dt) from iteration 2 onward: every such document needs an exact '## Preservation Gate' heading listing the previous iteration's verified claims the Developer must not regress.
metadata:
  short-description: The Preservation Gate plan-document field
---

# preservation-gate

Triggers when writing or reviewing a Dt plan/development document for iteration 2 or later of a warm-started, evidence-driven workflow.

## Quick Start

1. Read `references/source.md` before acting; it is the authoritative field definition.
2. Use the exact literal heading `## Preservation Gate` with at least one bullet from the prior iteration's verified claims.
3. Distinct from REPEAT: Preservation Gate is positive and never closes; REPEAT is negative and closes only via a mechanical check.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
