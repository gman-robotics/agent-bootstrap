---
name: split-branch-for-pr
description: Split mixed commits onto a fresh branch and open a clean PR.
metadata:
  short-description: Split a messy branch into a clean PR
---

# split-branch-for-pr

Triggers on split this work into its own branch or PR.

## Quick Start

1. Read `references/source.md` before acting.
2. Cherry-pick only the relevant commits.
3. Strip swept-in files in a follow-up commit.
4. Force-push the old branch only after an explicit confirm.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
