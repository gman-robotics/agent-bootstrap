---
name: delegation-patterns
description: Use when spawning subagents in Claude Code or Grok: two-tier model selection, parallel dispatch patterns, and mandatory worktree isolation for editing agents.
metadata:
  short-description: Subagent delegation patterns
---

# delegation-patterns

Triggers when setting up multi-agent delegation, choosing agent tiers, or running parallel analysis or isolated parallel edits.

## Quick Start

1. Read `references/source.md` for the three canonical patterns.
2. Use worktree isolation for ANY editing agent when the checkout may be shared.
3. Emit independent agent calls in a single message so they run in parallel.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
