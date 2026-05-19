---
name: write-tests
description: Use when implementing features, fixing bugs, or refactoring code that requires strict red-green-refactor TDD with the project's existing test framework.
metadata:
  short-description: TDD execution playbook
---

# write-tests

Triggers on requests to add behavior, fix a bug, improve coverage, or retrofit tests around existing code.

## Quick Start

1. Read `references/source.md` before changing production code.
2. Write one failing test for the next behavior, then make it pass with the minimum change.
3. Run the focused test and then the relevant full suite after each meaningful step.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
