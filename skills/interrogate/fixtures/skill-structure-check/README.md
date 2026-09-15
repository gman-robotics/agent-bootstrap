# skill-structure-check

Runs `scripts/validate_pstack_skill.py <skill-name>` — valid YAML frontmatter (`yaml.safe_load`), MIT provenance, house-adapt sections (Purpose / Do not use / Companions / Verification), and rejection of leftover Cursor-only tokens (`.cursor/skills`, `~/.cursor/projects`, required `environment: "cloud"`, bare `create-skill`).
