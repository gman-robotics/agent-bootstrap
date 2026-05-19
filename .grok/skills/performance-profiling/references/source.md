# performance-profiling.md — Performance Investigation Skill

**Purpose**  
A disciplined workflow for finding and fixing performance bottlenecks. Prevents premature optimization by requiring measurement before any code change.

**When to Use**
- A specific user-facing operation is measurably slow
- A background job queue is building backlog
- A database query is causing timeouts or high CPU
- A UI component is re-rendering excessively
- Monitoring shows elevated p95/p99 latency or memory spikes

---

## The Principle

> **Measure first. Change one thing. Measure again. Never optimize without a before/after number.**

Profiling without a baseline is guessing. A 50% improvement on a 10ms path is noise. Find the path that is 2000ms.

---

## Phase 1: Define the Target

Before touching any tooling, answer these questions:

1. **What is the specific operation?** (e.g., "POST /api/documents/bundle takes 8s on avg", "Bull job `generate-pdf` takes 45s", "Dashboard page render takes 4s on client")
2. **What is the current measurement?** (p50, p95, or a specific recorded time)
3. **What is the acceptable target?** (e.g., "under 2s", "queue drains in <1 min")
4. **Is this a regression or always been slow?** If a regression: use `git bisect` (see `debug-investigation.md`) to find the introducing commit before profiling.

---

## Phase 2: Measure the Baseline

Do not change any code during this phase. Only observe.

### Node.js / Express — Request Timing
```bash
# Quick timing without code changes
curl -w "\nTotal: %{time_total}s\n" -X POST http://localhost:3000/api/endpoint -d '{...}'
```

Add coarse timing spans around suspected slow sections:
```typescript
const t0 = performance.now()
const result = await suspectedSlowFunction()
console.log(`suspectedSlowFunction: ${(performance.now() - t0).toFixed(1)}ms`)
```

For production-like profiling, use `clinic.js`:
```bash
npx clinic doctor -- node src/server.js
# Run your slow request, then Ctrl-C. Opens an HTML report.

npx clinic flame -- node src/server.js
# Generates a flame graph — find the wide bars (CPU time)
```

Or use the built-in inspector:
```bash
node --inspect src/server.js
# Open chrome://inspect → Profiler → Start → run the slow operation → Stop
# Look for self-time in the flame chart
```

### MySQL — Query Performance
```sql
-- Step 1: identify the slow query
EXPLAIN ANALYZE
  SELECT <your slow query here>;

-- Read the output:
--   "actual time=X..Y" → Y is total ms for that node
--   "rows=N" vs "rows estimated=M" → large mismatch = bad statistics or missing index
--   "Seq Scan" on a large table → likely missing index

-- Step 2: check for missing indexes
SHOW INDEX FROM table_name;

-- Step 3: profile at the application layer
-- Log query time in your ORM/query builder and dump slow queries (>200ms) to console
```

Enable slow query log for persistent monitoring:
```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 0.2;   -- log queries over 200ms
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';
```

### Background Job Queues — Backlog Analysis
```typescript
const counts = await queue.getJobCounts()
console.log(counts)
// { waiting: N, active: N, completed: N, failed: N, delayed: N }

// Time a single job end-to-end
queue.on('completed', (job, result) => {
  console.log(`Job ${job.id} took ${Date.now() - job.timestamp}ms`)
})
```

Common your queue library bottlenecks:
- **Concurrency too low**: increase `{ concurrency: N }` in `queue.process()`
- **Worker doing synchronous CPU work**: move CPU-intensive work to a worker thread or separate process
- **DB queries inside the worker**: batch them or cache upstream

### React — Render Performance
```bash
# Build with profiling enabled
REACT_APP_PROFILE=true npm run build
```

In browser:
1. Open React DevTools → Profiler tab → Record
2. Perform the slow interaction
3. Stop recording
4. Look for components with high "render duration" or excessive re-render counts

Quick checks without DevTools:
```typescript
// Wrap suspected expensive component
import { memo } from 'react'
export default memo(ExpensiveComponent)

// Check why a component re-renders
import { useWhyDidYouUpdate } from 'ahooks'  // or console.log in useEffect
```

### Python
```bash
# Profile a function
python -m cProfile -s cumulative your_script.py | head -30

# Or use py-spy for a running process (no code changes needed)
pip install py-spy
py-spy top --pid <process-id>
py-spy record -o profile.svg --pid <process-id>
```

For ONNX inference latency:
```python
import time
t0 = time.perf_counter()
result = model.run(None, {"input": tensor})
print(f"ONNX inference: {(time.perf_counter() - t0) * 1000:.1f}ms")
```

---

## Phase 3: Identify the Bottleneck

After measuring, classify the bottleneck:

| Type | Symptoms | Typical fix |
|---|---|---|
| **N+1 query** | Many small fast queries in a loop | Batch with `WHERE id IN (...)` or eager-load |
| **Missing index** | Seq Scan on large table, high `actual time` | Add index on the filtered/joined column |
| **Unnecessary work** | Same computation repeated in a hot path | Cache the result (in-memory, Redis, or memoize) |
| **Synchronous I/O blocking event loop** | Node.js event loop lag, high latency on unrelated requests | Move to async or offload to a queue |
| **Over-fetching** | DB returns 50 columns, you use 3 | `SELECT` only needed columns |
| **Memory pressure / GC pauses** | Spiky latency, high GC in clinic.js doctor | Check for large object allocations in hot paths |
| **React over-rendering** | Component renders on every parent state change | `React.memo`, `useMemo`, `useCallback` at the boundary |

---

## Phase 4: Fix One Thing

1. Make exactly one change targeting the identified bottleneck.
2. Write or update a test that validates the behavior is unchanged (correctness first).
3. Measure again using the same method as Phase 2.
4. Record before/after numbers.

If the improvement is not meaningful (< 20% on a path that matters), reconsider whether this bottleneck is actually the constraint. Return to Phase 3.

---

## Phase 5: Document & Monitor

1. Add a comment near the fix explaining what the bottleneck was and why the fix works.
2. If the fix involved a DB index:
   ```sql
   -- Document the index in docs/projects/<name>/data-models.md
   CREATE INDEX idx_documents_owner_id ON documents(owner_id);
   ```
3. Set up a CloudWatch alarm or log-based metric if this is a path that should stay fast.
4. Update `memory-bank/progress.md` with what was profiled and what was found.

---

## CloudWatch — Production Monitoring

For operations already in production, check CloudWatch before profiling locally:
```bash
# Get p99 latency for an API path over the last hour
aws cloudwatch get-metric-statistics \
  --namespace YourApp/API \
  --metric-name RequestLatency \
  --dimensions Name=Path,Value=/api/your-endpoint \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics p99
```

---
