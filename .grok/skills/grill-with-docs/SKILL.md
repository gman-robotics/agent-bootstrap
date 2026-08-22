---
name: grill-with-docs
description: Use when aligning on a plan or design before code: grill the user in rounds, keep CONTEXT.md as a glossary, and offer ADRs only for hard-to-reverse trade-offs. Do not implement until they confirm.
metadata:
  short-description: Align on domain language before code
---

# grill-with-docs

Triggers on grill this, grill-with-docs, align on the domain, or build CONTEXT.md before a change.

## Quick Start

1. Read `references/source.md` before acting; it is the authoritative workflow.
2. Hard rule: no implement skills, feature branches, or PRs until the user confirms shared understanding.
3. Ask the whole decision frontier each round; look up facts yourself; write glossary-only CONTEXT.md as terms resolve.
4. Final confirm uses reply-contract's spec-gate card, not chat prose; a single blocking fact-question uses its clarify card.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
