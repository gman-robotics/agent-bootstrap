---
name: label-adjudication
description: Use for two independent labeler models on JSONL, adjudicator on disagreements only, and provenance-rich outputs for human stamp.
metadata:
  short-description: Two-model JSONL label curation
---

# label-adjudication

Triggers on adjudicate labels, label adjudication, two-model label, or curating labeled JSONL with multi-model agreement.

## Quick Start

1. Read `references/source.md` before acting.
2. Spawn labeler A and B with the same prompt template; no shared chain-of-thought.
3. Merge with scripts/adjudicate_labels.py; adjudicator rows required for every disagreeing id.
4. Emit adjudication.jsonl and final.jsonl; human stamp overrides; never skip conflicts.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
