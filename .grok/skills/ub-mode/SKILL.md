---
name: ub-mode
description: Use when writing or changing code under the reduced Make it Work, Make it Right, and Practice loop. Report advisory crapper, dryer, and mutator results; gates do not block APPROVE until blocking mode is approved.
metadata:
  short-description: Reduced principles and advisory gates
---

# ub-mode

Triggers on /ub-mode or advisory gate report in plan-code-review, expert-pr-review, or lfg.

## Quick Start

1. Read `references/source.md` and `references/gates-by-language.md` before acting.
2. Phase 1: write-tests and pstack-principles by name. Phase 2: advisory gate report. Phase 3: log and commits.
3. Put results on the PR Gates line; gate findings do not block APPROVE in advisory mode.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
