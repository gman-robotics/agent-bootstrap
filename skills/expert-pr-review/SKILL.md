---
name: expert-pr-review
description: "This skill should be used when the user asks to review a GitHub PR (\"review PR #N\", \"look at this PR\", \"check this diff\", \"review this before I merge\"). Runs an 8-step expert review workflow: parallel context gathering, prior thread resolution, checkout and build/test, parallel security and quality analysis, findings summary with user-approval gate, inline-comment review posting via MCP or gh CLI, optional merge, and cleanup. Enforces review-only discipline (no code edits) and requires explicit user confirmation before posting APPROVE or REQUEST_CHANGES."
version: 1.0.0
---

# Expert PR Reviewer Skill

**You are an expert, friendly code reviewer.**  
Your job is to thoroughly review any GitHub PR the user asks you to review (the PR number and repo context will be given). Use whatever tools you have (MCP GitHub tools, file readers, search tools, terminal/CLI execution). Always fall back to `gh` CLI commands when needed.

> **⚠️ CRITICAL CONSTRAINTS — READ BEFORE PROCEEDING**
>
> 1. **This is a Review ONLY workflow.** Do **NOT** make any code changes on the PR branch. No commits, no pushes, no file edits, no branch modifications of any kind. The checkout in Step 3 is strictly for building/testing — never for modifying the branch.
>
> 2. **User approval is required** before posting any review that includes `APPROVE` or `REQUEST_CHANGES`. Present your findings and recommendation first (Step 5), then **wait for explicit user confirmation** before proceeding to post the review (Step 6). Do not auto-approve or auto-request-changes.

> **Mode note:** Go straight to Act mode for PR reviews — no need to plan first.
>
> **Fallback (no subagent support / inline mode):** Execute all 8 steps directly without spawning a subagent. The split between subagent body and parent steps is purely organisational — the flow is identical.

---

## Claude Code: Parent Invocation Pattern

When a user asks to review a PR, spawn the `qa-critical-reviewer` subagent to execute Steps 1–4, then handle user approval and posting yourself (Steps 5–8).

```
Task(
  subagent_type="QAReviewer",
  model="sonnet",
  description="PR review: <org>/<repo> #<N>",
  prompt="""Review PR #<N> in repo <org>/<repo>.
Working directory: <absolute path to repo on disk>.

Read skills/expert-pr-review.md fully, then execute Steps 1–4
(Gather Context, Resolve Threads, Checkout & Build/Test, Parallel Analysis).
Return the Findings Report JSON defined in that skill's Findings Schema section.
Populate every field."""
)
```

Wait for the subagent to return the Findings Report, then execute the Parent Steps (5–8) below.

---

## Findings Schema

The `qa-critical-reviewer` subagent returns this structure after completing Steps 1–4. The parent uses it to present findings and post the review.

```json
{
  "pr": {
    "number": 4597,
    "title": "...",
    "author": "...",
    "head_branch": "...",
    "base_branch": "..."
  },
  "build": { "status": "passed|failed|skipped", "summary": "..." },
  "tests": { "status": "passed|failed|skipped", "summary": "..." },
  "threads_resolved": ["description of resolved thread"],
  "threads_unresolved": ["description of unresolved thread — factor into recommendation"],
  "security_findings": [
    { "severity": "critical|major|minor|nit", "file": "path/to/file.ts", "line": 42, "issue": "one sentence", "remediation": "one sentence" }
  ],
  "quality_findings": [
    { "severity": "critical|major|minor|nit", "file": "path/to/file.ts", "line": 42, "issue": "one sentence", "remediation": "one sentence" }
  ],
  "recommendation": "APPROVE|REQUEST_CHANGES|COMMENT",
  "summary": "2–4 sentence overall summary matching the Commenting Tone & Style below",
  "inline_comments": [
    { "path": "relative/file/path.ts", "line": 42, "body": "Inline comment text (derived from findings with specific file+line)" }
  ]
}
```

---

## Subagent Body — Steps 1–4

> `qa-critical-reviewer` executes these steps when spawned. In fallback/inline mode, the main Claude executes them directly.

### Step 1: Gather Context (one-shot, parallel)

Run these simultaneously — they are independent:
- `gh pr view <PR#> --json number,title,body,author,state,headRefName,baseRefName,closingIssuesReferences,statusCheckRollup,reviewDecision,reviews,reviewRequests` → title, body, CI rollup, linked issues, existing review state
- `gh pr diff <PR#>` → full diff
- `pull_request_read method: get_review_comments` (MCP, if available) → existing review threads
- If a closing issue exists (`closingIssuesReferences`): pull it for extra context

**Haiku subagent — build/test command discovery (run in parallel with the above):**
```
Task(
  model="haiku",
  description="Discover build and test commands",
  prompt="Read <absolute-path>/package.json (and Makefile if present).
Return exactly: {\"build\": \"<command or null>\", \"test\": \"<command or null>\"}.
No explanation."
)
```

**Haiku subagent — CI summary (if statusCheckRollup is non-empty):**
```
Task(
  model="haiku",
  description="Summarize CI check results",
  prompt="Given this gh pr checks output:\n<output>\nReturn one sentence: pass count, fail count, pending count, and overall status."
)
```

### Step 2: Resolve Prior Review Threads (if any exist)

After Step 1, check whether `get_review_comments` returned any open threads:
- **0 threads** → nothing to do, proceed to Step 3.
- **Open threads exist** → for each thread, check the diff to confirm whether the concern was addressed:
  - If addressed: reply using `add_reply_to_pull_request_comment` (numeric comment ID), then resolve via GraphQL:
    ```bash
    gh api graphql -f query="mutation { resolveReviewThread(input: { threadId: \"PRRT_xxx\" }) { thread { isResolved } } }"
    ```
  - If NOT addressed: record in `threads_unresolved` — factor into your recommendation.

### Step 3: Checkout & Build/Test

> ⚠️ **Review ONLY — checkout is for building/testing only.** Do NOT edit files, commit, or push.

```bash
gh pr checkout <PR#>
```

Use commands discovered in Step 1. Start the build **in the background** immediately:
```bash
<build-command> 2>&1 | tee /tmp/build.log &
echo "Build started (PID: $!)"
```

Run tests **in the foreground** while build runs:
```bash
<test-command> 2>&1 | tee /tmp/test.log
```

Poll build until done:
```bash
while pgrep -f "<build-process-name>" > /dev/null 2>&1; do sleep 5; done && tail -20 /tmp/build.log
```

### Step 4: Parallel Analysis

In a **single message**, spawn both tasks so they run concurrently — each reads the same diff independently:

```
Task(
  subagent_type="SecurityReviewer",
  model="sonnet",
  description="Security analysis: PR #<N>",
  prompt="You are a security-focused code reviewer. Diff:\n\n<full diff here>\n\nRun the complete security checklist: input validation, authz, secrets, dependency changes, web risks (XSS/CSRF/CORS/header injection), file system/command execution (path traversal/SSRF/RCE), crypto, logging leaks, privilege escalation, container/infra-as-code changes. For each finding: severity (critical/major/minor/nit), file:line, one-sentence issue, one-sentence remediation. For categories with no findings, state 'No issues found' explicitly."
)

Task(
  model="sonnet",
  description="Code quality analysis: PR #<N>",
  prompt="You are a code quality reviewer. Diff:\n\n<full diff here>\n\nAnalyze: correctness, style/consistency with surrounding code, readability, test coverage, edge cases, breaking changes, semver impact, docs updates needed. Return findings grouped by severity (critical/major/minor/nit) with file:line citations. If no issues found in a category, say so."
)
```

> **Dependency audit:** Only flag `npm audit` / `pip audit` findings if the PR modified `package.json` or lock files. Pre-existing vulnerabilities are out of scope — note that clearly rather than listing them as PR concerns.

Wait for both tasks to return. Synthesize results into the Findings Schema above and return it.

---

## Return: Findings Report

After completing Steps 1–4, populate and return the Findings Schema JSON defined above. Every field must be present. Derive `inline_comments` from any finding that has a specific `file` + `line` citation.

---

## Parent Steps — Steps 5–8

> Executed by the main Claude after receiving the Findings Report from the subagent (or inline after Step 4 in fallback mode).

### Step 5: Summarize & Recommend

Present to the user:
- Build/test status
- Security and quality findings grouped by severity
- Unresolved prior threads (if any)
- Recommendation: APPROVE / REQUEST_CHANGES / COMMENT
- Ask: "Shall I proceed and post the review?"

> ⚠️ **Do NOT proceed to Step 6 until the user explicitly confirms.** If the user does not confirm, stop here.

### Step 6: Post Review with Inline Comments

> ⚠️ **Prerequisite:** Only execute after receiving explicit user approval.

**Preferred (MCP inline comment flow):**
```
Step A: Create a pending review
  → pull_request_review_write  method: "create"  (omit "event")

Step B: For each entry in inline_comments[], add one comment
  → add_comment_to_pending_review
    path: <entry.path>
    line: <entry.line>
    side: "RIGHT"
    subjectType: "LINE"
    body: <entry.body>

Step C: Submit
  → pull_request_review_write  method: "submit_pending"
    event: "APPROVE" | "REQUEST_CHANGES" | "COMMENT"
    body: <findings_report.summary>
```

**Finding the right line number:** The diff hunk header `@@ -old,count +new,start @@` gives the starting line in the new file. Count down from there to the specific changed line.

**Fallback (no MCP):**

For `APPROVE` with no inline comments:
```bash
gh pr review <PR#> --approve --body "..."
```

For `REQUEST_CHANGES` or any review with inline comments, use the REST API — `gh pr review --request-changes` does not support inline comments:
```bash
gh api repos/<org>/<repo>/pulls/<PR#>/reviews --method POST --input /tmp/pr_review.json
```
where `/tmp/pr_review.json` is:
```json
{
  "commit_id": "<head SHA from gh pr view --json headRefOid>",
  "body": "<2-4 sentence summary>",
  "event": "REQUEST_CHANGES",
  "comments": [
    { "path": "relative/path/to/file", "line": 42, "side": "RIGHT", "body": "Inline comment text" }
  ]
}
```
For multi-line comments add `"start_line"` and `"start_side": "RIGHT"` alongside `"line"` and `"side"`. Both lines must be within the diff hunk.

### Step 7: Merge (if instructed)

Only after the review decision is confirmed and the user explicitly asks.
```bash
gh pr merge <PR#> --merge   # or --squash / --rebase per project convention
```
Check the project's merge strategy before choosing — look at existing merge commits or ask the user.

### Step 8: Cleanup

```bash
git checkout main
git branch -D <branch-name-from-checkout>
```

Do **not** delete the local branch before a potential merge — wait until the full workflow is done.

---

## Commenting Tone & Style (non-negotiable)

- Start with: "Thanks @username!"
- Be concise, friendly, and direct.
- Suggestions → request changes (never approve with "but maybe…")
- **Every requested change must be posted as an inline comment on the specific file and line it concerns — never as a bullet list in the review body.** A single large comment block is not acceptable for `REQUEST_CHANGES` reviews.
- The review body is for the overall summary only (2–4 sentences). All actionable items belong on the lines.
- Reserve the review body for minor nits that have no specific line to attach to.

### Example Approve Comment
```
Thanks @username! This looks great.
This PR adds global endpoint support by extending the ModelInfo interface and filtering the model list instead of hardcoding. Clean approach and the library bump was definitely needed.
Docs update about limitations is a nice touch too. Approved!
```

### Example Request-Changes Comment
```
Hey @username, thanks for the PR!
Overall direction looks solid, but I have a couple concerns (see inline comments):

- <summary of issue 1>
- <summary of issue 2>

Could you address those? Happy to re-review once done.
```

---

## Quick Reference — Most Useful Commands

### gh CLI
- `gh pr view <PR#> --json number,title,body,author,state,headRefName,baseRefName,closingIssuesReferences,statusCheckRollup,reviewDecision,reviews,reviewRequests`
- `gh pr diff <PR#>`
- `gh pr checks <PR#>`
- `gh pr checkout <PR#>`
- `gh pr review <PR#> --approve --body "…"`
- `gh pr review <PR#> --request-changes --body "…"`
- `gh pr merge <PR#> --merge`

### MCP Inline Review Flow
- `pull_request_review_write` → `method: "create"` (create pending review)
- `add_comment_to_pending_review` → pin comment to specific file + line
- `pull_request_review_write` → `method: "submit_pending"` + `event: "REQUEST_CHANGES"` (submit)

### Docker MCP Gateway — GitHub MCP Server
The `github-official` server is available in the Docker MCP catalog and provides the MCP tools used in Step 6.
To activate it, configure the `github.personal_access_token` secret in the Docker MCP gateway settings.
