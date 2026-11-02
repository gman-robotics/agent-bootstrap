# Blocking ub-gates CI job

GitHub Actions job **`ub-gates`** in `.github/workflows/test.yml` runs unclebob gates in **blocking** mode on every push and pull request. It uses the composite action `.github/actions/ub-gates` with `advisory: "0"` and merge-base scope against the PR base ref (or `origin/main` on push).

## Sub-features

- `blocking-action` — `run_ub_gates_ci.sh` with default `UB_GATES_ADVISORY=0`; fails on findings in scope, `tool_error`, and non-scope skips (including `skipped_mutator`).
- `crapper-contract` — `tests.test_ub_crapper_contract` with `UB_REQUIRE_CRAPPER=1`.
- `gate-fixture-meta-test` — `tests.test_ub_gate_pairs` with `UB_REQUIRE_GATE_TOOLS=1` (GMA-488 known-bad/known-good pairs per gate).

## How to get to it (user POV)

- Open a PR against `main`; wait for the **ub-gates** check on GitHub (local parity requires `crapper`, `dryer`, `mutator`, and `coverage` on PATH plus full git history for merge-base).

## Driving it with verify-hub

Preconditions:

- Dev requirements installed.
- Gate tools on PATH when reproducing the meta-test locally (`which crapper dryer mutator`).
- Not a substitute for `verify-hub-ci` — this job is CI-only; local agents use advisory `run_ub_gates_report.sh` inside `verify-hub-ci` unless explicitly running blocking mode.

- **Meta-test only (fast gate sanity).** From repo root:

```bash
UB_REQUIRE_GATE_TOOLS=1 python3 -m unittest tests.test_ub_gate_pairs
```

Expect exit `0` when tools are present; skipped tests when tools are missing unless `UB_REQUIRE_GATE_TOOLS=1`.

- **Blocking dry-run (optional, slow).** With tools installed and a meaningful scope:

```bash
UB_GATES_ADVISORY=0 UB_GATES_BASE_REF=origin/main bash scripts/run_ub_gates_ci.sh
```

Expect exit `0` on clean merge-base scope; non-zero on findings or `skipped_mutator` in blocking mode.

- **Proof.** Capture unittest footer for meta-test; capture `.metrics/ub-gates-outcome.txt` and exit code for blocking dry-run.

## Gotchas

- Do not weaken or restructure the `ub-gates` job when extending CI — add verify steps elsewhere (the **`verify-hub`** job already runs `verify-hub-ci`).
- Mutator budget timeout is reported but does not fail blocking CI the same way `skipped_mutator` does; read step summary when mutator hits the budget.
- Fixture pairs live under `tests/fixtures/ub_gate_pairs/`; changing gate CLI behavior requires updating fixtures and this meta-test.
