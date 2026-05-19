---
name: expert-pr-review
description: Use for GitHub pull request reviews that need a deep, critical pass covering context gathering, build and test verification, security review, and a user-approved final review decision.
metadata:
  short-description: Critical PR review workflow
---

# expert-pr-review

Triggers on requests to review a PR, inspect a diff, or provide an approve/request-changes recommendation.

## Quick Start

1. Read `references/source.md` fully before starting the review.
2. Treat this as review-only work: do not edit the PR branch.
3. Present findings and wait for explicit user approval before posting APPROVE or REQUEST_CHANGES.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
