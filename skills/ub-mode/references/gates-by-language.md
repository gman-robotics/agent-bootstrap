# ub-mode — quality gates by language

Run these from the **project root** after tests pass. Install each tool once per machine (each repo ships a `./crapper`, `./dryer`, or `./mutator` wrapper that creates a local `.venv` on first run). Do not invent substitutes; if the binary is missing, say so and skip that gate with evidence.

All six languages below are supported by the unclebob tools when the project has the usual test and coverage tooling for that stack.

## Shared thresholds (hub default)

| Gate | Tool | Pass when | Snapshot |
| --- | --- | --- | --- |
| CRAP | `crapper` | worst function **CRAP ≤ 10** (`--threshold 10` fails only when worst **&gt; 10**) | `.metrics/crap.edn` |
| Duplication | `dryer` | read `.metrics/dry.edn` after a successful run: **no** `:candidates` entry with `:score` **≥ 0.8** (dryer exits `0` even when pairs meet the threshold) | `.metrics/dry.edn` |
| Mutation | `mutator` | exit `0` (no surviving mutants) | `.metrics/mutate/*.edn` |

### Reading `.metrics/dry.edn`

Dryer writes EDN shaped like `{:candidates [{:score 0.89 :language "clojure" :left {...} :right {...}} ...]}`. Treat any candidate with `:score` ≥ 0.8 as a duplication gate failure, regardless of dryer exit code.

## Commands (any supported language in the tree)

```bash
# Changed files only (typical before APPROVE on a PR)
./path/to/crapper --changed --threshold 10
./path/to/dryer --changed --threshold 0.8
./path/to/mutator --changed

# Full tree (release or wide refactor)
./path/to/crapper --threshold 10
./path/to/dryer --threshold 0.8
./path/to/mutator
```

Point `./path/to/` at your checkout of each tool repo, or put the wrappers on `PATH`. **mutator** expects **crapper** checked out beside it (`../crapper`) for namespace names.

### Clojure

| Gate | Notes |
| --- | --- |
| crapper | Cloverage LCOV via `clj -M:cov --lcov` when `deps.edn` or `bb.edn` defines `:cov` |
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
| dryer | **TypeScript files only** (`.ts`, `.tsx`, `.mts`, `.cts`); compares functions, methods, and top-level arrow functions; callbacks nested inside another function stay in the parent; **no** separate Express route callback entries |
| mutator | Java-style mutation rules in TS syntax |

### Rust

| Gate | Notes |
| --- | --- |
| crapper | `cargo llvm-cov` or `cargo tarpaulin` LCOV |
| dryer | Functions and methods with a body; skips `mod tests` and closures |
| mutator | LCOV from llvm-cov/tarpaulin |

### Python

| Gate | Notes |
| --- | --- |
| crapper | `coverage.py` + pytest or unittest |
| dryer | Functions and methods; nested functions stay inside the enclosing function |
| mutator | Functions and methods; nested defs stay inside the parent |

## When a gate cannot run

| Situation | Action |
| --- | --- |
| Tool not installed | Record "gate skipped: &lt;tool&gt; not on PATH" in the PR or review handback |
| Project language not in the six | State plainly; do not fake a gate |
| Baseline tests fail | Fix tests first; mutator exit `2` means baseline failure |
| CRAP &gt; 10, dry candidate ≥ 0.8, or mutator survivor | REQUEST_CHANGES; fix or split until green |

## uml-viewer (optional)

[uml-viewer](https://github.com/unclebob/uml-viewer) reads `.metrics/crap.edn` and `.metrics/mutate/*.edn` for coverage, CRAP, and mutation paint. Use it when a human wants a picture. APPROVE evidence still needs crapper/mutator exit codes (where applicable), **plus** a `.metrics/dry.edn` read for duplication.
