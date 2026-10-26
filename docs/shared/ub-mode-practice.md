# ub-mode practice (hub)

Use **`/ub-mode`** or load `skills/ub-mode/SKILL.md` when you want the reduced loop: Make it Work, Make it Right, Practice. It complements `plan-code-review-workflow` and does not replace TDD (`write-tests`).

## Advisory vs blocking

**Advisory (hub default):** Run gates when practical, report honest measured results, and put them on the PR **`Gates:`** line. Findings **do not** block APPROVE and **do not** count as review rounds. **Blocking mode** starts only after Tom explicitly approves switching ub-mode to blocking gates.

## When to use

| Situation | Use ub-mode |
| --- | --- |
| Implementing a feature or fix in a supported language | Yes — phases 1–3 |
| PR review | Yes — advisory gate report (Step 3.5 / Phase 2.75) |
| Docs-only or Markdown hub skill edit | Phase 1 judgment only; `Gates: N/A (hub Markdown)` |
| Whole-repo audit | No — use `codebase-simplification-audit` |

## PR body header (hub PRs)

When the hub defines PR body fields, use this **order** at the top of the description (adapt values per PR):

```text
Tier: T0
Models: composer-2.5
Linear: https://linear.app/gman-personal-projects/issue/GMA-412
Summary: one short paragraph
Gates: crapper/dryer/mutator advisory results or skip reason
```

Use `Linear: N/A` when there is no tracking issue. Tier meanings: see **Tier scale** in `docs/shared/repo-standards-practice.md` (T0 small/docs/check-only through T3 infra/migration/new service).

Then add verification evidence (commands + exit codes) and any checklist aligned with CI.

**Linear line:** Must be an `https://linear.app/...` issue URL, or `N/A`. Never use a Cursor store path, box path, or sketch link. Do not use angle-bracket placeholders in committed examples.

For hub Markdown-only PRs, use `Gates: N/A (hub Markdown)`.

The same stanza appears in `skills/technical-writing/SKILL.md`, `skills/lfg/SKILL.md`, `skills/multi-harness-coordination/SKILL.md`, `skills/split-branch-for-pr/SKILL.md`, and `skills/adversarial-coordination-workflow/SKILL.md`.

## Pre-PR dev loop (optional)

Before the full phase 2 gate block (or before opening a PR in `lfg`), you may run a **quick advisory** subset when crapper and dryer are on PATH:

1. `rm -f .metrics/dry.edn`
2. `crapper --changed --threshold 10`
3. `dryer --changed --threshold 0.8`

Fix what you choose; record measured results on the PR **`Gates:`** line. This does not replace mutator when you run the full ub-mode phase 2 block.

## How tools pair with principles

| Tool | Enforces (principle names) |
| --- | --- |
| **write-tests** + your test runner | test-behavior-not-implementation, prove-it-works |
| **crapper** | fix-root-causes on complexity risk; sequence-verifiable-units per function |
| **dryer** | subtract-before-you-add on duplicate structure |
| **mutator** | test-behavior-not-implementation; prove-it-works on surviving mutants |
| **uml-viewer** | Optional picture of `.metrics/` for humans |

Definitions of principle names live only in `skills/pstack-principles/SKILL.md`.

## Evidence to report (advisory)

1. Test command and exit code.
2. **crapper**: worst CRAP ≤ 10 or the exceeding value (`.metrics/crap.edn` or stdout).
3. **dryer**: delete `.metrics/dry.edn` before run (GMA-411); if file missing after `--changed` with no selection, say **no selection/skipped**; else list `:candidates` with `:score` ≥ 0.8.
4. **mutator**: exit `0` / `2` / `3` (survivors) and `.metrics/mutate/`.
5. Skip reasons when a tool is not installed.

Summarize on the PR **`Gates:`** line. In advisory mode, missing gate data is not an APPROVE blocker.
