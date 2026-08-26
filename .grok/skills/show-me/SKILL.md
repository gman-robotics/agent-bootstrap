---
name: show-me
description: Use before code ('show the shape' / 'show-me'), or when reply-contract loads it for a status/your-turn visual. Owns the recipes: call tree, file/screen tree, stack, diff of those shapes, optional mermaid. One primary visual per reply.
metadata:
  short-description: Recipes for the one status visual
---

# show-me

Triggers on 'show the shape' / 'show-me' before code, or is auto-loaded by reply-contract for a status/your-turn reply that needs a visual.

## Quick Start

1. Read `references/source.md` for the recipe behind each visual; do not build it from memory.
2. Pick exactly one recipe (call tree, file/screen tree, stack, or diff of those shapes) per reply.
3. Default to fenced text; mermaid or HTML only if the user explicitly asked, and never open it with a shell/browser command.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
