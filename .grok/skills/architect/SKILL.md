---
name: architect
description: Use to sketch types, signatures, and module structure before code, run arena for competing designs, then implement against the chosen sketch and scrap when wrong.
metadata:
  short-description: Design-before-code with arena synthesis
---

# architect

Triggers on architect this, design this, or non-trivial work where jumping to code locks in the wrong shape.

## Quick Start

1. Read `references/source.md` before acting.
2. Ground with how (and why if ownership changes), then run arena with references/runner-prompt.md.
3. Phase C: reply-contract spec-gate (literal Approve/Reject) before fill-in; companions interrogate, pstack-principles.
4. Implement against the synthesized sketch; scrap and re-arena on repeated pattern friction.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
