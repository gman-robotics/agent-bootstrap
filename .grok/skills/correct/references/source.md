---
name: correct
description: "Find mistake classes agents keep repeating and make each one impossible. Prefer architecture, then types, then a lint whose error names the fix, then a test. Docs last. Use for /correct or after the same correction lands twice."
version: 1.0.0
---

# correct

**Purpose**
Turn a repeated agent mistake into a structural fix so the next agent cannot take the short path that compiles and is still wrong.

**Trigger**
"/correct", "stop correcting the same mistake", or any correction that is the second instance of a class already called on this repo.

**Do not use for**
- A single review thread on a PR we authored → `triage-review-feedback` (it already tags FIX as NEW or REPEAT; REPEAT still closes only with a mechanical check)
- Capturing a finished task as a new skill → `reflect`
- Designing a shape before any code exists → `architect`

## Companions

| Skill | Role here |
|---|---|
| `triage-review-feedback` | Per-PR REPEAT rule; this skill raises that rule from one thread to the repo |
| `architect` | Highest fix level when the class is a shape problem |
| `pstack-principles` | encode-lessons-in-structure, fix-root-causes, type-system-discipline |
| `write-tests` | Test level after architecture, types, and lint cannot close the class |

**Verification**
- Each class cites at least two pieces of evidence (commits, reverts, review comments, or agent-instruction workarounds)
- The chosen level is the highest that works, and the reply says why a higher level did not
- The new check fails on a real past mistake, locally and in CI
- The rule table pairs each live rule with what enforces it

---

# Correct

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Change the repo so a change that looks right from one file is right for the whole repo.

## Find the mistake classes

Read recent commits, reverts, review comments, agent instruction files (`AGENTS.md`, `docs/shared/constitution.md`), and comments that explain workarounds. Group into classes. A class counts once it has happened twice.

## Fix each class at the highest level that works

1. **Architecture.** One owner per piece of state. One supported way per task. Hide internals so the wrong import fails. Replace hand-synced lists with one source of truth. Delete the old path an agent would copy.
2. **Types, then lint.** Make the bad state unwritable. If it still compiles, add a lint or CI check whose error names the file, type, or function to use instead. If the pattern is already common, fail only when a change adds more.
3. **Tests.** Assert the behavior. Fix or delete any test that would still pass if every function it calls returned nothing.
4. **Docs last.** Agent rules and prose only for judgment calls. Nothing fails when an agent skips them.

## Fix and prove

Fix the most frequent classes now, one commit each. Prove each new check fails on a real past mistake. Run the same command locally and in CI. Exceptions go on the offending line with a reason, an expiry date, and a human approval.

## Keep the rule table

Keep a table in the agent instruction file (`AGENTS.md` or `docs/shared/constitution.md`) that pairs each rule with what enforces it. When the operator corrects you, fix the mistake and add the rule. If the rule was already there and nothing enforces it, that is a repeat: fix it at the highest level in the same change. Drop a rule once its mistake cannot happen.

**Reply:** each class with its evidence, the level you picked, and why a higher level did not work.

## Provenance

Adapted from [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT), pstack 0.15.9 (2026-10-03). Native multi-harness hub playbook — not a marketplace plugin copy. Cursor-only harness names stripped per `skills/subagent-routing/SKILL.md`.

*Last updated: 2026-10-03 | Hub version: 0.12.0*
