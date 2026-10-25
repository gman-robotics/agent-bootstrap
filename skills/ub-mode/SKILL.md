---
name: ub-mode
description: "Use when writing or changing code under the reduced Make it Work, Make it Right, and Practice loop (/ub-mode). Runs deterministic quality gates (crapper, dryer, mutator) before APPROVE when those tools exist for the project's language. Cite pstack-principles by name only; definitions live in skills/pstack-principles/SKILL.md."
version: 1.0.0
---

# ub-mode — Make it Work, Make it Right, Practice

**Purpose**
Enforce a thin, repeatable engineering loop when implementing or reviewing code. Pair judgment from **pstack-principles** with deterministic gates from [unclebob/crapper](https://github.com/unclebob/crapper), [unclebob/dryer](https://github.com/unclebob/dryer), and [unclebob/mutator](https://github.com/unclebob/mutator). Adapted from [unclebob/ub-mode](https://github.com/unclebob/ub-mode); see `NOTICE.md`.

**Trigger**
`/ub-mode`, "ub mode", "run the reduced principles", or any workflow step that names this skill before APPROVE (`plan-code-review-workflow`, `expert-pr-review`, `lfg`).

**Do not use for**
- Whole-repo simplification audit → `codebase-simplification-audit`
- Architectural checklist only (no CRAP/DRY/mutation tools) → `agents/software-architect.md` review phases
- Ordinary application TDD mechanics → `write-tests` (this skill calls it in phase 1)
- Black-box proof that a skill file works → `black-box-agent-qa`

## Companions

| Skill | Role here |
| --- | --- |
| `pstack-principles` | Named principles only — never copy definitions here |
| `write-tests` | Red/Green/Refactor during Make it Work |
| `plan-code-review-workflow` | Invokes this skill before QA APPROVE |
| `expert-pr-review` | Invokes gate block after build/test, before recommendation |
| `lfg` | Invokes gate block after simplify, before review sign-off |

**Verification**
- Phase 1 checks cite real test output (prove-it-works).
- Phase 2 gate block cites tool exit codes and `.metrics/` paths when tools exist.
- Practice log lists action + reason for each gate run or skip.

---

## How to run the three phases

Every change walks:

1. **Make it Work** — behavior first.
2. **Make it Right** — root cause, units, behavior tests, then gates.
3. **Practice** — log, context, worktrees, commits.

Do not APPROVE a PR or end the CODE phase until phase 2 gates pass or are explicitly skipped with a recorded reason (missing tool, unsupported language).

---

## Phase 1 — Make it Work

Apply these **pstack-principles** by name while implementing:

| Principle | Practice hint |
| --- | --- |
| laziness-protocol | One decision, one place; smallest edit |
| foundational-thinking | Data shape before logic; avoid shared mutable state |
| (TDD) | Follow `write-tests`: failing test first |
| redesign-from-first-principles | Do not bolt on; deliver in pieces |
| attack-the-premise | When two fixes fail the same gate, state the premise and remove it |
| subtract-before-you-add | Remove complexity before adding |
| outcome-oriented-execution | Aim at a checkable end state |
| build-the-lever | Automate repeated judgment |
| model-the-domain | Illegal states impossible; glossary when needed |
| boundary-discipline | Validate at the edge; pure core |
| type-system-discipline | Illegal values unrepresentable |
| make-operations-idempotent | Safe retry and crash recovery |
| separate-before-serializing-shared-state | One writer or separate ownership |

**Exit**: Tests green for the scoped change; each plan step's named check ran before the next step (**sequence-verifiable-units**).

---

## Phase 2 — Make it Right

### Judgment (always)

| Principle | Practice hint |
| --- | --- |
| fix-root-causes | Reproduce; no guard that only hides the crash |
| sequence-verifiable-units | One small unit, then check, then next |
| test-behavior-not-implementation | User-visible results only |

Refactor only after behavior is pinned: structure changes, proof unchanged (**prove-it-works**).

### Quality gates (when tools exist)

Language matrix and commands: `references/gates-by-language.md`. Supported languages: Clojure, Java, Go, TypeScript (incl. JS variants), Rust, Python. If the repo uses another language, state that no unclebob gate applies; do not invent a scanner.

| Gate | Tool | Hub threshold | Evidence |
| --- | --- | --- | --- |
| CRAP | crapper | worst score **&lt; 10** (`--threshold 10`) | `.metrics/crap.edn` |
| Duplication | dryer | flag pairs **≥ 0.8** (`--threshold 0.8`) | `.metrics/dry.edn` |
| Mutation | mutator | exit `0`; cover uncovered, kill survivors, delete dead code | `.metrics/mutate/*.edn` |

**Gate block (run in order after tests pass)**

1. `crapper --changed --threshold 10` (or full tree when the diff is wide).
2. `dryer --changed --threshold 0.8`.
3. `mutator --changed` (install crapper beside mutator per upstream README).

On failure: fix or split code; re-run from step 1. On missing tool: log skip reason; do not claim APPROVE on gate-backed quality.

Optional visualization: [uml-viewer](https://github.com/unclebob/uml-viewer) reads the same `.metrics/` files; not required for pass/fail.

**Exit**: Judgment principles satisfied **and** gates green or explicitly skipped with reason.

---

## Phase 3 — Practice

| Practice | Rule |
| --- | --- |
| Log | Every action + reason; attach to PR or review handback |
| Context | **guard-the-context-window** — bulk work in subagents; main thread keeps summary |
| Worktrees | Remove safe cruft; uncommitted work needs a human decision |
| Commits | Small, ordered; message states **why**, **what**, **how proved** |

Push only when the parent workflow allows (hub global rules).

---

## Wiring in other skills

- **`plan-code-review-workflow`**: After phase 2.5 (simplify the diff), run this skill's gate block before QA may recommend APPROVE.
- **`expert-pr-review`**: After Step 3 build/test pass, run the gate block before Step 5 recommendation.
- **`lfg`**: After step 3 (simplify), run the gate block before step 4 review sign-off.

---

## Provenance

Adapted from [unclebob/ub-mode](https://github.com/unclebob/ub-mode). Gate tools are external repositories (see `NOTICE.md`). Hub doc: `docs/shared/ub-mode-practice.md`.

*Last updated: 2026-10-25 | Hub version: 0.13.0*
