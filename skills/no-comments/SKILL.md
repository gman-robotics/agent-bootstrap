---
name: no-comments
description: "Strip comments that restate the code, then encode real constraints in types, tests, or lint. Use for /no-comments before review."
version: 1.0.0
---

# no-comments

**Purpose**
Remove comments that an agent will copy, and move real constraints into something that fails when skipped.

**Trigger**
"/no-comments", "strip comments", or a review pass whose scope is the current diff.

**Do not use for**
- Prose, PR bodies, or docs → `unslop` and `technical-writing`
- A repeated mistake class across the repo → `correct`
- Designing the module shape → `architect`

## Companions

| Skill | Role here |
|---|---|
| `unslop` | Prose tells; this skill is comments in code |
| `correct` | When a "do not" comment is the second instance of a class |
| `architect` | One consult when the accepted finding is a shape problem |
| `pstack-principles` | encode-lessons-in-structure, minimize-reader-load |

**Verification**
- Scope is the caller files or the diff against the base branch, not the whole repo
- Accepted findings are fixed or reported open with the encoding that was refused
- Rejected findings are not applied
- No new comment that restates the next line

---

# No comments

Review the comments in scope. Reject flags that are invalid, that misstate the code, or that would delete a constraint with no replacement.

Fix accepted findings at the smallest in-scope root cause. Delete dead paths. Do not add a symptom guard. Do not widen scope. Do not restore a comment whose keep was refuted.

For a comment that says do not remove or do not change, offer the cheapest in-scope encoding: a type, a runtime check, a test, or a CI lint whose error names the fix. Encode it if approved. Otherwise delete the comment and report the constraint as open.

If the finding is a shape problem, consult `architect` once, then implement the smallest in-scope fix.

**Reply:** accepted, rejected, encoded, and still-open constraints.

## Provenance

Adapted from [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT), pstack 0.15.9 (2026-10-03). Native multi-harness hub playbook — not a marketplace plugin copy. Cursor-only harness names stripped per `skills/subagent-routing/SKILL.md`.

*Last updated: 2026-10-03 | Hub version: 0.12.0*

