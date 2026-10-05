---
name: compound
description: "Use after verified work when the reasoning is non-obvious and not already in code, tests, or docs. Write one learning to docs/solutions so the next plan can read it. Skip routine fixes."
version: 1.0.0
---

# compound — Write the lesson the next plan must read

**Purpose**
Close the loop. After verified work, write one durable learning into the active project's `docs/solutions/` so a later plan does not rediscover it. Skip the write when the lesson is already in the code, the tests, or the docs.

**Trigger**
"Compound this", "capture the learning", end of `lfg`, or Phase LEARN of `task-loop-7-phase` when the lesson is non-obvious.

**Do not use for**
- A routine fix whose test already states the lesson
- Unverified work
- A session diary or a status note → `close-out` or `end-of-day-review`
- A skill-gap proposal → `close-out` Phase 2 or `reflect`

## Steps
1. Resolve the root. Use the active project from `manifest.yaml`. Write under `<project>/docs/solutions/`. If that project has no `docs/` tree, use `docs/solutions/` in the repo you are in. Do not invent a second tree.
2. Read existing notes in that folder whose titles overlap this lesson. Update a wrong note. Do not add a twin.
3. Apply the skip rule. Skip when any of these is true:
   - The work is not verified (no failing-then-green test, no recorded command output, no evidence packet).
   - The lesson is already stated by the test name, a comment, or an existing doc.
   - The only fact is that the diff finished.
4. If you skip, stop. Say `Documentation skipped: <reason>`. Do not write a file.
5. If you capture, write one file: `docs/solutions/YYYY-MM-DD-<slug>.md`. One learning per run. A second learning needs a second run.
6. Use this shape:

```yaml
---
title: <one line>
date: YYYY-MM-DD
module: <area>
tags: []
---
```

Then: Problem. What we learned. Why this is not already in the code. Related (plan, PR, test).
7. Add any new term to `docs/solutions/CONCEPTS.md`. One term per line. Do not rewrite the file.
8. End with `Documentation complete: <path>` or `Documentation skipped: <reason>`.

## Companions

| Skill | Role here |
|---|---|
| `compound-refresh` | Later pass that keeps this folder from rotting |
| `grill-with-docs` | Reads this folder before the interview |
| `plan-code-review-workflow` | Reads this folder in PLAN |
| `task-loop-7-phase` | LEARN calls this skill for the repo file; mem0 stays |
| `lfg` | Calls this skill after review fixes |

## Provenance
Adapted from EveryInc/compound-engineering-plugin `ce-compound` (MIT, Copyright (c) 2025 Every). Independent rewrite. No plugin tree copied.
