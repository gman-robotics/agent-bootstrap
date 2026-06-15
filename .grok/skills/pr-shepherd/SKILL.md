---
name: pr-shepherd
description: Use to keep open PRs moving: classify blockers, front-load all reviewer-dependent asks in the first hour, and fill reviewer-wait time with reviewer-free work.
metadata:
  short-description: PR pipeline shepherding
---

# pr-shepherd

Triggers at the start of the working day, after opening or un-drafting a PR, or when asked what is blocked or for PR status.

## Quick Start

1. Read `references/source.md` before acting.
2. Enumerate open PRs across manifest repos and classify each blocker.
3. Batch every review request and ping in the first hour, then pick disjoint fill work.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
