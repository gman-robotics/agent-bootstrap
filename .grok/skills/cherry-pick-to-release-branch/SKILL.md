---
name: cherry-pick-to-release-branch
description: Use when backporting a merged pull request onto an existing release branch and incrementing the release-candidate version suffix safely.
metadata:
  short-description: Release-branch cherry-pick
---

# cherry-pick-to-release-branch

Triggers on requests to hotfix or backport a merged PR onto a release branch.

## Quick Start

1. Read `references/source.md` before touching git state.
2. Fetch the release branch and the PR head, identify the exact PR commits, then cherry-pick them oldest first.
3. Update all configured version files consistently and verify the branch state before pushing.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
