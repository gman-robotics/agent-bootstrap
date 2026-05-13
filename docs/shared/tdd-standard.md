# TDD Standard — Red/Green/Refactor

> **Scope**: Team-wide. Applies to all projects in manifest.yaml.  
> For project-specific test tooling, see `docs/projects/<name>/`.

---

## The Rule

**All non-trivial logic must be developed using Red/Green/Refactor TDD.**

This is a global standard, not a suggestion. The QA Reviewer role in `plan-code-review-workflow.md` must flag new logic shipped without tests as a blocking issue.

---

## The Cycle

```
RED      → Write a failing test that defines exactly one behavior.
GREEN    → Write the minimum code to make it pass. Nothing more.
REFACTOR → Clean up without changing behavior. Tests stay green.
```

One cycle = one unit of behavior. Repeat until the feature is complete.

---

## When TDD Is Mandatory

| Situation | Requirement |
|---|---|
| New business logic | Full Red/Green/Refactor |
| Bug fix | Write a failing test that reproduces the bug *before* fixing it |
| Refactor of existing code | Tests must exist and stay green throughout; write them first if absent |
| New API endpoint or queue handler | Integration test covering happy path + at least one error case |
| Database migration | Test runs cleanly on a real schema in CI |
| Utility/helper function | Unit test; skip only if it is a pure pass-through with zero logic |

## When TDD May Be Skipped

- Glue code with no logic (config wiring, index re-exports, type-only files)
- One-off scripts explicitly labeled as throw-away tooling
- Pure UI layout with no conditional rendering logic
- Prototype/spike work — but the spike **must be deleted**, not promoted to production directly

---

## Red Phase Rules

1. Run the full test suite before starting. It must be green.
2. Write exactly one test for the next behavior.
3. Run it. It **must fail** — if it passes immediately, the test is wrong or the behavior already exists.
4. Do not write any production code until step 3 is confirmed.

## Green Phase Rules

1. Write the **minimum** code that makes the failing test pass.
2. Hardcoding a return value is acceptable in green phase — it is not cheating.
3. Do not refactor yet. Do not add error handling not driven by a test.
4. Run the full suite. All tests must pass before moving to refactor.

## Refactor Phase Rules

1. Remove duplication. Improve names. Simplify logic.
2. Do not change behavior — tests must stay green throughout.
3. Run the suite after every non-trivial change.
4. Stop when the code is clean. Do not add features during refactor.

---

## Test Naming

Tests must describe behavior, not implementation:

```
✓  "returns 404 when document does not exist"
✓  "throws AuthorizationError when user lacks read permission"
✗  "test getDocument error branch"
✗  "testGetDocumentError"
```

Pattern: **`[subject] [condition] [expected outcome]`**

---

## Mocking Discipline

| Dependency | Approach |
|---|---|
| Pure in-process logic | No mocks — test directly |
| Database (MySQL) | Use a real test DB; do not mock the ORM |
| External HTTP APIs | Mock the HTTP client at the network boundary |
| AWS SDK (S3, SES, SNS, Pinpoint) | Mock `@aws-sdk/client-*` at the call site |
| Bull queue workers | Test the worker handler directly; test the producer separately |
| RabbitMQ | Mock the channel in unit tests; use a real broker for integration tests |
| File system | Use tmp directories; avoid mocking `fs` |

---

## CI Enforcement

- All projects must have a `test` script (or `make test` / `pytest`).
- CI must fail on any test failure.
- Coverage is a signal, not a target. A 60% suite with behavioral tests beats 100% with assertions on internal variables.

---

## Relationship to Other Standards

- **`skills/write-tests.md`** — operational playbook for applying this standard session-by-session.
- **`skills/plan-code-review-workflow.md`** — QA Reviewer verifies TDD compliance in every review.
- **`docs/shared/decisions.md` ADR-003** — decision record for adopting this standard.

---

*Last updated: 2026-04-30 | Exceptions require an ADR entry in `docs/shared/decisions.md`*
