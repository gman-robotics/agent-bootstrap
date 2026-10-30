# ub-mode — quality gates by language

Run these from the **project root** after tests pass. Install each tool once per machine (each repo ships a `./crapper`, `./dryer`, or `./mutator` wrapper that creates a local `.venv` on first run). Do not invent substitutes; if the binary is missing, say so and skip that gate with evidence.

**Hub mode:** Dryer, crapper, and mutator are **blocking** by default. `scripts/run_ub_gates_ci.sh` defaults to `UB_GATES_ADVISORY=0`. Advisory mode is only `scripts/run_ub_gates_report.sh` or an explicit `UB_GATES_ADVISORY=1`. Scope is changed functions (crapper) and changed lines (dryer, mutator). Test paths, `.pyi`, and `.d.ts` are out of scope. Debt in untouched old functions does not block. There is no waiver: fix blocking findings on changed code, or escalate them to the CoS. A red `ub-gates` check does **not** count as a review round.

All six languages below are supported by the unclebob tools when the project has the usual test and coverage tooling for that stack.

## Shared thresholds (hub default)

| Gate | Tool | Clean result to report | Snapshot |
| --- | --- | --- | --- |
| CRAP | `crapper` | worst function **CRAP ≤ 10** (`--threshold 10` fails only when worst **&gt; 10**) | `.metrics/crap.edn` |
| Duplication | `dryer` | read `.metrics/dry.edn` from **this** run: no `:candidates` with `:score` **≥ 0.8** | `.metrics/dry.edn` |
| Mutation | `mutator` | exit `0`; exit `2` baseline tests failed; exit `3` **survivors** | `.metrics/mutate/*.edn` |

### GMA-411 — dryer hygiene

- **Delete** `.metrics/dry.edn` before every dryer run (`rm -f .metrics/dry.edn`).
- Upstream **`--changed`** uses **`git status`** (uncommitted files), not the PR diff. For committed branches and CI, pass an explicit path list from `git diff merge-base...HEAD` (see `docs/shared/ub-mode-practice.md`).
- `dryer --changed` with an **empty** `git status` selection exits `0` and does **not** refresh the snapshot; a stale file may remain if you skip the delete step.
- If `.metrics/dry.edn` is **missing** after the run, report **no selection / skipped** — never treat a pre-run file as evidence.
- Default size filters: **4 lines** (`--min-lines`) and **20 nodes** (`--min-nodes`) unless you override.

### Reading `.metrics/dry.edn`

Dryer writes EDN shaped like `{:candidates [{:score 0.89 :language "clojure" :left {...} :right {...}} ...]}`. Report every candidate with `:score` ≥ 0.8. Dryer exit `0` does not mean “clean”.

## Commands (any supported language in the tree)

```bash
# PR / branch scope (committed diff — preferred for CI and pre-PR)
./path/to/crapper --threshold 10 path/to/changed.py ...
rm -f .metrics/dry.edn && ./path/to/dryer --threshold 0.8 path/to/changed.py ...
./path/to/mutator path/to/changed.py ...

# Uncommitted edits only (git status — upstream --changed)
./path/to/crapper --changed --threshold 10
rm -f .metrics/dry.edn && ./path/to/dryer --changed --threshold 0.8
./path/to/mutator --changed

# Full tree (release or wide refactor)
./path/to/crapper --threshold 10
rm -f .metrics/dry.edn && ./path/to/dryer --threshold 0.8
./path/to/mutator
```

Point `./path/to/` at your checkout of each tool repo, or put the wrappers on `PATH`. **mutator** expects **crapper** checked out beside it (`../crapper`) for namespace names.

### Clojure

| Gate | Notes |
| --- | --- |
| crapper | When `deps.edn` or `bb.edn` exists, runs `clj -M:cov --lcov` (tool checks the file exists; `:cov` alias must be defined for coverage) |
| dryer | Top-level forms except `ns` (dry4clj lineage) |
| mutator | clj-mutate lineage; per-ns `.edn` under `.metrics/mutate/` |

### Java

| Gate | Notes |
| --- | --- |
| crapper | JaCoCo `INSTRUCTION` from Maven `pom.xml` modules |
| dryer | Methods with a body only; **constructors excluded**; no methods inside anonymous or local classes |
| mutator | mutate4java lineage |

### Go

| Gate | Notes |
| --- | --- |
| crapper | `go test ./... -coverprofile=...` |
| dryer | Functions and methods with a body; function literals stay inside the enclosing function |
| mutator | mutate4go lineage |

### TypeScript (dryer: `.ts`, `.tsx`, `.mts`, `.cts` only)

| Gate | Notes |
| --- | --- |
| crapper | Also analyzes `.js`, `.jsx`, `.mjs`, `.cjs`; LCOV; Vitest may auto-install `@vitest/coverage-v8` |
| dryer | **TypeScript files only**; functions, methods, and top-level arrow functions; nested callbacks stay in the parent; **no** Express route callback entries |
| mutator | Java-style mutation rules in TS syntax |

### Rust

| Gate | Notes |
| --- | --- |
| crapper | `cargo llvm-cov` or `cargo tarpaulin` LCOV |
| dryer | Functions and methods with a body; skips `mod tests` and closures |
| mutator | Rust uses the **Java** mutation set (mutate4java: `&&`/`||`, delete `!`, unary `-`); LCOV only to skip uncovered lines |

### Python

| Gate | Notes |
| --- | --- |
| crapper | `coverage.py` + pytest or unittest |
| dryer | Functions and methods; nested functions stay inside the enclosing function |
| mutator | Functions and methods; nested defs stay inside the parent |

## When a gate cannot run

| Situation | Action |
| --- | --- |
| Tool not installed | Record "gate skipped: &lt;tool&gt; not on PATH" on the PR `Gates:` line |
| Project language not in the six | State plainly; do not fake a gate |
| Baseline tests fail | Fix tests first; mutator exit `2` means baseline failure |
| Advisory mode | Only `scripts/run_ub_gates_report.sh` or explicit `UB_GATES_ADVISORY=1`. Findings and **`skipped_tools_missing`** then exit 0 with a warning — **`gates_ran=0`** is not a pass. A direct `scripts/run_ub_gates_ci.sh` call defaults to blocking (`UB_GATES_ADVISORY=0`) |
| Blocking mutator skip | `UB_GATES_SKIP_MUTATOR=1` or `CURSOR_AGENT` without `GITHUB_ACTIONS` is outcome **`skipped_mutator`** and exits 1. It is not `ran_clean` |
| Untouched old functions | Findings and debt outside changed functions (crapper) or changed lines (dryer, mutator) do not block |
| No waiver | Blocking findings on changed code are fixed, or escalated to the CoS |
| Local run | Throwaway `--rm` container, no host installs. Usage: `Usage: bash scripts/ub_gates_container.sh [--help] [--worktree PATH] [--main-git PATH] [--metrics-dir PATH]` |
| Declaration files | `.pyi` and `.d.ts` are outside gate scope (no function bodies). Test paths are outside gate scope |
| Mutator budget | 20-minute per-PR cap. A timeout is reported and leads the step summary. A timeout does not block |
| Dryer exit | Exit 0 with a fresh `.metrics/dry.edn` is the only dryer success. Exit 1, 2, or any other code is `tool_error` even when that file exists |
| Base ref | Fetch `UB_GATES_BASE_REF` with no depth limit and unshallow a shallow clone. A missing merge base is `tool_error` |

## uml-viewer (optional)

[uml-viewer](https://github.com/unclebob/uml-viewer) reads `.metrics/crap.edn` and `.metrics/mutate/*.edn` for coverage, CRAP, and mutation paint. Use it when a human wants a picture.
