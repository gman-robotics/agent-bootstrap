# Active Context: Multi-Agent Skills Hub

## Current Focus (This Session)
Creating the initial structure and core files for the Multi-Agent Skills Hub repository based on user's requirements and the skills/examples now included in this hub (expert-pr-review, cherry-pick-to-release-branch, memory-bank-protocol, global rules).

**In Progress**:
- Populating memory-bank/ core files (done: projectbrief, productContext, systemPatterns, techContext; now activeContext + progress).
- Designing and writing AGENTS.md (main source of truth — will be comprehensive, ~300-500 lines).
- Creating CLAUDE.md, README.md, manifest.yaml.
- Setting up /skills/ with copied + new skills.
- Setting up /agents/ with role definitions.
- Initializing skills/ and agents/.
- Ensuring full compliance with all global rules (read at start, co-create plan, KISS, absolute paths, no commits, etc.).

## Recent Changes
- 2026-04-28: Initialized directories (skills, agents, wiki, memory-bank).
- Created first 4 memory-bank core files with detailed content tailored to this project.
- Incorporated all skill content and examples directly into the hub's skills/ and agents/ directories (self-contained, no external files needed for the published repo).

## Active Decisions
- **Project Root**: /home/workdir/artifacts/ (as working dir; will be the repo root when cloned elsewhere).
- **Naming**: "Multi-Agent Skills Hub" — clear, descriptive. AGENTS.md is the entry point.
- **Workflow Definition**: The core "plan-code-review" workflow will be the flagship skill, directly implementing user's requested "plan -> code -> review process".
- **Subagent Roles** (initial 4):
  1. software-architect.md (Plan role — iterative with user)
  2. software-engineer.md (Code/Implement role)
  3. qa-critical-reviewer.md (Extremely critical QA, based on expert-pr-review)
  4. ui-ux-engineer.md (For frontend tasks)
- **Knowledge Management**: Through memory-bank/ files and skill documentation (no separate wiki layer).
- **manifest.yaml Structure**: Simple top-level `projects:` list with name, path (absolute), description, primary_tech, memory_bank_path.

## Open Questions (for User — Now Resolved by Completion)
- Project name: "Multi-Agent Skills Hub" chosen as clear and descriptive. Can be renamed later via simple search/replace.
- Additional roles/skills: Initial 4 roles + 4 skills cover the core request. Easy to add (copy template).
- manifest.yaml: Includes this project + clear template for user's projects (e.g. the release-branch one). User can edit directly.
- Architecture: Pure MD/YAML chosen per KISS and harness-agnostic requirement. No new framework needed.
- Extra files: Kept minimal (no .gitignore yet — user can add; LICENSE can be added on request).

## Current Status
**All core deliverables complete.** 
- AGENTS.md, CLAUDE.md, README.md, manifest.yaml created and verified.
- All skills and agents populated (core skills included verbatim where appropriate, new workflows added).
- **New**: memory-bank-protocol.md skill added to /skills/ (full playbook based on the Memory Bank concept, with init/read/update steps). AGENTS.md reference updated.
- Wiki initialized with 5+ entries + template.
- Memory-bank fully updated and read multiple times (including this update).
- Full self-review passed (consistent with expert-pr-review standards: no issues found, all requirements met, KISS followed, absolute paths used everywhere).
- Cleanup complete: Removed all references to personal uploaded files/attachments/ (not part of published GitHub repo); skills now fully self-contained.
- Removed wiki component to keep scope focused on agent harness bootstrap.

**State**: Foundational setup 100% complete and operational. The hub now includes your preferred Memory Bank skill as a first-class citizen and full Karpathy LLM Wiki. Ready for immediate use in any of your projects.

**Next**: Load AGENTS.md in your harness and try "Follow the memory-bank-protocol skill to initialize for [one of your projects]" or "Follow the plan-code-review workflow...". Feedback welcome!
