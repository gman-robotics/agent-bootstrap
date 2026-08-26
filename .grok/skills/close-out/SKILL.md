---
name: close-out
description: Use at the end of any significant task or conversation thread to verify memory-bank/shared-memory continuity (Phase 1) and turn session friction into concrete skill/process improvement proposals (Phase 2).
metadata:
  short-description: Task close-out & retrospective
---

# close-out

Triggers on 'close this out', 'wrap this up', or after completing a multi-step implementation session — task-scoped, not day-scoped.

## Quick Start

1. Read `references/source.md` for the full two-phase protocol.
2. Phase 1: audit activeContext.md/progress.md and sync shared memory if configured.
3. Phase 2: scan for friction/skill gaps and propose specific, filed improvements.
4. Step 8 proposals for a skill need a named case.json; Step 9 requires scripts/run_black_box_fixture.py to capture a pass and scripts/check_skill_live.py <name> to exit 0 before the skill is live — approval to write it is not a ship, and re-editing invalidates the record.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
