---
name: blast-radius
description: Use to find what a change could break beyond the diff and prove the one safety fact by running real code, not just writing it up.
metadata:
  short-description: Cross-cutting breakage and proof
---

# blast-radius

Triggers on blast radius of X, what could this break, or reviewing a small diff you do not trust.

## Quick Start

1. Read `references/source.md` before acting.
2. Find the one fact the change is safe because of; look where grep stops.
3. Prove it with a script at certainty step 4+; write through unslop.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
