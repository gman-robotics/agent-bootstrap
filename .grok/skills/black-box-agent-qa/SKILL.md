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
2. Name a literal input fixture and a specific, checkable expected output before running anything.
3. Actually run the real system under test; a diff read or a mock-only suite is not a pass.
4. Environment-blocked runs escalate, they do not pass; never authorize auto-merge or a silent harness/agent-state refine from the run.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
