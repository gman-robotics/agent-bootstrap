# Product Context: Multi-Agent Skills Hub

## Purpose
This project solves the problem of fragmented agent instructions across different AI coding harnesses (Claude Code, Cline, Cursor, Open Interpreter, etc.). Every time a new harness is added or a session resets, users must re-explain roles, workflows, and project context. This leads to inconsistent performance, lost knowledge, and repetitive setup.

## Problems Solved
- **Repetitive Context Loss**: Memory resets between sessions/harnesses; Memory Bank provides the single source of truth (as defined in this hub's memory-bank/ directory and memory-bank-protocol skill).
- **Role Inconsistency**: Different agents don't know "who" they are (architect vs engineer vs qa); agents/ defines reusable personas.
- **Workflow Fragmentation**: Complex processes like plan→code→review→fix are redefined per project; skills/ standardizes them (e.g., plan-code-review workflow).
- **Multi-Project Blindness**: Agents working on multiple codebases lose track; manifest.yaml gives explicit project registry.
- **Knowledge Silos**: Project insights, decisions, and learnings are lost or buried in chats; memory-bank/ provides persistent context for the team.
- **Skill Redefinition**: Excellent skills (expert-pr-review, cherry-pick-to-release-branch) from prior use were generalized into reusable hub skills for consistent reuse across projects and harnesses.

## User Experience Goals
- **Seamless Onboarding**: Clone repo → set AGENTS.md as instruction file in harness → immediately have full capabilities. One-time setup.
- **Role Switching**: Agent can say "I am now the Software Architect" and load the corresponding agent definition + follow its rules.
- **Workflow Invocation**: User says "Follow the plan-code-review workflow for task X" → agent executes the defined steps (plan with user, code, qa review, iterate).
- **Persistent Knowledge**: Agents proactively update memory-bank/ after tasks, making future sessions smarter.
- **Harness Agnostic**: Works the same whether in Claude's Artifacts, Cline sidebar, or custom MCP setup.
- **Proactive & KISS**: Agents are helpful without asking permission for obvious actions, but always co-create plans for significant work (per global rules).

## Success Criteria (Measurable)
- A new user can have a fully functional multi-agent setup in <5 minutes.
- After 3+ tasks using the workflows, memory-bank reflects accurate progress.
- PR reviews using the expert skill catch 90%+ of issues that a human senior dev would (based on past usage).
- manifest.yaml supports switching between 2+ real user projects without manual re-contextualization.
- All skills in this hub (expert-pr-review, cherry-pick-to-release-branch, memory-bank-protocol, etc.) are fully integrated, tested in workflows, and continuously improved (refactoring priority).

## Target Users
- **Development teams** using multiple AI coding agent harnesses who want to standardize workflows and share knowledge.
- Teams working on common projects who need persistent, searchable context and decisions.
- Developers who want to benefit from (and contribute to) team-developed skills and patterns without re-explaining everything.
