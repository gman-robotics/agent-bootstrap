---
name: lean-context
description: Keep agent context small: extract only needed text with rg, jq, markitdown, and trafilatura; prefer targeted reads over full dumps.
metadata:
  short-description: Lean context extraction
---

# lean-context

Triggers on large logs, docs, HTML/PDF, or JSON blobs where full dumps would crowd the transcript.

## Quick Start

1. Read `references/source.md` before extracting.
2. Run `bash scripts/box-tools.sh --check` to see which CLI helpers are present.
3. Use rg/jq/markitdown/trafilatura for slices; write long extracts to files, not chat.

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
