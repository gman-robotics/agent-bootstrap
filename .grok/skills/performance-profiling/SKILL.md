---
name: performance-profiling
description: Use for slow requests, latency spikes, backlog growth, heavy renders, or other performance issues that need measurement-first profiling and before/after validation.
metadata:
  short-description: Performance bottleneck workflow
---

# performance-profiling

Triggers on requests about slowness, timeouts, latency, throughput, or optimization.

## Quick Start

1. Read `references/source.md` before changing code.
2. Define the exact slow path and record a baseline measurement first.
3. Change one thing at a time and re-measure using the same method.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
