# memory-bank-protocol.md — Memory Bank Setup and Maintenance Skill

**Purpose**
This skill formalizes the Memory Bank concept into a reusable, mandatory protocol for **any** long-running project. It guarantees context continuity across sessions, different agent harnesses (Claude Code, Grok, Cline, Codex, etc.), and multi-month tasks where chat history is useless.

Continuity rests on **one required layer** plus an **optional coordination layer**:
- **`memory-bank/`** (required) — per-project durable state (current focus, decisions, progress). Versioned files, human-readable, the source of truth for *project* state.
- **mem0 shared memory** (optional) — when your team configures it: cross-harness coordination (findings, handoffs, task state on `run_id: coord-YYYYMMDD`) and searchable session facts. Skip mem0 steps when not configured; the memory bank alone is sufficient for single-harness teams.

Because optional mem0 can carry fine-grained session/coordination traffic, the memory bank stays **lean**: it holds distilled state, not a transcript.

**When to Use This Skill**
- **Initializing** a brand new project (create the directory + 6 core files)
- **At the start** of every session or significant task (tiered read — see below)
- **At the end of every task** (update + compaction rules below)
- When switching projects via `manifest.yaml`
- When onboarding a new harness or team member to an existing project

---

## File Structure

All files live in `memory-bank/` at the **project root** (absolute path). Clean Markdown.

### The 6 Core Files

| Tier | File | Content | Volatility |
|---|---|---|---|
| Foundation | `projectbrief.md` | Scope, core goals/requirements | Rarely changes |
| Foundation | `productContext.md` | Purpose, problems solved, UX goals | Rarely changes |
| Foundation | `systemPatterns.md` | Architecture, design patterns, key decisions | Occasional |
| Foundation | `techContext.md` | Stack, tooling, setup, constraints | Occasional |
| **Hot** | `activeContext.md` | Current focus, plan, load-bearing decisions, next steps | Every session |
| **Hot** | `progress.md` | Status log, what works, learnings | Every session |

Plus: `memory-bank/archive/` — superseded activeContext/progress sections, moved out by the compaction rule.

---

## Tiered Read Protocol (Start of Every Session / Task)

**Always (every session):**
1. Read the two **hot files**: `activeContext.md` + `progress.md` (in parallel).
2. **If mem0 is configured**: search for task-relevant context — today's/yesterday's coordination bus (`run_id: coord-YYYYMMDD`) plus a semantic query for the task topic. This replaces re-reading history out of the bank.

**Conditionally (read the 4 foundation files when):**
- First session ever in this project, or first session after ≥ 2 weeks away
- The task touches architecture, cross-component design, stack/tooling choices, or anything `systemPatterns.md`/`techContext.md` governs
- Something in the hot files doesn't make sense without deeper context

When in doubt, read them — but a routine task in a familiar project needs only the hot files (plus optional mem0 search).

If any file is missing or empty: pause and initialize it using this skill.

> **Warning**: Skipping the hot-file read = instant amnesia. Chat history is **not** the source of truth.

---

## Update Protocol (End of Every Task)

1. **Update `activeContext.md`**: clear completed plan items; record new decisions, open questions, and the next steps.
2. **Update `progress.md`**: what was delivered, gotchas, learnings.
3. **If mem0 is configured**: post coordination-relevant outcomes (PRs opened/merged, handoffs, blockers) to the coordination bus so other harnesses see them without reading this bank.
4. **Verify** by re-reading what you changed.

### Evidence Rule (mandatory)

Any status claim of **implemented / merged / deployed / verified** MUST cite a verifiable artifact: commit SHA, PR link, CI run, log line, or task-def revision. A claim without an artifact is a *plan*, not a status — write it as one.

> Why: a past "implementation complete" entry was recorded with no commit behind it; the false record survived two days and cost a full audit to correct. The rule makes optimistic logging structurally impossible.

### Compaction Rule (keep the bank lean)

`activeContext.md` target: **≤ ~150 lines** — current focus, the active plan, and load-bearing decisions only.

During the end-of-day review (`end-of-day-review.md`) or whenever the file exceeds target:
1. Move superseded plans, completed-day chronologies, and resolved investigations to `memory-bank/archive/activeContext-YYYY-MM.md` (append-only, dated headers).
2. Keep in activeContext only: current focus, tomorrow's plan, decisions still constraining future work (with one-line context), open questions.
3. `progress.md`: keep the most recent ~2 weeks of entries inline; archive older ones to `memory-bank/archive/progress-YYYY-MM.md`.
4. Never delete — archive. The archive is grep-able history; activeContext is the working set every session pays to read.

**Litmus test**: "Will a session two weeks from now act differently because this paragraph is in activeContext?" No → archive it.

---

## Initialization Steps (New Project)

1. `mkdir -p /absolute/path/to/project/memory-bank/archive`
2. Create the 6 files (use this hub's `memory-bank/` as live templates).
3. Populate `projectbrief.md` first; fill others progressively.
4. Add the project to `manifest.yaml` (`memory_bank_path` pointing at the directory).
5. Run the Tiered Read Protocol to verify.

---

## What Goes Where — Decision Table

| Question | Layer |
|---|---|
| "What are we working on right now?" | `memory-bank/activeContext.md` |
| "What did another harness finish an hour ago?" | mem0 coordination bus (`coord-YYYYMMDD`) if configured; else `progress.md` |
| "What did we learn last Tuesday?" | `memory-bank/progress.md` (or archive) |
| "What does the API look like?" | `docs/projects/<name>/api-contracts.md` |
| "Why did we choose X?" | `docs/projects/<name>/decisions.md` (ADR) |
| "What's the deploy procedure?" | A skill or `docs/` runbook — never the memory bank |

> **Don't put technical reference in memory-bank** (context bloat → use `docs/`, see `docs-protocol.md`). **Don't put per-session coordination chatter in memory-bank** when mem0 is available — that's mem0's job. The bank holds the distilled state that survives both.

---

## Integration with Other Skills & Subagents

- **plan-code-review-workflow.md**: calls this protocol in PLAN (step 1) and FINALIZE (step 5).
- **end-of-day-review.md**: runs the compaction pass and writes tomorrow's plan into activeContext.
- **multi-harness-coordination.md**: uses mem0 (when configured) as the coordination bus; this bank stays the durable layer.
- **All agents** reference memory-bank/ in their behaviors; AGENTS.md §2 "Context Management" is enforced by this skill.

---

## Self-Hosting Note (This Repo)

This very `memory-bank/` is maintained using this skill. Commit policy varies by project — check `manifest.yaml` notes or project docs. This hub's memory-bank may be committed; application repos may keep theirs local.

**Last updated**: 2026-06-15 | Version: 2.0 (lean tiered protocol + optional mem0 + compaction & evidence rules)
