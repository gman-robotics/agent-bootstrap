# debug-investigation.md — Systematic Debugging Skill

**Purpose**  
A disciplined workflow for diagnosing bugs. Replaces ad-hoc guessing with a repeatable process that produces a test before a fix.

**When to Use**
- Any bug report or unexpected behavior
- Flaky test investigation
- Production incident root-cause analysis (pair with `incident-response.md` if one exists)

---

## The Principle

> **Never fix what you cannot reproduce. Never merge a fix without a failing test.**

A fix without a test will regress. A fix without a reproduction is a guess.

---

## Phase 1: Reproduce

**Goal**: Get a reliable, local reproduction before touching any code.

1. Read the bug report carefully. Identify:
   - What was expected
   - What actually happened
   - Environment (dev / staging / prod), inputs, user account if relevant
2. Attempt to reproduce locally with the exact inputs described.
3. If you cannot reproduce it:
   - Check environment-specific config (`.env`, feature flags, DB seed state)
   - Check logs from the reported environment (`CloudWatch`, `stdout`, `Bull` job logs)
   - Ask the user for a specific reproduction case before proceeding
4. **Do not proceed past this phase until you have a reliable local reproduction.**

---

## Phase 2: Isolate

**Goal**: Narrow the faulty code to the smallest possible unit.

### Strategy A — Binary Search (git bisect)
Use when the bug is a regression and you know a commit that worked:
```bash
git bisect start
git bisect bad                          # current commit is broken
git bisect good <last-known-good-sha>   # this commit worked
# git will check out midpoints; test each one, then:
git bisect good   # or: git bisect bad
# repeat until git identifies the introducing commit
git bisect reset
```

### Strategy B — Code Path Narrowing
Use when the bug is in a known area:
1. Identify the entry point (HTTP handler, queue worker, scheduled job, CLI command).
2. Add a temporary `console.log` or `logger.debug` at the entry point to confirm the code is reached.
3. Binary-search down the call stack — log at the midpoint, then narrow to the half where behavior diverges.
4. Stop when you can point to a specific function or line.

### Strategy C — Data Isolation
Use when the bug is data-dependent:
1. Reproduce with the minimal dataset. Remove fields/rows/records until the bug disappears — the last thing you removed is relevant.
2. For MySQL: run the failing query directly in a DB client with `EXPLAIN ANALYZE` to check for unexpected scans or nulls.

---

## Phase 3: Write a Failing Test

Before writing any fix:
1. Write a test that:
   - Sets up the exact conditions of the reproduction
   - Calls the isolated unit
   - Asserts the expected (correct) behavior
2. Run it. It must fail, matching the observed bug.
3. If the test passes, your isolation is wrong — the bug lives elsewhere. Return to Phase 2.

This test is your proof that you found the right place and your safety net that the fix works.

---

## Phase 4: Fix

1. Write the minimum change that makes the failing test pass.
2. Run the full test suite. Fix any regressions before continuing.
3. Manually verify the original reproduction case is gone.

---

## Phase 5: Verify & Close

1. Run the full suite one more time.
2. Check edge cases adjacent to the fix (what happens with nulls, empty arrays, concurrent calls?).
3. Remove all temporary `console.log` / debug instrumentation.
4. Write a short commit message explaining *why* the bug occurred, not just what changed.
5. Update `memory-bank/progress.md` if this was a significant bug.

---

## Stack-Specific Tips

### Node.js / Express
```bash
# Attach inspector to a running process
node --inspect src/server.js
# Open chrome://inspect in Chrome → Sources → set breakpoints
```
- For async bugs: check whether `await` is missing or `Promise` is unhandled.
- For middleware bugs: log `req.headers`, `req.body`, and `res.locals` at the entry of each middleware in the chain.

### Background Job Queues (e.g. Bull)
- Jobs that silently disappear: check `queue.on('failed')` handler — errors in workers are swallowed by default if no handler is registered.
- Check `queue.getJobCounts()` to see if jobs are stuck in `delayed`, `waiting`, or `active`.
- Reproduce by calling the worker handler function directly in a test rather than through the queue.

### MySQL
```sql
-- Always run EXPLAIN ANALYZE on slow or incorrect queries
EXPLAIN ANALYZE SELECT ...;
-- Check for NULL propagation bugs
SELECT COALESCE(col, 'default') FROM table WHERE col IS NULL;
```

### Python
```bash
# Run with verbose output
pytest -s -v -k "failing test name"
# Drop into pdb on failure
pytest --pdb
```

### React / Frontend
- Use React DevTools → Components tab to inspect prop values at the render that fails.
- For state bugs: add a `useEffect(() => { console.log(state) }, [state])` to trace state transitions.
- For hydration mismatches: check whether server and client render different markup on first paint.

---

## Anti-Patterns to Avoid

| Anti-pattern | Why it fails |
|---|---|
| Fixing before reproducing | You are guessing. The fix may mask rather than resolve the bug. |
| Adding logs without a hypothesis | You will drown in output. Form a hypothesis first, then verify it. |
| Fixing without a test | The bug will regress. Always write the failing test first. |
| Changing multiple things at once | You will not know which change fixed the bug. One change at a time. |
| Deleting the reproduction case after fixing | Keep it as a test. The reproduction *is* the test. |

---
