# Project Brief: Multi-Agent Skills Hub

## Project Name
Multi-Agent Skills Hub (or Universal Agent Harness)

## Core Goals
- Create a **shared team knowledge base** that defines reusable agents, skills (workflows), and knowledge management for AI coding agents used by the whole development team.
- Enable consistent behavior across different agent harnesses by providing AGENTS.md as the single source of truth.
- Make it easy for any team member to contribute and benefit from skills/patterns developed by others.
- Support multi-project awareness (our common projects) via manifest.yaml.
- Provide persistent knowledge management via memory-bank/ for projects and team practices.
- Define standard workflows (plan-code-review, expert-pr-review, etc.) so the whole team follows the same high-quality process.
- Make onboarding new team members and new harnesses fast and consistent.

## Scope
- **In Scope**: 
  - Core files: AGENTS.md, CLAUDE.md, README.md, manifest.yaml
  - Subagent role definitions (software architect/plan, software engineer/code, qa/critical reviewer, ui/ux, etc.)
  - Skills directory with reusable workflows (PR review, cherry-pick, llm-wiki, plan-code-review, etc.)
  - Wiki directory with initial structure and llm-wiki skill for management
  - Memory bank integration as example and for this project's own continuity
  - Documentation on usage with popular harnesses
- **Out of Scope** (initial):
  - Specific integrations/code for each harness (users adapt AGENTS.md)
  - Full implementation of all possible agents
  - Automated testing of skills (future)

## Success Criteria
- Any team member can clone this repo and immediately have full multi-role, multi-workflow capability via AGENTS.md + agents/ + skills/.
- New common projects are added to manifest.yaml with memory-bank + wiki sections.
- memory-bank/ is actively used and updated by the team for project context.
- Team adoption: 80%+ of developers actively using the hub (contributing or consuming) within 30 days.
- Follows KISS, consistency, and the global rules defined in this hub.

## Key Requirements
- Root: AGENTS.md (source of truth), CLAUDE.md (pointer)
- No code execution unless for skills; focus on Markdown/YAML for portability.
- All agent instructions must reference memory-bank for state.
- Prioritize refactoring/improving existing over new unless specified (but this is greenfield creation).
