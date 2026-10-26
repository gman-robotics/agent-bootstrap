# Repo standards skills (hub)

## When to run

| Situation | Skill |
| --- | --- |
| New manifest project; agents guess PR shape | `create-repo-standards` once per repo |
| CI renamed, new verify skill, ub-mode adopted | `maintain-repo-standards` (trigger only — no scheduled routine) |
| agent-bootstrap hub skill only | Use `close-out` + black-box gate — not `create-repo-standards` |

**Do not** run `create-repo-standards` against arbitrary third-party repos from the hub task runner; run it only when the user targets a project they own and the agent may write `.github/` and harness skill dirs.

## Generated artifact

`standards-<repo>/SKILL.md` in project harness folders, for example:

- `.cursor/skills/standards-my-app/SKILL.md`
- `.claude/skills/standards-my-app/SKILL.md`
- `.grok/skills/standards-my-app/SKILL.md`

GitHub: `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/*`, optional `STANDARDS.md`.

## How each harness loads the local skill

| Harness | Discovery |
| --- | --- |
| Cursor | Project rules + `.cursor/skills/`; user may invoke `/standards-<repo>` when packaged |
| Claude Code | `~/.claude/skills/` symlinks or project `.claude/skills/` |
| Grok | `.grok/skills/standards-<repo>/` slash command when exported |
| Cline / Roo Code | Reads `.clinerules` at repo root (bootstrap pointer to `AGENTS.md`). It does **not** load `.cursor/skills/`. Point `.clinerules` or `AGENTS.md` at the on-disk `standards-<repo>/SKILL.md` path if you use Cline. |
| Hub cloud agent | Read project `AGENTS.md` + `standards-<repo>/SKILL.md` when `manifest.yaml` names the project |

Hub workflows (`plan-code-review-workflow`, `expert-pr-review`, `lfg`) say: **if** `standards-<repo>` exists for the active project, follow its PR/issue formats before APPROVE. Compatible with **advisory** ub-mode (`Gates:` line reports tool results; does not block APPROVE).

## PR header order (hub default)

When the project has no overriding `standards-<repo>` skill, match `docs/shared/ub-mode-practice.md`: `Tier:`, `Models:`, `Linear:` (`https://linear.app/...` or `N/A`), `Summary:`, `Gates:`, then evidence/checklist.

## Principles (names only)

See `skills/pstack-principles/SKILL.md`: **encode-lessons-in-structure**, **prove-it-works**, **sequence-verifiable-units**.
