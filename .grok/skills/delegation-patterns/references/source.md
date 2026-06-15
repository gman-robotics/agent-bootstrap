# Delegation Patterns — Claude Code Multi-Agent Reference

**Scope**: Claude Code native `Task()` delegation. These patterns are no-ops in Cline/Cursor/other harnesses — frontmatter is ignored and the agent definitions are simply read as context.

---

## The Two-Tier Rule

Before spawning a subagent, pick the right tier:

| Tier | When to use | Model | `maxTurns` |
|------|-------------|-------|------------|
| **Tier 1 — Lightweight** | Classification, routing, quick reads, summarising a small file | `claude-haiku-4-5` (set in prompt override) | 3 |
| **Tier 2 — Full** | Structured analysis, code generation, multi-step workflows | `claude-sonnet-4-5` (agent default) | per agent definition |

**Rule**: Default to Tier 2 (sonnet) for anything beyond simple classification. These tasks involve pattern matching and structured analysis — they benefit from the full model.

---

## Pattern 1: Parallel Read-Only Analysis

Use when N independent read tasks produce results that are later synthesised.

```
# In a single message (runs simultaneously):
Task(
  subagent_type="<AgentName>",
  description="<short label for logging>",
  prompt="<full context + specific instructions>"
)

Task(
  subagent_type="<AgentName>",
  description="<short label for logging>",
  prompt="<full context + specific instructions>"
)
```

**Rules**:
- All Task() calls in **one message** = parallel execution.
- Task() calls across **separate messages** = sequential.
- Use read-only agents (Write-deny permissions) to prevent races.
- Pass the full input (diff, file content, etc.) in each prompt — agents don't share state.

---

## Pattern 2: Parallel Independent Edits (worktree isolation)

Use when N agents each own a disjoint set of files and write simultaneously.

> **Hard rule**: worktree isolation is **mandatory for ANY editing agent** when the shared checkout could be in use — by another agent, a PR-review checkout, or the user — not just for parallel edits. Read-only agents are exempt. See `subagent-routing.md` Rule 3.

```
Task(
  subagent_type="Engineer",
  description="Implement feature A in src/feature-a/",
  prompt="Implement <feature A spec>. Touch only files under src/feature-a/."
)

Task(
  subagent_type="UIUXEngineer",
  description="Implement UI for feature A in src/components/",
  prompt="Implement <UI spec>. Touch only files under src/components/."
)
```

**Requirements**:
- Agents must have `isolation: worktree` in their frontmatter (Engineer and UIUXEngineer do).
- File ownership must be disjoint — overlapping writes cause conflicts even with worktree isolation.
- Merge results manually or with a follow-up Engineer Task() after both complete.

---

## Pattern 3: Parallel PR Analysis (SecurityReviewer + QAReviewer)

The canonical use case — replaces Step 4 of `expert-pr-review.md`.

```
Task(
  subagent_type="SecurityReviewer",
  description="Security analysis: PR #<N>",
  prompt="You are a security-focused code reviewer. Diff:\n\n<full diff here>\n\nRun the complete security checklist (input validation, authz, secrets, dependency changes, web risks, file system/command execution, crypto, logging leaks, privilege escalation). Return structured findings: each finding must include severity (critical/major/minor/nit), file:line, and a one-sentence remediation. If no issues found in a category, say so explicitly."
)

Task(
  subagent_type="QAReviewer",
  description="Code quality analysis: PR #<N>",
  prompt="You are a code quality reviewer. Diff:\n\n<full diff here>\n\nAnalyze: correctness, style/consistency with surrounding code, readability, test coverage, edge cases, breaking changes, semver impact, docs updates needed. Return structured findings grouped by severity (critical/major/minor/nit) with file:line citations."
)
```

Synthesise both outputs in the next message, then continue with Step 5 of `expert-pr-review.md`.

---

## Named Agent Reference

| Agent name | File | `isolation` | Write? | Best for |
|---|---|---|---|---|
| `Architect` | `agents/software-architect.md` | none | ❌ deny | Planning, ADR writing |
| `Engineer` | `agents/software-engineer.md` | worktree | ✅ allow | Implementation, refactors |
| `QAReviewer` | `agents/qa-critical-reviewer.md` | none | ❌ deny | Full PR review orchestration |
| `SecurityReviewer` | `agents/security-reviewer.md` | none | ❌ deny | OWASP security checklist |
| `UIUXEngineer` | `agents/ui-ux-engineer.md` | worktree | ✅ allow | Frontend implementation |

---

## Install (make agents available globally in Claude Code)

```bash
bash scripts/install-agents.sh
```

This symlinks every `agents/*.md` into `~/.claude/agents/` so Claude Code's project-local and global scan paths both resolve the agent names used in `subagent_type`.

---

**Last updated**: 2026-06-15
