---
name: triage-review-feedback
description: "This skill should be used when a PR we authored receives review feedback - from a human reviewer, an AI reviewer, or an automated scanner - or when the user says 'address the review feedback on PR #N' or 'triage the comments on my PR'. Workflow: inventory every claim, verify each against the actual code/environment before classifying (FIX / DISMISS-with-evidence / JUDGMENT), tag every FIX NEW or REPEAT (REPEAT closes only with a mechanical check, never an instance fix or a comment - worked example in fixtures/repeat-exporter-dropped-references/), apply the fix batch TDD-first, run a QA pass before posting, then reply to every thread, resolve, and re-request review. The inverse of expert-pr-review."
version: 1.2.0
---

# triage-review-feedback.md — Responding to Reviews on Our Own PRs

**Purpose**
Systematic workflow for triaging and responding to review feedback received on a PR **we authored** — human reviewers, AI reviewers, and automated scanners (Amazon Inspector, CodeQL, linters). The inverse of `expert-pr-review.md` (which is for reviewing *others'* PRs).

The core discipline: **verify every claim against the actual code before classifying it.** Reviewer claims are hypotheses, not facts — some are wrong, some are right for the wrong reason, and some are *worse* than reported.

**When to Use This Skill**
- A PR we authored received a review (CHANGES_REQUESTED, COMMENTED, or inline comments)
- An automated scanner posted findings on our PR (Amazon Inspector, CodeQL, Dependabot, etc.)
- An AI reviewer posted a multi-item review
- The user says "address the review feedback on PR #N" or "triage the comments on my PR"

**Field-proven**: a multi-item AI review (11 findings → 6 fixed, 4 dismissed with evidence, 1 judgment call); a scanner batch (16 comments → all refuted with data-flow evidence); a human review (2 blockers → fixed + threads resolved).

---

## Step 1: Inventory ALL Feedback

Gather every open item before acting on any of them:

```bash
# All reviews + states
gh pr view <N> --repo <org>/<repo> --json reviews,reviewDecision

# All inline review comments with thread state
gh api repos/<org>/<repo>/pulls/<N>/comments --paginate

# Unresolved review threads (GraphQL — thread resolution state is not in REST)
gh api graphql -f query='query { repository(owner:"<org>", name:"<repo>") {
  pullRequest(number:<N>) { reviewThreads(first:100) { nodes {
    isResolved path line comments(first:10){nodes{author{login} body}} } } } } }'
```

Build a numbered list: one row per distinct claim (a single review may contain many). Note the source type — **human**, **AI reviewer**, or **scanner** — because the dismissal bar differs (see Step 3).

---

## Step 2: Verify Each Claim Against Reality

For **every** item, before classifying:

1. **Read the actual code at the cited location** — not the reviewer's quote of it. Quotes are sometimes stale or truncated.
2. **Check the claim against the full context**: surrounding code, callers, the migration/contract it touches, test coverage.
3. **Check environment facts when the claim depends on them** (DB versions, runtime versions, infra config). Example: a database-version concern was refuted by confirming the fleet runs a single supported version.
4. **Look for the claim being *understated***: one duplicate-index finding turned out worse than reported — the boot-time creator also ignored the `unique` flag. Verification is not just for dismissing; it sharpens fixes too.

**Never classify an item from memory or from the reviewer's description alone.**

---

## Step 3: Classify Each Item

| Verdict | Criteria | Action |
|---|---|---|
| **FIX** | Claim verified correct (or worse than reported) | Add to fix batch |
| **DISMISS** | Claim refuted by code or environment evidence | Draft reply citing the specific evidence (file:line, version, config value) |
| **JUDGMENT** | Claim is valid but the tradeoff is debatable | Decide, state the reasoning in the reply; when genuinely 50/50, ask the user |

**Dismissal bar by source**:
- **Scanner findings** (Inspector, CodeQL): dismiss only with a concrete data-flow argument — e.g., "template vars are compile-time constants, not user input"; "path is server-generated, never user-supplied"; "CI-only script with no HTTP surface". Generic "false positive" replies are not acceptable.
- **AI reviewer findings**: same evidence bar as scanners. Expect a mixed batch — verify all, assume none.
- **Human reviewer findings**: if dismissing, the reply must be respectful, cite evidence, and explicitly invite pushback. When the human marked it blocking, prefer a conversation over a unilateral dismiss.

**Tag every FIX: NEW vs REPEAT**

Every item classified FIX also gets a second, orthogonal tag:

| Tag | Meaning |
|---|---|
| **NEW** | First time this failure class has been called on this repo, or on the same product family. |
| **REPEAT** | The same failure class was already called before — on this repo, or on the same product family — regardless of which file, symbol, or PR it shows up in this time. |

REPEAT is a class match, not a location match: a different file or function with the same underlying failure still counts.

**Closing a REPEAT tag is stricter than closing a NEW one.** A REPEAT item is never closed by an instance fix alone, and it is never closed by adding another PR comment, AGENTS.md line, skill line, or style-guide line — none of those are mechanical, and none of them stop the same class from recurring. Closing REPEAT requires the fix batch (Step 4) to also add one mechanical check that goes red on a fixture reproducing the old bug and green once the fix lands: a lint rule, a compiler/type-checker diagnostic, a failing-then-green test, or a CI rule. If no mechanical check is added, the item stays open no matter how many times it has been fixed by hand.

**Worked example in this repo**: `fixtures/repeat-exporter-dropped-references/` — a real failure class (`scripts/export_codex_skills.py`'s `--force` re-export dropping hand-added `references/` files) called NEW once, then REPEATed twice with no mechanical check, then finally closed by `tests/test_export_codex_skills.py::test_force_reexport_preserves_hand_added_reference_files` (red before the exporter fix, green after) plus the fix itself. This is not a hypothetical — that exact history is logged in `memory-bank/progress.md` (2026-08-22, three separate entries).

**Record the class on every NEW tag.** Note, in one line, what actually broke (the failure class, not just the file:line) so the next occurrence is recognized as REPEAT instead of re-classified NEW. See Step 7.

---

## Step 4: Fix Batch (TDD)

1. Apply all FIX items on the PR branch following `write-tests.md` (failing test first where behavior changes).
2. One logical concern per commit where practical; reference the review item in the commit body.
3. For any item tagged **REPEAT**, the same commit must add the mechanical check named in Step 3 (lint rule, compiler/type diagnostic, failing-then-green test, or CI rule) — a REPEAT fix with no mechanical check is not done.
4. Run the full affected suite green before moving on.
5. If a fix changes a documented contract (migration comments, API docs), update the document in the same commit — contract text and code must never disagree.

---

## Step 5: QA Pass Before Posting Anything

Spawn a QA review (QAReviewer agent or inline `expert-pr-review` Steps 1–4 equivalent) of the **new commits** before posting replies. The bar: verdict SHIP/APPROVE on the fix batch. Do not skip this because the fixes "look small."

---

## Step 6: Post Replies + Resolve Threads

1. Reply to **every** item — fixed items get the commit SHA; dismissed items get the evidence; judgment calls get the reasoning.
2. Resolve threads you replied to **only when** the item is fixed-and-pushed or dismissed-with-evidence. Leave genuinely open questions unresolved.
3. Push all commits before posting replies, so cited SHAs exist on the remote.
4. Re-request review from the blocking reviewer after everything is posted (do this immediately — reviewer latency is the usual critical path; see `pr-shepherd.md`).

---

## Step 7: Record the Tally

Add one line to `memory-bank/progress.md`. **If mem0 is configured**, also post to the coordination bus:

> Triaged &lt;M&gt;-item review on &lt;repo&gt;#&lt;N&gt;: X fixed (`&lt;sha&gt;`), Y dismissed with evidence, Z judgment. QA verdict: &lt;verdict&gt;. Re-review requested from &lt;reviewer&gt;.

For every FIX tagged **NEW** this pass, add a second line naming the failure class in one sentence (what broke, generically — not just the file:line). This is the record a future triage checks before tagging a similar-looking finding NEW again; without it, the same class is re-discovered as NEW every time instead of recognized as REPEAT.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Fixing items in the order they appear, without inventorying first | Inventory all, verify all, then batch — avoids rework when items interact |
| Accepting an AI/scanner claim because it sounds plausible | Verify at the cited location; mixed batches are common |
| Dismissing with "false positive" and no evidence | Cite the data-flow or environment fact that refutes it |
| Posting replies before pushing the fix commits | Push first; replies should cite real SHAs |
| Resolving a human's blocking thread unilaterally | Reply with evidence and let them resolve, or get explicit agreement |
| Forgetting to re-request review after responding | Always re-request — an answered review with no re-request is invisible to the reviewer |
| Closing a REPEAT with an instance fix and a "won't happen again" comment | Add the lint/diagnostic/test/CI rule named in Step 3 in the same fix commit, or leave it open |
| Closing a REPEAT by adding a line to AGENTS.md, a skill, or a style guide | Soft guidance is not mechanical; it does not close REPEAT on its own |
| Skipping the NEW failure-class note because the fix "was obvious" | Record it anyway — it is what makes the next sighting recognizable as REPEAT |

---
