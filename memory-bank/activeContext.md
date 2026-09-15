# Active Context: Multi-Agent Skills Hub

## Current Focus (This Session)
**GMA-48 — Port Cursor pstack shortlist into agent-bootstrap** (2026-09-15, cloud agent, branch `cursor/port-pstack-skills-dc70`). Fresh port from `main`; prior cancelled run not assumed.

**What shipped (this branch, pre-merge)**:
- 16 adapted workflow skills under `skills/`: architect, arena, swarm, blast-radius, interrogate, figure-it-out, show-me-your-work, create-verification-skill, maintain-verification-skill, how, why, teach, technical-writing, unslop, reflect, automate-me
- Combined `skills/pstack-principles/` with high-leverage principles + **hard carve-out**: never-block-on-the-human does not override literal Approve/Reject spec-gate cards
- MIT provenance in each skill's Provenance section (source: https://github.com/cursor/plugins/tree/main/pstack)
- Cursor-only harness names stripped; multi-harness language via `skills/subagent-routing/SKILL.md`
- `skills/INDEX.md` + `AGENTS.md` §4 + all five harness trigger files updated
- `scripts/export_codex_skills.py` SkillConfig entries + `.grok/skills/` re-export
- Live gate: `scripts/validate_pstack_skill.py` + per-skill fixtures + `tests/test_pstack_skills.py` (99/99 tests pass)
- Skipped per task: poteto-mode, setup-pstack, poteto-agent, bro, make-bot-ui, recall, no-comments, comment-sicko, individual principle-* skills

**Verification**: `python3 -m unittest discover -s tests` — 99/99 pass. `python3 scripts/index_skills.py` — all non-grandfathered INDEX entries live-eligible.

**Next**: Draft PR for Blair review; do not merge.
