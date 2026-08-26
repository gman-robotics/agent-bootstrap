---
name: reply-contract
description: Use when giving status, a your-turn / smoke checklist, or any longer explanation to a human who may have just switched projects. Write as if they are new: one show-me visual, gloss jargon, leftover vs bug, who is waiting.
metadata:
  short-description: Status and your-turn as if they just walked in
---

# reply-contract

Triggers on status after another agent finished, smoke / tap-through, or anything the human must do or decide.

## Quick Start

1. Read `references/source.md` before writing the reply.
2. Load `skills/show-me/SKILL.md` for the one visual (tree, stack, or diff); never reimplement its recipes here. No mermaid/HTML on Photon unless asked.
3. Gloss only the jargon you used. Say leftover vs bug and who is waiting.
4. Use the spec-gate card for a binary Approve/Reject on a held artifact; use the clarify card for a plain question, never both.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
