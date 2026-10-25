---
name: ub-mode
description: Use when writing or changing code under the reduced Make it Work, Make it Right, and Practice loop. Run crapper, dryer, and mutator before APPROVE when those tools exist for the project language.
metadata:
  short-description: Reduced principles and quality gates
---

# ub-mode

Triggers on /ub-mode or before APPROVE in plan-code-review, expert-pr-review, or lfg.

## Quick Start

1. Read `references/source.md` and `references/gates-by-language.md` before acting.
2. Phase 1: write-tests and pstack-principles by name. Phase 2: gate block. Phase 3: log and commits.
3. Do not APPROVE while a gate failed; record skip reasons when tools are missing.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
