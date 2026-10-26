---
name: ub-mode
description: "Use when writing or changing code under the reduced Make it Work, Make it Right, and Practice loop (/ub-mode). Reports advisory quality-gate results (crapper, dryer, mutator) when those tools exist; gates do not block APPROVE until Tom approves blocking mode. Cite pstack-principles by name only; definitions live in skills/pstack-principles/SKILL.md."
version: 1.0.4
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
- Phase 2 gate block cites measured results (CRAP, dry.edn candidates, mutator exits) when tools exist; findings are advisory only.
- Practice log lists action + reason for each gate run or skip.

---

## How to run the three phases

Every change walks:

1. **Make it Work** — behavior first.
2. **Make it Right** — root cause, units, behavior tests, then gates.
3. **Practice** — log, context, worktrees, commits.

**Advisory mode (hub default):** Run phase 2 gates when practical and **report** results in the PR body (`Gates:` line) or review handback. Gate findings **do not** block APPROVE and **do not** count as review rounds. Blocking mode starts only after Tom explicitly approves switching ub-mode to blocking gates.

**Pre-PR dev flow (implementer):** Pass the merge-base **scope** file list to `crapper --threshold 10` and `dryer --threshold 0.8` (`rm -f .metrics/dry.edn` first) and **fix** what they flag. Use upstream `--changed` only for **uncommitted** edits (`git status`). Run **mutator** on scope on a **laptop** or in **CI** only (`--since-last-run` for incremental function reruns). CI **`ub-gates`** uses the same scope on every `push` / `pull_request`. See `docs/shared/ub-mode-practice.md`.

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

### Quality gates (advisory report when tools exist)

Language matrix and commands: `references/gates-by-language.md`. Supported languages: Clojure, Java, Go, TypeScript, Rust, Python (crapper also covers JavaScript variants; dryer TypeScript files only — see reference). If the repo uses another language, state that no unclebob gate applies; do not invent a scanner.

| Gate | Tool | Measured result (report honestly) | Evidence |
| --- | --- | --- | --- |
| CRAP | crapper | worst function **CRAP ≤ 10** is clean; `--threshold 10` exits non-zero only when worst **&gt; 10** | `.metrics/crap.edn` |
| Duplication | dryer | read `.metrics/dry.edn`: list any `:candidates` with `:score` **≥ 0.8** (dryer exits `0` even when pairs meet the threshold) | `.metrics/dry.edn` |
| Mutation | mutator | exit `0` clean; exit `3` means **survivors**; cover the uncovered, kill the survivors, delete dead code | `.metrics/mutate/*.edn` |

**Gate block (run in order after tests pass; report only — advisory until blocking mode is approved)**

1. `crapper --threshold 10` on **scope** paths (merge-base diff, or `--changed` only with uncommitted edits). Report worst CRAP from `.metrics/crap.edn` or stdout.
2. **dryer (GMA-411):** `rm -f .metrics/dry.edn` then `dryer --threshold 0.8` on **scope**. Parse `.metrics/dry.edn` for candidates ≥ 0.8 (dryer exit `0` is not “clean”).
3. `mutator` on **scope** (install crapper beside mutator per upstream README). `--changed` = changed **files** from `git status`; `--since-last-run` for function-level reruns. Note exit `3` = survivors.

Record results on the PR **`Gates:`** line (see `docs/shared/ub-mode-practice.md`). Implementer fixes crapper/dryer flags before PR; mutator on laptop/CI. Reviewer confirms **`ub-gates`** at head SHA only. Gate debt on the **`Gates:`** line does not block APPROVE in advisory mode; red/missing **`ub-gates`** is a gate miss (hand back, not a review round).

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

*Last updated: 2026-10-25 | Hub version: 0.13.1*
