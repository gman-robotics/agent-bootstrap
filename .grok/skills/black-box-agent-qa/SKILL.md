---
name: black-box-agent-qa
description: Use before treating any agent, harness, verb, or skill change as verified: name an input fixture and expected output, then actually run it. Reading the PR or skill Markdown is not a pass; mocking the system under test is not the only proof; an environment-blocked run escalates, it never passes.
metadata:
  short-description: Black-box run-it verification for agent/harness/skill changes
---

# black-box-agent-qa

Triggers before marking a change to an agent persona, harness wiring, a verb/command, or a skill file as tested, passing, or ready to ship.

## Quick Start

1. Read `references/source.md` before acting; it is the authoritative workflow.
2. Write fixtures/<case>/case.json (schema: SCHEMA.md), then run scripts/run_black_box_fixture.py to actually execute it against the real system under test.
3. A diff read, a description, or a mock-only suite is not a pass; check scripts/check_skill_live.py <name> exits 0 before treating a skill as live.
4. Environment-blocked runs escalate (verdict blocked), they do not pass; never authorize auto-merge or a silent harness/agent-state refine from the run.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
