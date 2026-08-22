---
name: codebase-simplification-audit
description: "Use when the user wants a whole-repo read-only audit for simpler data structures, state representation, control flow, algorithms, or ownership. Inventory every subsystem, fan out bounded workers (\u22642 material recs or skip), verify, then audit the audit. Do not edit, test, implement, commit, or push until the user accepts a recommendation."
version: 1.0.0
---

# codebase-simplification-audit — Read-only representation audit

**Purpose**
Find *materially simpler* models of data, state, control flow, algorithms, and ownership. Produce a ranked report. Leave the repository unchanged.

Adapted from Aaron Francis’s gist [`audit-your-codebase.md`](https://gist.github.com/aarondfrancis/8735edbe48532f97ee5ea818db4dbd47). This skill is the hub playbook; the gist is provenance, not a second source of steps.

**Trigger**
“Audit this codebase for simplifications”, “codebase simplification audit”, “is our state model too messy?”, or a paste of that gist against a repo.

**Do not use for**
- A bug (“fix X”) → `debug-investigation`
- A planned change / refactor the user already accepted → `plan-code-review-workflow`
- A PR/diff review → `expert-pr-review`
- “Make it faster” with a measured symptom → `performance-profiling`
- Recent-diff cleanup / style → the implementer's own bounded cleanup pass on touched files (see `agents/software-engineer.md` "Cleanup pass"), not a whole-repo audit

---

## Hard rule — no edits until the user accepts

This skill is **audit-only**. Until the user **explicitly accepts** one or more recommendations (names the rec / subsystem / “implement #2”):

1. **Do not** edit files, format, refactor, or “just tidy while I’m here.”
2. **Do not** run tests, implement recommendations, commit, or push.
3. **Do not** invoke `plan-code-review-workflow`, `write-tests`, `task-loop-7-phase`, or any implementer role.
4. **Do not** open a PR, create a branch for the rec, or start TDD “to save time.”
5. Read-only inspection is allowed: `git status`, `git diff` (to prove no mutation), `rg`, file reads, directory listings.

If `git status` is dirtier than when you started, **stop and revert your own changes** before presenting the report.

After accept: stop this skill. Load `plan-code-review-workflow` + `write-tests` for **that slice only**. Then `expert-pr-review`. Optional: `docs-protocol` (ADR), `feature-flag-lifecycle` (risky cutover).

---

## Companions (same job — do not reimplement)

Read and follow; do not copy their playbooks into this file.

| Skill | Role here |
|---|---|
| `subagent-routing` | One worker per subsystem; model tier |
| `delegation-patterns` | Read-only lanes only (no isolated-edit pattern) |
| `agent-orchestration-roles` | You coordinate; workers do not implement |
| `adversarial-coordination-workflow` | Fresh pass for “audit the audit” only — **not** its implement/PR loop |
| `memory-bank-protocol` | Park inventory + ranked recs as **plan**, never as implemented |
| `reply-contract` | Present the report as if the user just switched projects |

Skip a companion if the harness cannot load it. The hard rule still holds.

---

## Words

- **Material** — would make the model easier to reason about, not merely shorter.
- **Skip** — this subsystem is already fine; that *is* completed coverage.
- **Coverage contract** — the inventory. Catch-all rows (“misc”, “the backend”) do not prove coverage.
- **Invalid combination** — flags/nullables that can describe a state the domain forbids.

---

## What to look for (workers)

- Scattered booleans / nullables that permit invalid combinations → state machine or discriminated union
- Repeated object-shape assumptions → shared typed model
- Duplicated branching → small map, registry, reducer, or command model
- Unclear state/behavior ownership → small module boundary
- Repeated scans / transforms / lookups → a more appropriate collection or index
- Lifecycle / concurrency / async representation that can go stale or contradict

**Architectural Review Phases (optional named lens, ownership rows only)**  
For a subsystem row about module boundaries or ownership, a worker may frame findings against these four checklist names (canonical definition in `agents/software-architect.md`; names only — no CRAP/mutation/DRY tooling to install):
1. **UI/Core Separation**
2. **Dependency Rule**
3. **Information Hiding And Encapsulation**
4. **Local Code Quality**
This is a lens for phrasing an existing recommendation, not an extra required pass — do not add rows just to cover all four names.

**Do not recommend**
- Style, naming, import order
- Hypothetical extensibility
- Minor line-count reduction
- Moving existing branching behind a new type with no simpler semantics
- Forced abstractions. Prefer boring local code when it is already clear.

At most **two** opportunities per subsystem. If nothing meets the bar, return `skip`.

---

## Steps

You are the coordinator. Continue until every inventory row is `recommend` or `skip` and the audit-the-audit pass is done.

### 1. Snapshot + coverage contract

Record starting `git status --porcelain` (must be empty of *your* edits at the end).

Inventory every identifiable subsystem. Include frontend, backend, shared infra, platform bridges, generated-contract ownership, and test/tooling when material.

Each row:

| Field | Required |
|---|---|
| Stable ID | e.g. `S-auth` |
| Name | short |
| Ownership boundary | exact; non-overlapping |
| Key files | implementation |
| Interfaces / call sites / tests | if they exist |
| Status | `queued` → `in review` → `recommend` or `skip` |

One canonical scratchpad (memory-bank `progress.md` or a session file the user already uses). Include: inventory, confirmed recs, explicit skips, cross-cuts, duplicates, priorities, audit log.

**Done when:** every identifiable subsystem has a non-catch-all row. If you cannot name a boundary, it is not inventoried.

### 2. Bounded subsystem reviews

Follow `subagent-routing` / `delegation-patterns`. Fresh read-only workers. One distinct, non-overlapping boundary each.

Concurrency ≤ lanes you can actually harvest. One wait mechanism. Do not interrupt slow productive workers. Close workers after harvest.

If the harness has no subagents, walk subsystems sequentially with the same brief and cap.

**Worker brief (give verbatim):**

> Review only this subsystem: `<ID> <name>`. Boundary: `<files / modules>`. Stay inside it. You may *name* a cross-subsystem concern; do not expand to solve it.
>
> At most two *material* simplifications in data structures, state representation, or organizing model. Inspect implementation, public interfaces, major call sites, and existing tests. Prefer boring local code. Do not recommend style, hypothetical extensibility, or a new type that only relocates branching.
>
> Return `skip` or at most two recommendations, each with all 8 fields below. Do not edit files, run tests, or implement.

**Recommendation schema (all 8 required or reject):**

1. Verdict: `recommend` or `skip`
2. Evidence: exact file + line
3. Current complexity / invalid states
4. Proposed representation and why it is simpler
5. Smallest credible implementation scope (files / interfaces)
6. Regression risks and migration
7. Existing + additional validation required
8. Confidence: high / medium / low

**Done when:** every queued row has been reviewed; each rec has 8 fields or the row is `skip`.

### 3. Validate and synthesize

Independently verify every finding against the **current** tree before accepting it.

Reject, narrow, or demote: vague, duplicate, wrong about intentional semantics, or merely relocates complexity.

Skips count as coverage. Deduplicate. One authoritative subsystem per accepted rec.

Keep opening batches until every inventory row is complete.

**Done when:** you have re-checked each accepted rec yourself; no duplicate owners.

### 4. Audit the audit

Fresh independent pass (new worker / new context if available) for:

- Missing subsystem boundaries
- Duplication / ownership overlap
- Materiality and over-abstraction
- Schema completeness (all 8 fields)
- Dependency-aware ranking

A real omission → **new inventory row**, then audit it. Do **not** hide it by widening a completed boundary.

Rank remaining recs by concrete impact, confidence, implementation effort, blast radius, prerequisites. Name the best first implementation slices.

**Done when:** the checklist in Verification is true **and** `git status --porcelain` matches the start snapshot (no new mutations).

### 5. Present — then stop

Use `reply-contract` (+ show-me tree of ranked recs). Gloss *material* / *skip* if you used them.

The report must include:

- Coverage: N subsystems reviewed, N skips, N recs
- Ranked recs (ID, one-line simpler model, confidence, blast radius)
- Explicit “repo unchanged”
- **Your turn:** accept rec IDs, discard, or stop

Do not start implementation in the same turn as the report.

---

## After the user accepts

Only then, and only for accepted IDs:

1. Load `plan-code-review-workflow` + `write-tests`.
2. One slice per cycle. Do not “while we’re here” neighboring recs.
3. `expert-pr-review` on the PR.
4. `docs-protocol` if the new representation should be an ADR.
5. `feature-flag-lifecycle` only if the cutover cannot flip in one PR.

---

## Common pitfalls

1. Starting `plan-code-review-workflow` mid-audit because a rec looks obvious.
2. Running the test suite “to understand the system.”
3. Catch-all inventory rows instead of real boundaries.
4. Recommending a new type that wraps the same branching.
5. More than two recs per subsystem.
6. Treating skip as failure.
7. Widening a finished boundary when the coverage pass finds a hole.
8. Writing “implemented” into the memory bank — this skill never implements.

---

## Verification checklist

- [ ] Starting git snapshot recorded; ending porcelain matches (no audit-caused edits)
- [ ] Every identifiable subsystem has a row; no catch-all as proof of coverage
- [ ] Every row is `recommend` or `skip`
- [ ] Every rec has all 8 fields and coordinator-verified file:line evidence
- [ ] Audit-the-audit ran; omissions became new rows
- [ ] Recs ranked; first slices named
- [ ] Did **not** invoke implement skills or create a change branch
- [ ] Report used `reply-contract`; user must accept before any edit

*Last updated: 2026-08-22 | Hub version: 0.6.0*
