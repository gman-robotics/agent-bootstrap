---
name: agent-orchestration-roles
description: "This skill defines the standard division of labor and coordination workspace when multiple agent harnesses (e.g. Claude Code and Codex CLI) collaborate on the same team of projects. Use this to orient a new harness and to coordinate tasks between a planning/reviewing harness and an implementing harness."
version: 1.0.0
---

# Agent Orchestration Roles & Coordination

This skill establishes a standardized division of labor and coordination workspace for autonomous agents working across the projects listed in this hub's `manifest.yaml`. It serves as a persistent guide so multiple agent harnesses cooperate seamlessly and respect their defined roles.

## Coordination Workspace

All development and orchestration activities are coordinated from the parent directory that contains this `agent-bootstrap` checkout and its sibling project repos (resolve the exact path via `manifest.yaml`).

`agent-bootstrap` itself serves as the central hub where agents (Claude Code, Cline, Codex, etc.) retrieve, share, and maintain cross-agent skills, standard rules, and project-wide context.

---

## Harness Roles & Division of Labor

To maximize efficiency and reliability, split agent harnesses into specialized roles rather than having every harness do everything:

### 1. Planner / Architect / Reviewer harness (e.g. Claude Code)
Designated as the **Planner, Architect, and Reviewer**. It handles high-level, reasoning-heavy tasks.
- **Planning & Architecture:** Drafting implementation plans, analyzing dependencies, and structuring tasks.
- **Code Reviews:** Conducting detailed reviews of code files and pull requests.
- **PR Reviews:** Checking diffs, validating logic, and confirming issue resolution.
- **Security Reviews:** Scanning for potential vulnerabilities, credentials in code, and compliance flaws.

*Guideline:* This harness focuses on analysis, documentation, plan-creation, and quality assurance. It does not perform the direct, bulk feature coding if an implementer harness is available.

### 2. Implementer / Software Engineer harness (e.g. Codex CLI)
Designated as the **Software Engineer / Implementer**. It is responsible for translating plans into code.
- **Code Implementation:** Writing the physical code, creating new features, and making the requested code changes.
- **Refactoring:** Executing code adjustments and cleanups based on plans and reviews.
- **Test-Driven Development (TDD):** Writing and running tests (Red-Green-Refactor) for code changes.

*Guideline:* The implementer harness focuses on writing clean, functional code according to the plans and review feedback provided by the planner harness.

---

## Workflow & Collaboration Loop

When executing a task or developing a feature, the standard collaboration loop is:

```
                  ┌─────────────────────────────────┐
                  │ 1. User initiates a request      │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │ 2. Planner harness: Plans/Designs│
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │ 3. Implementer harness: Codes    │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │ 4. Planner harness: Reviews/Audits│
                  └─────────────────────────────────┘
```

1. **Planning:** The planner harness analyzes the requirements, creates an implementation plan, and gains user approval.
2. **Execution:** The implementer harness picks up the approved plan and implements the code changes (strictly following the TDD Red/Green/Refactor standard).
3. **Review:** The planner harness runs a full PR / code review on the implementer's changes to verify correctness, security, and quality before finalization.

---

## Troubleshooting & Verification

- **Workspace Path:** Verify your working directory matches the parent directory declared for this hub in `manifest.yaml`.
- **Cross-Agent Skills:** Confirm that any cross-agent skills are committed and stored under `skills/` so they are accessible to every harness.
- **Memory Sync:** If shared memory (e.g. mem0) is configured, ensure critical findings or status changes are written there so subsequent agent runs can see the current state of work.

*Last updated: 2026-07-01*
