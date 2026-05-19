---
name: memory-bank-protocol
description: Use whenever a project needs the six-file memory-bank structure, when starting a session, switching projects, or updating persistent project state.
metadata:
  short-description: Memory-bank protocol
---

# memory-bank-protocol

Triggers on project initialization, session startup, project switching, or requests to update long-lived project context.

## Quick Start

1. Read `references/source.md` before initializing or updating a memory bank.
2. At session start, read all six core files in the required order before significant work.
3. At task end, update `activeContext.md` and `progress.md`, then verify the edits.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
