# write-tests.md — Test Writing Skill

**Purpose**  
Operational playbook for applying the team TDD standard during a session. Use this whenever writing new tests, fixing bugs, or adding coverage to existing code.

**Read first**: `docs/shared/tdd-standard.md` — the authoritative rules on when TDD is required and the mock discipline policy.

**When to Use This Skill**
- Starting any new feature, bug fix, or refactor (always before writing production code)
- When a PR review flags missing or insufficient tests
- When adding coverage to untested legacy code

---

## Step 1: Orient

1. Confirm the active project and its test framework:

   | Project | Framework | Run command |
   |---|---|---|
   | Node.js/TypeScript project | Jest | `npm test` or `npm test -- --watch` |
   | Bun/TypeScript project | Bun test | `bun test` |
   | Python project | pytest | `pytest` |

2. Run the full suite. It must be **green** before you start. If it is red, fix or flag existing failures first.

---

## Step 2: Write the Failing Test (Red)

1. Identify the single next behavior to implement or cover.
2. Write one test asserting that behavior. Follow the naming rule: `[subject] [condition] [expected outcome]`.
3. Run only that test:
   ```bash
   # Jest
   npx jest --testNamePattern="your test description"
   # Bun
   bun test --filter "your test description"
   # pytest
   pytest -k "your test description"
   ```
4. Confirm it **fails with an assertion error** — not an import error or syntax error. An import error means your test file is broken, not that TDD is working.

**Do not write any production code until the test is red and failing for the right reason.**

---

## Step 3: Make It Pass (Green)

1. Write the minimum production code to make the failing test pass.
2. Run the single test to confirm it goes green.
3. Run the full suite to confirm nothing regressed.
4. If the suite goes red, fix the regression before moving on — do not leave a broken suite.

---

## Step 4: Refactor

1. Review the production code. Remove duplication, clarify names, simplify conditionals.
2. Review the test itself — is the name precise? Is the assertion testing behavior or internals?
3. Run the full suite after each meaningful change.
4. Stop when the code is clean. Do not add behavior during refactor.

---

## Step 5: Repeat

Return to Step 2 for the next behavior. When all required behaviors are covered, the feature is complete.

---

## Retrofitting Tests on Legacy Code

When adding tests to untested existing code:

1. **Do not refactor first.** Untested code is fragile — you need a safety net before touching it.
2. Write a **characterization test** that documents current behavior, even if that behavior is incorrect.
3. Once the characterization test is green, you have a safety net. Refactor from there.
4. Fix bugs in separate commits from refactors — it makes the history readable.

---

## Extraction Refactors Need Characterization-First + Parity QA

This applies to **every** extraction refactor (pulling a hook, helper, or service out of existing code) — not just legacy code. A spec-compliant extraction can still silently change behavior the spec never mentioned.

> Field lesson (polling-hook extraction): the first cut satisfied the written spec but broke two subtle behaviors — the old content stayed visible during regenerate in the original, and the original made 21 requests (initial + 20 retries) where the extraction made 20. Only a behavior-by-behavior comparison against the original caught both.

1. **Before extracting**: write characterization tests against the **original** code covering every observable behavior — including the unglamorous ones: exact request counts, what stays visible during loading/error states, cleanup ordering, abort/supersession sequencing, timer behavior.
2. Extract. The characterization tests must stay green against the new structure.
3. **Parity QA pass**: a reviewer (or QA agent) explicitly compares new vs. original side by side, asking "what does the original do that no test asserts?" — the gaps found become new characterization tests, not review comments.
4. Off-by-one counts (N vs N+1 attempts), state-visibility-during-transition, and effect-dependency staleness are the three most common silent breaks — check them by name.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Writing the test after the code | Always write the failing test first. If you can't, the behavior is not yet defined — clarify it. |
| Test passes immediately | Either the feature already exists or the test is wrong. Investigate before moving on. |
| Testing implementation details | If the test breaks on a private variable rename, it is testing implementation. Rewrite to assert observable output. |
| One massive test per function | One test per behavior. Multiple small focused tests beat one large one. |
| Mocking the subject under test | You are testing nothing. Remove the mock. |
| Skipping refactor phase | Unrefactored green code becomes legacy debt within one sprint. |

---

## Test Structure Reference

```typescript
// Jest / Bun (TypeScript)
describe("DocumentService", () => {
  describe("getDocument", () => {
    it("returns the document when it exists", async () => {
      // Arrange
      const doc = await factory.createDocument()
      // Act
      const result = await service.getDocument(doc.id)
      // Assert
      expect(result.id).toBe(doc.id)
    })

    it("throws NotFoundError when the id does not exist", async () => {
      await expect(service.getDocument("nonexistent")).rejects.toThrow(NotFoundError)
    })

    it("throws AuthorizationError when user lacks read access", async () => {
      const doc = await factory.createDocument({ ownerId: "other-user" })
      await expect(service.getDocument(doc.id, { userId: "attacker" })).rejects.toThrow(AuthorizationError)
    })
  })
})
```

```python
# pytest (Python)
class TestDocumentClassifier:
    def test_classifies_text_page_as_safe_when_no_images(self, classifier):
        result = classifier.classify(page_text="long enough text " * 10, has_images=False)
        assert result.verdict == "safe"

    def test_routes_image_page_to_vision_worker(self, classifier):
        result = classifier.classify(page_text="short", has_images=True)
        assert result.routed_to == "docuvision"
```

---
