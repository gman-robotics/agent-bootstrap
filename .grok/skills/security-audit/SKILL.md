---
name: security-audit
description: Use only for the literal request 'security audit', 'run the Cloudflare security audit', or an explicit full/comprehensive/end-to-end/pen-test request against a codebase. Do NOT use for generic 'security review', 'review this PR', 'what could this break', or unscoped find-vulnerabilities requests -- those are expert-pr-review / blast-radius. Opt-in only, never auto-invoked.
metadata:
  short-description: Opt-in Cloudflare security-audit vendor (GMA-56)
---

# security-audit

Triggers only on the literal allowlist: 'security audit'/'security-audit', 'run the Cloudflare security audit', or an explicit full/comprehensive/pen-test ask. Never auto-invoked by plan-code-review-workflow or expert-pr-review's SecurityReviewer spawn.

## Quick Start

1. Read `references/source.md` before acting; it is the authoritative workflow.
2. Guidance mode is the default: loading this skill never auto-runs the six-phase audit, creates an output directory, or writes artifacts on its own.
3. Full audit mode requires an explicit ask AND a capability check against the four Universal execution-safety controls (no external network, allowlisted environment, scratch-only writes, explicit resource limits) before any target-controlled build/test/browser/fuzzer; missing any control keeps the result needs_validation, never a silent pass.
4. Not a substitute for expert-pr-review (PR-scoped review) or blast-radius (diff-scoped breakage proof), and neither of those is a substitute for this.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
