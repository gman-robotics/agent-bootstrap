---
name: pstack-principles
description: Use as the combined reference for high-leverage pstack principles: prove-it-works, encode-lessons-in-structure, test-behavior-not-implementation, guard-the-context-window, never-block-on-the-human (with gated-engineering carve-out), and related rules.
metadata:
  short-description: Combined pstack principles reference
---

# pstack-principles

Triggers when a workflow cites a pstack principle or you need a decision lens before designing or verifying.

## Quick Start

1. Read `references/source.md` before acting.
2. never-block does NOT override literal Approve/Reject spec-gate cards.
3. Cite principles by name; pair prove-it-works with real artifacts or scripts.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
