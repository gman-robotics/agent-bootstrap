---
name: feature-flag-lifecycle
description: Use when adding, rolling out, auditing, or removing feature flags so flags stay default-off, tested on both paths, and removed on schedule.
metadata:
  short-description: Feature flag lifecycle
---

# feature-flag-lifecycle

Triggers on requests to create a flag, stage a rollout, or clean up a retired flag.

## Quick Start

1. Read `references/source.md` before implementing the flag.
2. Create default-off flags with an explicit cleanup date and tracking entry.
3. Test both flag-off and flag-on behavior, then remove the flag promptly after rollout.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
