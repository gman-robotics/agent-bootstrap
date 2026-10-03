---
name: blocker-walkthrough
description: Use when Tom asks to be walked through the blockers or open decisions; explain each blocking decision one at a time with context and answer options.
metadata:
  short-description: One-at-a-time blocker walkthrough
---

# blocker-walkthrough

Triggers on walk me through the blockers, or the same request in other words.

## Quick Start

1. Read `references/source.md` before acting.
2. List and order the blockers, then explain blocker 1 fully. Put the answer options at the END of the message.
3. Wait for the answer, act on it, then go to the next blocker. Never ask two questions at once.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
