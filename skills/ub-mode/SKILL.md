---
name: ub-mode
description: "Use when writing or changing code under the reduced Make it Work, Make it Right, and Practice loop (/ub-mode). Dryer, crapper, and mutator block by default (scripts/run_ub_gates_ci.sh, UB_GATES_ADVISORY=0). Advisory mode is only run_ub_gates_report.sh or UB_GATES_ADVISORY=1. Cite pstack-principles by name only; definitions live in skills/pstack-principles/SKILL.md."
version: 1.0.5
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
| `plan-code-review-workflow` | Reviewer reads CI `ub-gates` outcome in Phase 3 (implementer Phase 2.75) |
| `expert-pr-review` | Reviewer reads CI `ub-gates` outcome in Step 3.5 |
| `lfg` | Reviewer reads CI `ub-gates` outcome in step 4 |

**Verification**
- Phase 1 checks cite real test output (prove-it-works).
- Phase 2 gate block cites measured results (CRAP, dry.edn candidates, mutator exits). Blocking findings on changed code are fixed or escalated before the PR.
- Practice log lists action + reason for each gate run or skip.

---

## How to run the three phases

Every change walks:

1. **Make it Work** — behavior first.
2. **Make it Right** — root cause, units, behavior tests, then gates.
3. **Practice** — log, context, worktrees, commits.

**Blocking by default:** `scripts/run_ub_gates_ci.sh` defaults to `UB_GATES_ADVISORY=0`. Dryer, crapper, and mutator fail the job on findings in changed scope, on `tool_error`, on `skipped_tools_missing`, and on `skipped_mutator`. Advisory mode is only `scripts/run_ub_gates_report.sh` or an explicit `UB_GATES_ADVISORY=1`. There is no waiver. A red **`ub-gates`** check is a gate miss. Gate misses **do not** count as review rounds.

**Pre-PR dev flow (implementer):** Before opening a PR, run dryer, crapper, and mutator on the new code and act on the results. Local recipe (no host installs): `bash scripts/ub_gates_container.sh` (`docker run --rm`, `UB_GATES_ADVISORY=0`). Usage line: `Usage: bash scripts/ub_gates_container.sh [--help] [--worktree PATH] [--main-git PATH] [--metrics-dir PATH]`. Scope is changed functions (crapper) and changed lines (dryer, mutator). Test paths, `.pyi`, and `.d.ts` are out of scope. Debt in untouched old functions does not block. The PR **`Gates:`** section reports the real results. See `docs/shared/ub-mode-practice.md`.

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

### Quality gates (blocking on changed code)

Language matrix and commands: `references/gates-by-language.md`. Supported languages: Clojure, Java, Go, TypeScript, Rust, Python (crapper also covers JavaScript variants; dryer TypeScript files only — see reference). If the repo uses another language, state that no unclebob gate applies; do not invent a scanner.

| Gate | Tool | Measured result (report honestly) | Evidence |
| --- | --- | --- | --- |
| CRAP | crapper | changed functions at **CRAP ≤ 10** are clean; other functions are `crapper_debt` (reported only) | `.metrics/crap.edn` |
| Duplication | dryer | candidates **≥ 0.8** that overlap changed lines block; other candidates are `dryer_debt` (reported only) | `.metrics/dry.edn` |
| Mutation | mutator | changed lines; 20-minute budget; a timeout is reported and does not block; exit `3` means **survivors** | `.metrics/mutate/*.edn` |

**Gate block (run after tests pass, before the PR; blocking on changed scope)**

1. `crapper --threshold 10` on the merge-base file list. Blocking findings are changed functions with CRAP > 10. Report them from `.metrics/crap.edn`.
2. **dryer (GMA-411):** `rm -f .metrics/dry.edn` then `dryer --threshold 0.8` on that list. Blocking findings are candidates ≥ 0.8 that touch changed lines (dryer exit `0` still needs the fresh `.metrics/dry.edn` read).
3. `mutator` on changed lines. Budget is 20 minutes per PR. A timeout is reported (it leads the summary) and does not block. Exit `3` means **survivors** and blocks. A skip in blocking mode is `skipped_mutator` and fails.

Prefer `bash scripts/ub_gates_container.sh` so the three tools run inside a throwaway container. Fix blocking findings on changed code, or escalate them to the CoS. Findings and debt in untouched old functions do not block.

Record real results on the PR **`Gates:`** line (see `docs/shared/ub-mode-practice.md`). The reviewer reads **`ub-gates`** at head SHA only. A red or missing **`ub-gates`** check is a gate miss (hand back, not a review round).

Optional visualization: [uml-viewer](https://github.com/unclebob/uml-viewer) reads the same `.metrics/` files.

**Exit**: Judgment principles satisfied; gate results reported or skip reason recorded.

---

## Phase 3 — Practice

| Practice | Rule |
| --- | --- |
| Log | Keep a log of every action and the reason; attach to PR or review handback |
| Context | **guard-the-context-window** — keep the main thread small; bulk work elsewhere with a summary |
| Worktrees | Find what is safe to remove; uncommitted work waits for a human decision |
| Commits | Commit often in small ordered commits; each states **why**, **what**, and **how proved** |

Push only when the parent workflow allows (hub global rules).

---

## Wiring in other skills

- **`plan-code-review-workflow`**: Implementer runs pre-PR dev flow (Phase 2.75); reviewer confirms CI `ub-gates` outcome (Phase 3).
- **`expert-pr-review`**: Step 3.5 confirms CI `ub-gates` at head SHA — does **not** re-run gate tools.
- **`lfg`**: Steps 3.4–3.5 implementer pre-PR dev flow; step 4 reviewer confirms CI only.

---

## Provenance

Adapted from [unclebob/ub-mode](https://github.com/unclebob/ub-mode). Gate tools are external repositories (see `NOTICE.md`). Hub doc: `docs/shared/ub-mode-practice.md`.

*Last updated: 2026-10-30 | Hub version: 0.14.0*
