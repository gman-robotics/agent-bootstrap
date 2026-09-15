---
name: pstack-principles
description: "High-leverage engineering principles ported from pstack: prove-it-works, encode-lessons-in-structure, test-behavior-not-implementation, separate-before-serializing-shared-state, sequence-verifiable-units, guard-the-context-window, subtract-before-you-add, laziness-protocol, and related rules. Reference by principle name from workflow skills."
version: 1.0.0
---

# pstack-principles — High-leverage rules in one place

**Purpose**  
Pack the most reusable pstack principles into one reference skill. Workflow skills (`architect`, `arena`, `figure-it-out`, `blast-radius`, etc.) cite these by name instead of duplicating prose.

**Trigger**  
Any task where a workflow skill names a principle, or when you need a decision lens before designing, implementing, reviewing, or verifying.

**Do not use for**  
Replacing a full workflow skill. This is the principle catalog, not the procedure.

---

## Hard carve-out — gated engineering gates win

**`never-block-on-the-human` does NOT override hub gated engineering.**

Proceed on reversible work without permission pauses — but when `reply-contract`, `grill-with-docs`, `plan-code-review-workflow`, or `docs/shared/constitution.md` Article 1 require a **spec-gate card**, only a literal **Approve** or **Reject** counts. "Looks good", silence, and chat-prose agreement do not stamp the gate. Irreversible actions still need explicit confirmation.

---

## Quick reference index

| Principle | One line |
|---|---|
| prove-it-works | Check the real artifact; script the check when you can |
| encode-lessons-in-structure | Second time you write the same instruction → lint/check/script |
| test-behavior-not-implementation | Assert literal observable output, not mocks or constant pins |
| separate-before-serializing-shared-state | Separate writers first; locks only when sharing is invariant |
| sequence-verifiable-units | Verify each unit before the next; stack commits to prove delivery |
| guard-the-context-window | Subagents hold bulk; main thread gets summaries |
| subtract-before-you-add | Remove dead code before building |
| laziness-protocol | Deletion, flat hierarchy, minimal diff |
| build-the-lever | Codemod/script/skill artifact a reviewer can rerun |
| foundational-thinking | Data structures first; scaffold before features |
| exhaust-the-design-space | 2–3 structurally distinct prototypes before commit |
| redesign-from-first-principles | Redesign as if the requirement was day-one |
| fix-root-causes | Reproduce; ask why; no nil-check band-aids |
| boundary-discipline | Validate at boundaries; pure logic inside |
| type-system-discipline | Illegal states unrepresentable; parse at boundaries |
| minimize-reader-load | Fewer layers + less hidden state |
| model-the-domain | State machines, unions, registries vs scattered ifs |
| make-operations-idempotent | Safe on retry/crash; converge to end state |
| migrate-callers-then-delete-legacy-apis | Same-wave migration + delete old API |
| outcome-oriented-execution | Target architecture over smooth throwaway intermediates |
| experience-first | User/colleague delight over implementation convenience |
| attack-the-premise | 2+ failed fixes sharing a premise → census, question premise |
| never-block-on-the-human | Proceed on reversible work; confirm irreversible only (**see carve-out above**) |

---

## Execution

### prove-it-works
Verify every output against the real thing: run the feature, read the actual value, inspect the diff — not proxies or self-reports. Write a deterministic script when possible; keep output visible for review.

### sequence-verifiable-units
Break sweeps/migrations into units that each end checkable. Verify before advancing. Stack commits/PRs so the sequence proves delivery (failing test first, then fix).

### build-the-lever
For non-trivial work, build the tool that does or proves the job (codemod, generator, rerunnable check). Skip only when trivial. A delegate skill contract counts as a lever when fanning out.

### never-block-on-the-human
Supervise asynchronously: do reversible work, present results, let the human course-correct. Ask only on genuine ambiguity. **Does not relax spec-gate Approve/Reject or irreversible-action confirmation.**

### outcome-oriented-execution
Optimize for the verifiable end state. Planned intermediate breakage is acceptable when scoped and reversible; full verification still runs before done.

---

## Design

### foundational-thinking
Get data structures right before logic. Scaffold (CI, types, test harness) before features. Subtraction before scaffolding.

### exhaust-the-design-space
When no precedent exists, build 2–3 competing prototypes/sketches. A second flavor of the first shape does not count.

### redesign-from-first-principles
When integrating a new requirement, ask "if this were day-one, what would we build?" Propagate through types, docs, examples.

### model-the-domain
Prefer state machines, discriminated unions, registries over scattered booleans and phase-named modules.

### experience-first
When convenience conflicts with user/colleague delight, choose delight. Ship fewer polished features over more rough ones.

### attack-the-premise
When 2+ fixes sharing one premise fail the same gate: write the premise, census per actor (scripted), remove asymmetry instead of compensating.

---

## Code shape

### boundary-discipline
Validate/narrow at system boundaries (CLI, config, network). Trust typed internals. Business logic in pure functions.

### type-system-discipline
Make illegal states unrepresentable. Brand semantic primitives. Parse external data at boundaries. Exhaustive matching on sum types.

### minimize-reader-load
Track layers to trace and hidden state. Collapse pass-through layers. Prefer pure functions and locals over shared mutable state.

### laziness-protocol
Prefer deletion. Flat call hierarchy (rich interfaces are not deep chains). Minimal diff. Question signal threading through many layers.

### subtract-before-you-add
Remove dead code, redundant validators, stub references before adding. Cut before polish.

### migrate-callers-then-delete-legacy-apis
When the new API is right, migrate callers and delete the old path in the same wave — no permanent dual APIs.

---

## Concurrency and state

### separate-before-serializing-shared-state
Give each actor its own file/branch/key when possible. Serialize structurally (lockfile, single writer) only when one shared writer is a real invariant.

### make-operations-idempotent
Every mutating operation must converge on retry: answer "what if this runs twice?" and "what if the last run crashed halfway?"

### fix-root-causes
Reproduce first. Ask why until root. No guards that only silence symptoms. When restart breaks things, suspect stale persistent state.

---

## Agent operations

### guard-the-context-window
Route verbose outputs to subagents. Read selectively. Keep always-used templates inline in the skill file.

### encode-lessons-in-structure
Second time writing the same instruction → lint rule, metadata flag, runtime check, or script. Capture corrections; route to the right layer.

### test-behavior-not-implementation
Call code the way users do; assert literal expected output. If the test passes when every import returns `undefined`, rewrite or delete it.

---

## Companions

| Skill | Relationship |
|---|---|
| `write-tests` | Operational TDD playbook; pairs with test-behavior-not-implementation |
| `black-box-agent-qa` | prove-it-works for harness/skill changes |
| `reply-contract` | owns spec-gate/clarify cards that never-block must not bypass |
| `subagent-routing` | guard-the-context-window + parallel fan-out model policy |
| `expert-pr-review` | distinct from `interrogate` (hub PR review vs multi-model stress test) |

---

## Verification checklist

- [ ] Cited principle name matches this catalog
- [ ] never-block did not bypass a literal Approve/Reject gate
- [ ] prove-it-works evidence is a real artifact or script output, not prose
- [ ] encode-lessons applied when the same instruction appeared twice

## Provenance

Adapted from [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) principle skills (MIT). Combined into one hub reference per GMA-48; individual `principle-*` marketplace skills are not ported separately.

*Last updated: 2026-09-15 | Hub version: 0.11.0*
