---
name: maintain-repo-standards
description: Periodic drift pass for standards-<repo> and GitHub templates; at most one PR; never product code.
metadata:
  short-description: Maintain repo standards
---

# maintain-repo-standards

Triggers on /maintain-repo-standards or standards drift audit.

## Quick Start

1. Read `references/source.md` before acting.
2. Re-interview CI and templates vs standards skill; fix drift in scope only.
3. Declare outcome clean, changed, or blocked.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
