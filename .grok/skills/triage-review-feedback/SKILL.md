---
name: triage-review-feedback
description: Use when a PR we authored receives review feedback from humans, AI reviewers, or scanners: verify every claim against the code, then fix or dismiss with evidence.
metadata:
  short-description: Respond to PR review feedback
---

# triage-review-feedback

Triggers when our PR gets a review, inline comments, or scanner findings, or the user asks to address review feedback on a PR.

## Quick Start

1. Read `references/source.md` before acting.
2. Inventory all claims first; verify each at the cited code location before classifying.
3. Fix TDD-first, QA-pass before posting, reply to every thread, then re-request review.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
