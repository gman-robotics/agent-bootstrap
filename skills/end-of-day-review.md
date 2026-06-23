# end-of-day-review.md — Daily Wrap-Up & Next-Day Plan

**Purpose**
A short, structured session at the end of each working day: verify what actually got done (against evidence, not memory), capture learnings, compact the memory bank, and write tomorrow's plan with reviewer-dependent asks queued first.

**When to Use This Skill**
- End of every working day ("wrap up the day", "EOD", "let's plan tomorrow")
- Before any extended break (weekend, vacation) — same steps, longer horizon
- Pairs with `pr-shepherd.md`, which executes the queued asks the next morning

---

## Step 1: Verify the Day's Outcomes (Evidence-Based)

Do not trust the session's narrative — check live state:

```bash
# What merged / moved recently (Linux-compatible date)
SINCE=$(date -d '1 day ago' +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)
gh search prs --author "@me" --updated ">=${SINCE}" --json repository,number,title,state

# Per-repo open PR state (repeat for each repo from manifest.yaml — see pr-shepherd.md)
gh pr list --repo <org>/<repo> --author "@me" --json number,reviewDecision,statusCheckRollup,mergeable
```

**If mem0 is configured:** pull today's coordination bus (`run_id: coord-YYYYMMDD`) for what other harnesses completed or handed off.

For each item planned this morning: **done (cite SHA/PR/log), partially done (what remains), or not started (why)**. A status claim without a verifiable artifact is not a status — write it as a plan instead.

---

## Step 2: Capture Learnings

One bullet each, only if real:
- **Process learnings** → `memory-bank/progress.md` "Key Learnings" (e.g., "front-load reviewer asks"; "worktree isolation mandatory")
- **Technical/contract learnings** → the owning repo's memory-bank or `docs/`. If it changes a skill's steps, update the skill file itself — skills are versioned process memory.
- **Candidate new skill**: if the same un-codified workflow ran ≥2 times this week, propose codifying it.

---

## Step 3: Update + Compact the Memory Bank

1. Append today's entry to `memory-bank/progress.md` (what was done, learnings) and update `memory-bank/activeContext.md`.
2. Run the **compaction pass** from `memory-bank-protocol.md`: superseded plans and completed-day details move to the archive; activeContext keeps only current focus, load-bearing decisions, and tomorrow's plan.
3. Apply the **evidence rule**: every "merged/deployed/done" claim written today must carry its SHA, PR link, or log reference.

---

## Step 4: Write Tomorrow's Plan

Add a `## Plan for <YYYY-MM-DD>` section at the **top** of `memory-bank/activeContext.md`:

1. **State snapshot** (1–3 lines): the bottleneck, what's blocked on whom.
2. **First hour — reviewer-dependent asks**: every review request, re-request, ping, and merge that needs a human. Front-loading these is the single proven latency win.
3. **Main work items** (ordered, 2–5): each with its blocking dependency named, so the next session can re-order when something unblocks.
4. **Fill-the-wait items**: reviewer-free work for human-blocked gaps.
5. **Gates/deadlines**: anything date-bound (release train, deploy window).

Keep it under ~25 lines. The plan is for tomorrow's first session read, not an archive.

---

## Step 5: Sync the Coordination Bus (optional)

**If mem0 is configured:** post a compact EOD summary (`run_id: coord-YYYYMMDD`, plus tomorrow's run_id if creating handoffs): what merged, what's blocked on whom, tomorrow's first moves. Other harnesses start from this.

If mem0 is not configured, the `## Plan for <date>` section in activeContext is sufficient for the next session.

---

## Step 6: Commit (per project policy)

If this project's memory-bank is committed (this hub may be), use a `docs(memory-bank): EOD <date> — <one-line summary>` commit message. Confirm with the user before pushing if not already authorized.

---

## Anti-Patterns

| Anti-pattern | Why it hurts |
|---|---|
| Narrating the day from session memory | Optimistic logging → false records |
| Writing tomorrow's plan as prose paragraphs | The morning session needs an ordered, scannable list |
| Skipping compaction "just today" | activeContext grows ~50 lines/day and every session pays the read |
| Planning only main work, no fill-the-wait items | Human-blocked time becomes idle time |
| Leaving learnings in the chat | The session is gone tomorrow; files (and mem0 if configured) persist |

---

Last updated: 2026-06-15
