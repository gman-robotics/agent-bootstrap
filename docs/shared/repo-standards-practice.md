# Repo standards skills (hub)

## When to run

| Situation | Skill |
| --- | --- |
| New manifest project; agents guess PR shape | `create-repo-standards` once per repo |
| CI renamed, new verify skill, ub-mode adopted | `maintain-repo-standards` (trigger only — no scheduled routine) |
| agent-bootstrap hub skill only | Use `close-out` + black-box gate — not `create-repo-standards` |

**Do not** run `create-repo-standards` against arbitrary third-party repos from the hub task runner; run it only when the user targets a project they own and the agent may write `.github/` and harness skill dirs.

## Reading agent-bootstrap at a pinned hub SHA

When the run must cite a specific hub commit (for example a `manifest.yaml` pin), use **one** of these and confirm the bytes came from that ref:

| Method | Command / URL |
| --- | --- |
| **Contents API** | `gh api repos/<owner>/<repo>/contents/<path>?ref=<full-40-char-sha>` (decode `content` as UTF-8) |
| **Raw.githubusercontent.com** | `https://raw.githubusercontent.com/<owner>/<repo>/<full-sha>/<path>` |
| **Tarball** | `gh api repos/<owner>/<repo>/tarball/<full-sha>` → extract archive to a temp dir |

Hub skills and shared docs live at `skills/<name>/SKILL.md` and `docs/shared/` — not under `.cursor/skills/` on the hub repo. Record the full SHA and the path(s) read in interview notes. Do not fetch by bare SHA with git.

## Tier scale (copy into generated standards skills)

| Tier | Meaning |
| --- | --- |
| **T0** | Small change, docs-only, or check-only (hub Markdown, typos, config tweak) |
| **T1** | Medium feature or fix in an existing module |
| **T2** | Larger feature, new module, or cross-cutting behavior change |
| **T3** | Infra, migration, or new service / major architectural move |

`create-repo-standards` copies this table into each generated `standards-<repo>` skill. Repeat tier hints in an HTML comment **under** the `Tier:` line in `.github/PULL_REQUEST_TEMPLATE.md` (not only in one top-of-file comment block).

## Generated artifact

`standards-<repo>/SKILL.md` only in harness folders the project **already uses** (do not create `.claude/`, `.grok/`, or Cline-only paths unless that harness is present).

Examples when those folders exist:

- `.cursor/skills/standards-my-app/SKILL.md`
- `.claude/skills/standards-my-app/SKILL.md`
- `.grok/skills/standards-my-app/SKILL.md`

GitHub: `.github/PULL_REQUEST_TEMPLATE.md` (per-header HTML hints), `.github/ISSUE_TEMPLATE/*` with `config.yml` limited to `blank_issues_enabled` and `contact_links`, optional `STANDARDS.md`.

## How each harness loads the local skill

| Harness | Discovery |
| --- | --- |
| Cursor | Project rules + `.cursor/skills/`; user may invoke `/standards-<repo>` when packaged |
| Claude Code | `~/.claude/skills/` symlinks or project `.claude/skills/` |
| Grok | `.grok/skills/standards-<repo>/` slash command when exported |
| Cline / Roo Code | Reads `.clinerules` at repo root (bootstrap pointer to `AGENTS.md`). It does **not** load `.cursor/skills/`. Point `.clinerules` or `AGENTS.md` at the on-disk `standards-<repo>/SKILL.md` path if you use Cline. |
| Hub cloud agent | Read project `AGENTS.md` (or README-inferred habits) + `standards-<repo>/SKILL.md` when `manifest.yaml` names the project |

Hub workflows (`plan-code-review-workflow`, `expert-pr-review`, `lfg`) say: **if** `standards-<repo>` exists for the active project, follow its PR/issue formats before APPROVE. Compatible with **advisory** ub-mode (`Gates:` line reports tool results; does not block APPROVE).

## PR header order (hub default)

When the project has no overriding `standards-<repo>` skill, copy `docs/shared/hub-pull-request-template.md` to `.github/PULL_REQUEST_TEMPLATE.md` and match `docs/shared/ub-mode-practice.md` header order.

Example Linear line (concrete): `Linear: https://linear.app/gman-personal-projects/issue/GMA-412` or `Linear: N/A`.

## Issue templates and labels

Before writing `.github/ISSUE_TEMPLATE/*`, list labels the repo actually has (`gh label list` or API). **Omit** a `labels:` key in a form when the label does not exist — GitHub rejects unknown labels. Add a question issue form only when a `question` label exists.

## Drift pass (`maintain-repo-standards`)

Use the explicit drift checklist in `skills/maintain-repo-standards/SKILL.md` (placeholders, tier table, CI pass bar step-for-step, test cites, per-header PR template hints, header order, `config.yml` keys, question label rule, skill id). Outcome **clean**, **changed**, or **blocked** — at most one PR when **changed**.

## Placeholder self-check

After generating or editing standards artifacts, strip HTML comments and grep for angle-bracket placeholders; output must be empty. See `create-repo-standards` step 5.

## Principles (names only)

See `skills/pstack-principles/SKILL.md`: **encode-lessons-in-structure**, **prove-it-works**, **sequence-verifiable-units**.
