---
name: no-comments
description: Strip comments that restate the code and encode real constraints in types, tests, or lint.
metadata:
  short-description: Strip restating comments
---

# no-comments

Triggers on /no-comments before review.

## Quick Start

1. Read `references/source.md` before acting.
2. Limit scope to the caller files or the diff.
3. Encode real do-not constraints; delete the rest.
4. Consult architect once if the finding is a shape problem.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
