---
name: evidence-packet-protocol
description: Use when an implementer/QA-Tester role needs to hand a planner claim-bound, checkable evidence of what actually works (and what still has a gap) instead of a prose status update: the E_t.json evidence packet.
metadata:
  short-description: Claim-bound evidence packets (E_t.json)
---

# evidence-packet-protocol

Triggers after an implementer/QA-Tester turn needing checkable evidence, or before a planner starts the next iteration and must read the prior packet.

## Quick Start

1. Read `references/source.md` before acting; it is the authoritative schema and rules.
2. head_sha is required (GB-4 freeze); qa_status and every record's status are verified|gap only, never partial/blocked/looks good.
3. execution_records must be non-empty and typed screenshot|runtime_trace|fixture; empty is a gap, not a pass (GB-1).
4. Schema failure gets one retry, then ESCALATE at exit 1 (never exit 2, which is the runner's own environment-blocked verdict) -- GB-6.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
