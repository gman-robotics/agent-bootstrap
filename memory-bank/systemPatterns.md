# System Patterns: Multi-Agent Skills Hub

## Architecture Overview
The system is a **documentation-driven, file-based agent operating system**:
- **Single Source of Truth**: AGENTS.md at root — every agent loads this first. It references agents/, skills/, manifest.yaml, and memory-bank/.
- **Modular Roles (Subagents)**: Each role is a self-contained .md file in agents/ that an agent can "become" by loading its content. This enables dynamic persona switching within one session or across harnesses.
- **Skills as Workflows**: /skills/ contains executable playbooks (Markdown with steps, commands, decision trees). Agents follow them verbatim or adapt intelligently. Examples: expert-pr-review (critical QA), cherry-pick-to-release-branch (release ops), plan-code-review (core dev loop).
- **Multi-Project Context**: manifest.yaml is the registry. Agents parse it to know which projects exist, their tech stacks, paths (absolute), and dedicated memory-bank locations. Switching projects = load that project's memory-bank.
- **Knowledge Layer**: memory-bank/ provides persistent per-project context. Additional documentation can be added in memory-bank/ files as needed.
- **State Persistence**: memory-bank/ (this project's) + per-project memory-banks follow the exact 6-file hierarchy defined in the memory-bank-protocol skill and this hub's memory-bank/. Updated after every significant task. Non-optional read at session start.

## Key Design Patterns
- **Composition over Inheritance**: Roles compose (e.g., "Software Architect" uses "Plan Mode" pattern; "QA Reviewer" uses "Critical Review Checklist" from expert-pr-review skill).
- **Workflow Orchestration**: Standard dev loop is a state machine: PLAN (architect + user) → IMPLEMENT (engineer) → REVIEW (qa) → FIX (engineer) → APPROVE (qa) → UPDATE (memory-bank). Defined in skills/plan-code-review-workflow.md.
- **Context Injection**: AGENTS.md injects the global rules (defined in this hub), memory bank protocol, and "always use absolute paths", "KISS", "co-create plans for significant work".
- **Harness Compatibility Layer**: AGENTS.md has sections for "How to use with Claude Code", "Cline", "Open Code", etc. — simple copy-paste instructions. No harness-specific code.
- **Self-Improving System**: Agents are instructed to refactor skills and agents when better patterns emerge (prioritize improving existing over new per global rules).
- **Security & Safety**: All skills include critical constraints (e.g., "Review ONLY — never edit PR branch" from expert-pr-review). No destructive actions without explicit confirmation.

## Component Relationships
- AGENTS.md → loads/ references all others
- agents/*.md → loaded dynamically by role name in workflows
- skills/*.md → followed step-by-step; can call other skills
- manifest.yaml → parsed by agents to build project list + context switcher
- docs/ → persistent technical reference (api-contracts, data-models, pipeline, ADRs); navigated via `docs_path` in manifest.yaml
- memory-bank/ → read at start of every task (per core principle); updated at end

## Technical Decisions
- **Format**: Pure Markdown + YAML (maximum portability, no runtime deps, works in any editor/harness).
- **No Execution Engine**: Skills are human + LLM readable playbooks, not scripts (unless a skill needs bash — then use via terminal tool, but never auto-commit).
- **Versioning**: Skills and agents can have "Last updated" footers. manifest.yaml has version field.
- **Extensibility**: Easy to add new agent (copy template), new skill (follow existing format), new project (add to manifest).
- **KISS & Consistency**: Every file <500 lines where possible. Match the hub's skill styles exactly (friendly, direct, checklists, examples, warnings in > blocks).

## Constraints
- Internet disabled in sandbox → no external fetches in skills unless using provided tools.
- Never commit/push unless user explicitly says (global rule 6).
- Always request confirmation for deletions/destructive ops.
- For this creation task: since greenfield, we asked user implicitly by following their spec; now building per plan.
