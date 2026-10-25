# ub-mode practice (hub)

Use **`/ub-mode`** or load `skills/ub-mode/SKILL.md` when you want the reduced loop: Make it Work, Make it Right, Practice. It complements `plan-code-review-workflow` and does not replace TDD (`write-tests`).

## When to use

| Situation | Use ub-mode |
| --- | --- |
| Implementing a feature or fix in a supported language | Yes — phases 1–3 |
| PR review before APPROVE | Yes — phase 2 gate block |
| Docs-only or Markdown hub skill edit | Phase 1 judgment only; skip gates |
| Whole-repo audit | No — use `codebase-simplification-audit` |

## How tools pair with principles

| Tool | Enforces (principle names) |
| --- | --- |
| **write-tests** + your test runner | test-behavior-not-implementation, prove-it-works |
| **crapper** | fix-root-causes on complexity risk; sequence-verifiable-units per function |
| **dryer** | subtract-before-you-add on duplicate structure |
| **mutator** | test-behavior-not-implementation; prove-it-works on surviving mutants |
| **uml-viewer** | Optional picture of `.metrics/` for humans |

Definitions of principle names live only in `skills/pstack-principles/SKILL.md`.

## Evidence for reviewers

A complete gate handback includes:

1. Test command and exit code.
2. Each gate command, exit code, and path to `.metrics/crap.edn`, `.metrics/dry.edn`, or `.metrics/mutate/`.
3. Skip reasons when a tool is not installed.

Do not APPROVE without that line or an explicit "gates not applicable" reason (language or environment).
