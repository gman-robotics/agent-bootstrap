---
name: create-repo-standards
description: Interview a repository and generate standards-<repo> in harness skill folders plus GitHub PR/issue templates for consistent agent workflows.
metadata:
  short-description: Bootstrap repo standards skill
---

# create-repo-standards

Triggers on /create-repo-standards for a manifest-owned project.

## Quick Start

1. Read `references/source.md` before acting.
2. Interview templates, CI, AGENTS.md, PRs; write standards-<repo> and .github templates.
3. Prove the skill loads with no placeholders; offer maintain-repo-standards.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
