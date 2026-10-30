---
name: ub-mode
description: Use when writing or changing code under the reduced Make it Work, Make it Right, and Practice loop. Dryer, crapper, and mutator block by default (UB_GATES_ADVISORY=0). Advisory mode is only run_ub_gates_report.sh or UB_GATES_ADVISORY=1.
metadata:
  short-description: Reduced principles and blocking gates
---

# ub-mode

Triggers on /ub-mode or CI ub-gates confirmation in plan-code-review, expert-pr-review, or lfg.

## Quick Start

1. Read `references/source.md` and `references/gates-by-language.md` before acting.
2. Implementer: run dryer, crapper, and mutator on new code before the PR (bash scripts/ub_gates_container.sh). Reviewer: read CI ub-gates outcome only.
3. Put real results on the PR Gates line. Blocking findings on changed code are fixed or escalated to the CoS.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
