---
name: plan-code-review-workflow
description: "This skill should be used for any non-trivial task touching more than one file or with user-facing impact. It is the default development workflow for all significant features, refactors, bugfixes, or changes. Runs a Plan -> Code -> Review -> Iterate -> Finalize cycle with dynamic role switching between Software Architect, Software Engineer, and QA Critical Reviewer. Enforces TDD, expert review via expert-pr-review, and user approval gates before committing or pushing."
version: 1.0.2
---

# plan-code-review-workflow.md

**Core Development Workflow for All Significant Work**

This is the default process for any non-trivial task. It enforces the "Plan first, then Act" rule and guarantees critical review.

## When to Use
- Any feature, refactor, bugfix, or change that touches >1 file or has user impact.
- **Never skip** for greenfield or complex work (global rule).
- **Do not start this skill** during a `codebase-simplification-audit`. That audit is read-only until the user accepts a recommendation.
- **Do not start this skill** during `grill-with-docs` until the user confirms shared understanding.

## Roles Involved (Dynamic Switching)
- **Software Architect** (plan phase)
- **Software Engineer** (implement phase)
- **QA Critical Reviewer** (review phase — uses expert-pr-review skill when applicable)
- **(Optional) UI/UX Engineer** (if UI involved)

## Detailed Steps

### Phase 1: PLAN (Software Architect Role)
1. **Load Context** (mandatory)
   - Read all 6 memory-bank/*.md files for the active project (from manifest.yaml).
   - Read relevant memory-bank/ entries.
   - Read AGENTS.md sections on global rules and agents.
   - Read `STRATEGY.md` when the active project has one.
   - Read overlapping notes in `docs/solutions/` (`compound`). Do not re-plan a lesson already captured.
2. **Understand the Request**
   - Clarify goals, success criteria, edge cases, constraints with user.
   - Identify affected files, dependencies, breaking changes.
3. **Create Detailed Plan**
   - Use Mermaid flowchart if complex.
   - Break into small, testable steps.
   - Order the steps so that each one ends with a check you can run. Name that check beside the step, per the **pstack-principles** (sequence-verifiable-units) principle.
   - Include: files to create/edit, tests to add/update, risks, rollback plan.
   - Estimate effort and potential side effects.
4. **Document**
   - Write plan into `memory-bank/activeContext.md` under "## Current Plan".
   - Update `progress.md` with "Planning complete for [task]".
5. **Get User Buy-In**
   - Present plan clearly.
   - Ask: "Does this plan look complete and correct? Any changes? Ready to switch to Act mode (Software Engineer implements)?"

**Exit Criteria**: User explicitly approves plan and says "Proceed to implementation" or "Switch to Act mode".

### Phase 2: CODE / IMPLEMENT (Software Engineer Role)
1. **Switch Role** — Load `agents/software-engineer.md`.
2. **Execute Plan Exactly**
   - Make changes using read_file → edit_file / write_file / bash (non-interactive).
   - Follow existing codebase conventions 100% (KISS, style, patterns).
   - Add or update tests for every new behavior.
   - Run the named check for each step before you start the next step. Do not batch the checks at the end (sequence-verifiable-units).
   - Handle errors, edge cases, logging where appropriate.
3. **Self-Review Immediately**
   - Re-read changed files.
   - Run any local tests/linters if available. Read the real output (exit code, test count) and check the changed behavior on the real artifact, not on a re-read of the diff, per the **pstack-principles** (prove-it-works) principle.
   - Check against plan — did I miss anything?
4. **Update State**
   - Append to `memory-bank/progress.md`: "Implemented [X] per plan. Self-reviewed. Ready for QA."
   - Note any deviations or learnings.

**Exit Criteria**: All planned changes complete + self-review passed. Hand off to QA.

### Phase 2.5: SIMPLIFY THE DIFF
1. Refine only the fresh diff for reuse and clarity. Behavior stays the same.
2. Do not start `codebase-simplification-audit`. That skill is a whole-repo read-only audit.
3. Re-run the named checks. A simplify pass that fails a check is not done.

**Exit Criteria**: Diff is simpler and the same checks still pass. Then hand off to QA.

### Phase 2.75: ub-mode pre-PR dev flow (implementer)
1. Load `docs/shared/ub-mode-practice.md` (Pre-PR dev flow) and `skills/ub-mode/references/gates-by-language.md`.
2. After tests pass, run **`crapper --changed --threshold 10`** and **`dryer --changed --threshold 0.8`** (`rm -f .metrics/dry.edn` before dryer). **Fix** what they flag before opening a PR.
3. Run **`mutator --changed`** on changed functions only on a **laptop** or in **CI** — **never** in a cloud agent harness.
4. Record measured results on the PR **`Gates:`** line and in `progress.md`. **dryer (GMA-411):** missing `.metrics/dry.edn` after empty `--changed` = **no selection/skipped**, not a pass from an old file.
5. Push so CI job **`ub-gates`** runs the same checks (`scripts/run_ub_gates_ci.sh`). Advisory mode: gate debt on the **`Gates:`** line does not block QA **APPROVE**; a **red/missing `ub-gates` check** at head SHA is a gate miss (hand back without a review round).

**Exit Criteria**: Pre-PR dev flow done or skipped with documented reason; CI ub-gates triggered. Then hand off to QA.

**Optional — project standards:** When the active manifest project has `standards-<repo>/SKILL.md` in its harness skill folders, follow its PR and planning formats before QA recommends APPROVE (`docs/shared/repo-standards-practice.md`). Compatible with advisory ub-mode.

### Phase 3: REVIEW (QA Critical Reviewer Role)
1. **Switch Role** — Load `agents/qa-critical-reviewer.md` + full `skills/expert-pr-review/SKILL.md` if this results in a PR.
2. **Ub-gates at head SHA** — Confirm CI check **`ub-gates`** completed at the PR head SHA; do **not** re-run crapper/dryer/mutator. Gate miss → implementer fix; **not** a review round.
3. **Perform Critical Review**
   - If GitHub PR: Follow **exact** 8-step flow in expert-pr-review.md (gather context in parallel, resolve threads, build/test, security checklist, summarize).
   - If internal changes (no PR yet): Use the same rigor — checklist for correctness, style, tests, security, performance, accessibility (if UI), breaking changes.
   - Focus on highest-risk files first.
   - Be extremely critical but friendly ("Thanks @user! ...").
4. **Output**
   - Clear summary: What works, bugs/issues (grouped by severity), minor nits.
   - Recommendation: **APPROVE** | **REQUEST_CHANGES** | **COMMENT only**.
   - If REQUEST_CHANGES: List specific actionable items with file/line references.
5. **User Gate**
   - Present findings to user.
   - **Wait for explicit confirmation** before posting any review (if PR) or before engineer proceeds to fix.

**Exit Criteria**: QA approves or user says "Address the review comments and re-review".

### Phase 4: ITERATE (Engineer + QA Loop)
1. Engineer loads review feedback.
2. Fixes all requested changes (prioritize critical > major > minor).
3. Self-reviews fixes.
4. Hands back to QA for re-review.
5. Repeat until QA gives clean APPROVE.

**Limit**: Max 3 iterations before escalating to Architect for plan adjustment (rare).

### Phase 5: FINALIZE & KNOWLEDGE CAPTURE
1. **QA Approves** — "This looks great. Approved!"
2. **Engineer Final Touches**
   - Run full test suite / build if applicable.
   - Update any docs, CHANGELOG, version if needed.
3. **Knowledge Update** (mandatory)
   - Update `memory-bank/progress.md` with final status and what was learned.
   - Update `activeContext.md` — clear "Current Plan", note completion.
4. **User Confirmation**
   - Present summary: "Task complete. Changes: X files. Wiki updated: Y. Ready for commit/push?" 
   - **Only commit/push if user explicitly says yes** (global rule).

## Verification

- [ ] Each plan step names its own check, each check ran before the next step began, and the "Ready for QA" note cites real command output (sequence-verifiable-units, prove-it-works)

## Tone & Style Across All Phases
- Friendly, direct, concise.
- Start responses with role + thanks where appropriate.
- Use checklists, code blocks, Mermaid.
- Proactive but never destructive without confirmation.
- Always reference absolute paths.

## Example Invocation
User: "Follow the plan-code-review workflow to add global endpoint filtering to the model list."

Agent (Architect): "Understood. Loading context... [reads memory-bank + manifest]. Here's my plan: ... Does this look good?"

(After approval) Agent (Engineer): "Switching to Software Engineer. Implementing..."

(After code) Agent (QA): "Switching to QA Critical Reviewer. Performing review per expert-pr-review skill..."

This workflow guarantees high-quality, well-documented, reviewed output every time.

**Last updated**: 2026-10-03 | Integrates global rules + expert-pr-review + memory-bank protocol.
