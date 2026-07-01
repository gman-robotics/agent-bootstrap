---
name: pr-shepherd
description: "This skill should be used at the start of every working day, immediately after opening/un-drafting/pushing fixes to a PR, when the user asks 'what's blocked?' or 'PR status', or as a recurring check on merge-heavy days. Enumerates open PRs across all repos (including agent-authored ones via the mem0 coordination bus when configured), classifies each as human-blocked / us-blocked / stacked-blocked / unassigned / ready-to-merge, front-loads reviewer-dependent asks in the first hour, and fills the wait with reviewer-free work."
version: 1.0.0
---

# pr-shepherd.md — PR Pipeline & Reviewer-Latency Management

**Purpose**
Keep our open PRs moving. Human reviewer latency is consistently the critical-path bottleneck (repeatedly: multiple PRs green-and-mergeable, human-blocked). This skill turns the proven counter-strategy into a routine: **front-load every reviewer-dependent ask, then fill the wait with reviewer-free work.**

**When to Use This Skill**
- At the **start of every working day** (pairs with `end-of-day-review.md`, which queues the asks for the morning)
- Immediately after opening, un-drafting, or pushing fixes to any PR
- When the user asks "what's blocked?", "PR status", or "what should I work on while waiting?"
- As a recurring check during a merge-heavy day

---

## Step 1: Enumerate Open PRs Across All Repos

Derive repositories from `manifest.yaml` — do not hardcode org/repo names. From the agent-bootstrap root:

```bash
# Helper: extract github.com owner/repo from a git remote URL
remote_to_repo() {
  git -C "$1" remote get-url origin 2>/dev/null \
    | sed -E 's#.*github\.com[:/]([^/]+/[^/.]+)(\.git)?$#\1#'
}

MANIFEST_ROOT="$(pwd)"  # agent-bootstrap root

# This hub
repo="$(remote_to_repo "$MANIFEST_ROOT")"
[ -n "$repo" ] && gh pr list --repo "$repo" --author "@me" \
  --json number,title,isDraft,mergeable,reviewDecision,statusCheckRollup,reviewRequests,updatedAt

# Each manifest project with a local git checkout
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    sys.exit(0)
manifest = Path("manifest.yaml")
if not manifest.exists():
    sys.exit(0)
data = yaml.safe_load(manifest.read_text()) or {}
root = manifest.resolve().parent
seen = set()
for proj in data.get("projects", []):
    path = (root / proj.get("path", ".")).resolve()
    if not (path / ".git").exists():
        continue
    try:
        remote = subprocess.check_output(
            ["git", "-C", str(path), "remote", "get-url", "origin"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        continue
    import re
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", remote)
    if m and m.group(1) not in seen:
        seen.add(m.group(1))
        print(m.group(1))
PY | while read -r repo; do
  gh pr list --repo "$repo" --author "@me" \
    --json number,title,isDraft,mergeable,reviewDecision,statusCheckRollup,reviewRequests,updatedAt
done
```

Include PRs authored by coordinated agents: **if mem0 is configured**, check the coordination bus `coord-YYYYMMDD` for PRs other harnesses opened on your behalf.

---

## Step 2: Classify Each PR

| State | Meaning | Action |
|---|---|---|
| **Human-blocked** | CI green + mergeable + review requested, no response | Ping/escalate (Step 3) |
| **Us-blocked** | CHANGES_REQUESTED, failing CI, or merge conflict | This is OUR critical path — fix today, before new work (use `triage-review-feedback.md` for review responses) |
| **Stacked-blocked** | Waiting on another PR in a stack to merge first | Note the dependency; when the parent merges, immediately rebase/retarget, resolve conflicts, verify diff-vs-main is only this PR's files, re-request review |
| **No reviewer assigned** | Open/un-drafted but nobody requested | Request a reviewer NOW — an unassigned PR ages silently |
| **Ready to merge** | Approved + green | Merge (per repo policy / user confirmation), then trigger the post-merge chain (deploys, dependent PR rebases) |

---

## Step 3: Front-Load Reviewer-Dependent Asks (FIRST HOUR)

The single highest-leverage rule:

> Reviewer latency is often the day's bottleneck. Front-load ALL reviewer-dependent asks in the first hour, then fill the wait with work needing no reviewers.

1. Request/re-request review on everything reviewable — all at once, not as you finish each task.
2. For each human-blocked PR, decide the nudge level:
   - **< 1 business day**: wait, no ping.
   - **≥ 1 business day**: polite ping on the PR or team channel, with a one-line "what's needed".
   - **Critical path** (blocks a deploy gate or other people): tell the user — escalation to a human channel is their call.
3. Never let a fix sit unpushed waiting for "one more thing" — push and re-request as soon as it's green; batching costs a reviewer round-trip.

---

## Step 4: Fill the Wait

While human-blocked, pick work that needs **no reviewer**:
- Next implementation task from `memory-bank/activeContext.md` (new branch, doesn't touch blocked PRs)
- Verification/E2E work (env checks, log evidence gathering)
- Re-planning, issue grooming, docs/ADRs, memory-bank compaction
- Pre-staging the post-merge chain: draft the rebase plan for stacked PRs, the project's deploy checklist (`docs/` runbook or deploy skill), release steps

Do NOT start work that will conflict with a blocked PR's files — it turns a merge into a rebase fight.

---

## Step 5: React to Reviewer Responses Fast

When a reviewer responds (check on each shepherd pass):
- **Approved** → merge promptly (per repo policy), kick off post-merge chain same day. A merged-but-undeployed PR is still a blocker for whatever gates on its deploy.
- **CHANGES_REQUESTED / comments** → switch to `triage-review-feedback.md` immediately. Same-day turnaround on review responses keeps our PRs at the top of the reviewer's mental stack.

---

## Step 6: Report

Output a compact status table (PR, state, who/what blocks it, age in that state, next action). **If mem0 is configured**, post material changes (merged, newly blocked) to the coordination bus so other harnesses see pipeline state.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Requesting reviews one-at-a-time as work finishes | Batch all asks in the first hour of the day |
| Treating "approved" as done | Merge + deploy + unblock the stack is the actual done |
| Starting big new work that touches a blocked PR's files | Pick disjoint fill-the-wait work |
| Pinging a reviewer hours after requesting | Give a business day; then a specific, low-effort ask |
| Forgetting agent-authored PRs | Check mem0 bus if configured; not just `--author "@me"` |
| Letting an un-drafted PR sit with no requested reviewer | Reviewer request is part of un-drafting, not a separate later step |

---
