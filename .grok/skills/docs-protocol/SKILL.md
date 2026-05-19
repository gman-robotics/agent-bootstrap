---
name: docs-protocol
description: Use when creating or updating project or shared technical documentation so docs stay separate from operational memory-bank state.
metadata:
  short-description: Technical docs protocol
---

# docs-protocol

Triggers on requests to create or update API docs, data models, pipeline docs, or ADRs.

## Quick Start

1. Read `references/source.md` before editing technical docs.
2. Choose the correct target under `docs/shared/` or `docs/projects/<name>/`.
3. Keep `docs/` for technical reference and `memory-bank/` for operational state.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
