---
name: compound-refresh
description: Maintain docs/solutions. Classify each note Keep, Update, Consolidate, Replace, or Delete. Delete only with evidence. Autofix must not delete.
metadata:
  short-description: Refresh the solutions corpus
---

# compound-refresh

Triggers when docs/solutions needs a Keep/Update/Consolidate/Replace/Delete pass.

## Quick Start

1. Read `references/source.md` before acting.
2. Classify each note. Autofix may update drift. Autofix must not delete.
3. Write an Applied vs Recommended report.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
