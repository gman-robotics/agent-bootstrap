---
name: architect
description: "Sketch types, signatures, and module structure before code, then stay in the loop while implementation fills in. Use for /architect, 'architect this', 'design this', or non-trivial work where jumping to code would lock in the wrong shape."
version: 1.0.0
---

# architect

**Purpose**
Sketch types, signatures, and module structure before code, synthesize across model perspectives via arena, then implement against the chosen sketch.

**Trigger**
"architect this", "design this", or non-trivial work where jumping to code would lock in the wrong shape.

**Do not use for**
- Hub plan-only work before code → `agents/software-architect.md` + `grill-with-docs` / `plan-code-review-workflow` (that role never writes code)
- Mechanical edits whose shape is already settled → implement directly
- PR review on an open pull request → `expert-pr-review`

## Companions

| Skill | Role here |
|---|---|
| `how` | Ground every subsystem the design touches |
| `why` | Capture existing rationale when ownership or layering changes |
| `arena` | Produce and synthesize design candidates in Phase B |
| `interrogate` | Adversarial pressure on the synthesized sketch before implementing |
| `reply-contract` | Phase C spec-gate card (Approve/Reject) before fill-in |
| `pstack-principles` | Decision lenses cited by name (exhaust-the-design-space, foundational-thinking, etc.) |

**Verification**
- Phase A produced a traced `how` model (not just file names)
- Phase B ran arena with ≥2 structurally distinct candidates
- Phase C presented `reply-contract` spec-gate card; only literal Approve/Reject stamped implementation
- Phase D deviations surfaced, not absorbed silently
- Rationale shaped per `references/rationale-template.md`

---

# Architect

Design before implementing. Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Synthesize across multiple model perspectives, then fill in code against the chosen sketch. If implementation proves the sketch wrong, throw it out and redesign.

## Start

Open a todolist with one entry per phase before starting.

1. Ground
2. Sketch
3. Agree
4. Implement
5. Scrap

## Phase A: Ground the problem

Build a real mental model of every system the new code touches. Run the **how** skill over the relevant subsystems.

Naming a file isn't grounding. Produce the traced model `how` prescribes. If the design redefines ownership or layering, also run the **why** skill on the existing shape so the rationale becomes a constraint, not a guess.

Skip Phase A only when the work is genuinely greenfield with no surrounding system to integrate.

## Phase B: Sketch

Run the **arena** skill with the design-sketch task and the Phase A grounding artifacts. Pass `references/runner-prompt.md` as each runner's prompt. Each candidate produces a design package shaped per `references/rationale-template.md`.

Use your configured architect runners (defaults Sonnet-tier model (see skills/subagent-routing/SKILL.md), Sonnet-tier model (see skills/subagent-routing/SKILL.md), Haiku-tier model (see skills/subagent-routing/SKILL.md), Sonnet-tier model (see skills/subagent-routing/SKILL.md)).

Design it twice. Require at least two structurally distinct candidates before synthesis, even when the first looks sufficient. This is the **pstack-principles** (exhaust-the-design-space) principle made concrete. Whole-shape alternatives, not point fixes inside one shape.

Screen every candidate against [`references/design-red-flags.md`](references/design-red-flags.md) before synthesis. Reject or revise shallow modules, information leakage, temporal decomposition, and pass-through methods.

Compare viable candidates on interface depth. Prefer the design that hides more complexity behind a smaller, simpler public surface. A rich interface can keep call chains short by concentrating capability instead of scattering it across layers.

Arena returns one synthesized design package. The synthesis decision populates the rationale's "Synthesis decision" section.

## Phase C: Agree

Default: present the synthesized design via `reply-contract`'s spec-gate card (`skills/reply-contract/SKILL.md`; same contract as `grill-with-docs` Step 4 and `docs/shared/constitution.md` Article 1). `Documents:` names the rationale/sketch location. Only a literal **Approve** or **Reject** counts — chat prose ("looks good", silence) does not stamp the gate. Implementation fill-in starts only after Approve.

This is **not** the same role as `agents/software-architect.md` (hub plan role: collaborates on goals/scope/risks, never writes code). This `architect` skill is an implementer workflow: sketch types and signatures, then fill them in.

`pstack-principles` (never-block-on-the-human) lets reversible investigation proceed without permission pauses, but **does not** override this spec-gate. `figure-it-out` cites the same carve-out for multi-hour run checkpoints.

The synthesis can ship as its own commit either way, as the "scaffold first" mode of the **pstack-principles** (foundational-thinking) principle. Planned and scoped breakage during fill-in is fine, per the **pstack-principles** (outcome-oriented-execution) principle. For adversarial pressure on the design before implementing, run the **interrogate** skill on the synthesized sketch.

If the human pushes back on the shape (in a checkpoint or after the fact), treat that as Phase A evidence. Re-ground and re-run Phase B before writing more code.

## Phase D: Implement against the sketch

Replace `not implemented` bodies with code, pseudocode with logic. The synthesized sketch is the contract.

Deviations from the sketch are signal worth surfacing, not friction to absorb silently. If a function needs a parameter the sketch didn't anticipate, ask whether the sketch was wrong, the requirement was missed, or the implementation is overreaching.

## Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch can't absorb, throw the sketch out. Don't bolt fixes onto a wrong design, per the **redesign-from-first-principles** and **pstack-principles** (fix-root-causes).

The signal is a *pattern*, not single instances. Tells:

- The same shape of workaround appearing repeatedly across unrelated code.
- Multiple unrelated edge cases that all need special-case branches.
- Types that need escape hatches (`any`, casts, optional fields always set in practice) to compile.
- The "we need a lock" reflex when the sketch said the state wasn't shared.
- Callers having to know the abstraction's internal rules to use it.
- Two or more independent Phase D deviations of the same shape across the implementation.

Use judgment. A few edge cases don't condemn an architecture. Some problems are legitimately complex. Complexity in the data is not complexity in the design.

When you scrap:

1. Re-run the **how** skill over what's been built.
2. Redesign as if the new constraints had been day-one assumptions, per redesign-from-first-principles.
3. Subtract before adding, per the **pstack-principles** (subtract-before-you-add) principle. The new sketch should be smaller than the old one before it grows.
4. Return to Phase B and re-run arena.

## Outputs

The caller's usage is written first and the type sketch derived from it. One file with new types and signatures for small changes. Module map plus type definitions for larger work. The rationale ships alongside, shaped per `references/rationale-template.md`, including the usage sketch and the synthesis decision.

## Provenance

Adapted from [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT). Native multi-harness hub playbook — not a marketplace plugin copy. Cursor-only harness names stripped per `skills/subagent-routing/SKILL.md`.

*Last updated: 2026-09-15 | Hub version: 0.11.0*
