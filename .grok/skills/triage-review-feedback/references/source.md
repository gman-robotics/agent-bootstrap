---
name: triage-review-feedback
description: "This skill should be used when a PR we authored receives review feedback - from a human reviewer, an AI reviewer, or an automated scanner - or when the user says 'address the review feedback on PR #N' or 'triage the comments on my PR'. Workflow: inventory every claim, verify each against the actual code/environment before classifying (FIX / DISMISS-with-evidence / JUDGMENT), apply the fix batch TDD-first, run a QA pass before posting, then reply to every thread, resolve, and re-request review. The inverse of expert-pr-review."
version: 1.0.0
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

---

## Step 4: Fix Batch (TDD)

1. Apply all FIX items on the PR branch following `write-tests.md` (failing test first where behavior changes).
2. One logical concern per commit where practical; reference the review item in the commit body.
3. Run the full affected suite green before moving on.
4. If a fix changes a documented contract (migration comments, API docs), update the document in the same commit — contract text and code must never disagree.

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

---
