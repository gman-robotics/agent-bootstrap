---
name: compound-refresh
description: "Use to maintain docs/solutions. Classify each note Keep, Update, Consolidate, Replace, or Delete. Delete only when the lesson lives elsewhere, and only with evidence."
version: 1.0.0
---

# compound-refresh — Keep the solution corpus true

**Purpose**
`docs/solutions/` rots if nobody audits it. This skill classifies each note and applies the safe edits. Delete is rare.

**Trigger**
"Refresh solutions", "compound-refresh", or a scheduled pass after several `compound` writes.

**Do not use for**
- Writing a new lesson from this session → `compound`
- A whole-repo code audit → `codebase-simplification-audit`

## Steps
1. Resolve `<project>/docs/solutions/` the same way `compound` does. Skip `README.md` and `_archived/`.
2. For each note, read the code and docs it cites. Classify:
   - Keep — still true, and not a duplicate.
   - Update — drifted. Fix the stale lines. Do not rewrite the lesson.
   - Consolidate — two notes say the same thing. Merge into one. Point the other at the survivor, then archive it.
   - Replace — a newer note supersedes this one. Archive the old file under `_archived/`.
   - Delete — the lesson is fully captured in a test, a comment, or an instruction file. You must name that file.
3. Interactive mode asks before Delete or Consolidate. Autofix may Update drift. Autofix must not Delete.
4. Write a report: Applied, Recommended, Evidence. Update `CONCEPTS.md` only for terms you removed or merged.
5. Do not commit unless the user asked for the commit.

## Companions

| Skill | Role here |
|---|---|
| `compound` | Writes the notes this skill maintains |
| `docs-protocol` | ADR and shared-doc rules still win for decisions |

## Provenance
Adapted from EveryInc/compound-engineering-plugin `ce-compound-refresh` (MIT, Copyright (c) 2025 Every). Independent rewrite. No plugin tree copied.

Last updated: 2026-10-05
