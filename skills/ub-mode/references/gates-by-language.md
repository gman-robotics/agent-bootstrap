# ub-mode — quality gates by language

Run these from the **project root** after tests pass. Install each tool once per machine (each repo ships a `./crapper`, `./dryer`, or `./mutator` wrapper that creates a local `.venv` on first run). Do not invent substitutes; if the binary is missing, say so and skip that gate with evidence.

All six languages below are supported by the unclebob tools when the project has the usual test and coverage tooling for that stack.

## Shared thresholds (hub default)

| Gate | Tool | Pass when | Snapshot |
| --- | --- | --- | --- |
| CRAP | `crapper` | worst function CRAP **&lt; 10** | `.metrics/crap.edn` |
| Duplication | `dryer` | no pair at similarity **≥ 0.8** worth fixing | `.metrics/dry.edn` |
| Mutation | `mutator` | exit `0` (no surviving mutants) | `.metrics/mutate/*.edn` |

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
| dryer | Structural fingerprints on `defn` forms (dry4clj lineage) |
| mutator | clj-mutate lineage; per-ns `.edn` under `.metrics/mutate/` |

### Java

| Gate | Notes |
| --- | --- |
| crapper | JaCoCo `INSTRUCTION` from Maven `pom.xml` modules |
| dryer | Methods and constructors (anonymous inner classes omitted, same as crapper) |
| mutator | mutate4java lineage |

### Go

| Gate | Notes |
| --- | --- |
| crapper | `go test ./... -coverprofile=...` |
| dryer | Package-level functions and methods |
| mutator | mutate4go lineage |

### TypeScript (and `.js` / `.jsx` / `.tsx` / `.mjs` / `.cjs`)

| Gate | Notes |
| --- | --- |
| crapper | LCOV; Vitest projects may auto-install `@vitest/coverage-v8` |
| dryer | Same function units as crapper (including Express route callbacks as named entries) |
| mutator | Java-style mutation rules in TS syntax |

### Rust

| Gate | Notes |
| --- | --- |
| crapper | `cargo llvm-cov` or `cargo tarpaulin` LCOV |
| dryer | Functions and methods (`mod tests` skipped) |
| mutator | LCOV from llvm-cov/tarpaulin |

### Python

| Gate | Notes |
| --- | --- |
| crapper | `coverage.py` + pytest or unittest |
| dryer | Functions and methods; nested defs stay inside the parent |
| mutator | Same units as crapper |

## When a gate cannot run

| Situation | Action |
| --- | --- |
| Tool not installed | Record "gate skipped: &lt;tool&gt; not on PATH" in the PR or review handback |
| Project language not in the six | State plainly; do not fake a gate |
| Baseline tests fail | Fix tests first; mutator exit `2` means baseline failure |
| Survivor or CRAP over threshold | REQUEST_CHANGES; fix or split until green |

## uml-viewer (optional)

[uml-viewer](https://github.com/unclebob/uml-viewer) reads `.metrics/crap.edn` and `.metrics/mutate/*.edn` for coverage, CRAP, and mutation paint. Use it when a human wants a picture; the APPROVE gate only needs the tool exit codes and snapshot paths in the evidence line.
