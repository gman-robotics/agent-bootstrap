---
name: agent-bootstrap
description: Load and follow the Agent Bootstrap Hub instructions, memory-bank protocol, manifest, skills catalog, and replay guidance for syncing this shared hub across project checkouts.
---

# Agent Bootstrap Hub

Use this skill when working inside an `agent-bootstrap` checkout, syncing hub updates
between project copies, or helping another harness load the shared team rules.

## Quick Start

1. Read `AGENTS.md`; it is the single source of truth for agent behavior in this
   repository.
2. Read the hot memory-bank files: `memory-bank/activeContext.md` and
   `memory-bank/progress.md`.
3. Read `skills/INDEX.md` before invoking or editing any workflow skill.
4. Check `manifest.yaml` to resolve sibling project paths before copying,
   cherry-picking, or replaying hub updates into another checkout.

## Replay Guidance

- Prefer `git cherry-pick` when the target checkout shares history with this
  repository.
- Prefer a scoped patch (`git format-patch` / `git apply --3way`) when the target
  checkout has local-only commits or a different remote.
- Re-run the relevant tests after replaying script or exporter changes.
- Re-export generated harness packaging after changing canonical skill sources.
