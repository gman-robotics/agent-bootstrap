---
name: lfg
description: Run the agreed loop hands-off: route, implement, simplify the diff, review, compound, push a PR, watch CI. Do not merge unless granted.
metadata:
  short-description: Compose the loop through a PR
---

# lfg

Triggers when a plan or bug should become a PR without a merge.

## Quick Start

1. Read `references/source.md` before acting.
2. Call existing skills. Stop if review invalidates a settled decision.
3. Push the PR and watch CI. Do not merge unless granted.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
