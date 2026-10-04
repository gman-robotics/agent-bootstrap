---
name: recall
description: "Rebuild recent working context into a tight current-state brief before starting or resuming work. Use for /recall, catch me up, where did I leave off."
version: 1.0.0
---

# recall

**Purpose**
Hand back a current-state capsule from live git/GitHub state, the shared record, and optional local transcripts. Do not reconstruct a feature only from chat.

**Trigger**
"/recall", "catch me up", "where did I leave off", "what have I been working on", before starting or resuming a named topic.

**Do not use for**
- Session-start memory-bank reads with no named topic → `memory-bank-protocol`
- Why a subsystem was built this way → `why` (this skill calls it for the shared-record sweep)
- Turning habits into a skill → `automate-me`
- One specific in-flight session to resume, when the user already named the branch and files → use that capsule and skip mining

## Companions

| Skill | Role here |
|---|---|
| `why` | Shared-record sweep: what shipped, what reverted, what users still report |
| `memory-bank-protocol` | Hot files (`activeContext`, `progress`) when the topic is a manifest project |
| `unslop` | Write the brief without AI tells |
| `pr-shepherd` | Live PR classification when the topic is merge state |

**Verification**
- Scope was stated before search (window, topic, workspace)
- Live `git` / `gh` checked every PR, branch, and ticket the brief names
- Output matches the contract below
- Private context stripped before any public output

---

# Recall

Lock the scope first. "Recent" is a real range, default the last 7 days. Name the topic and the workspace. State the scope back. Do not turn "all" into "recent N".

Two records. Chat history holds what this operator decided. The shared record holds symptoms, shipped fixes, reverts, and errors still firing. A feature with a long bug tail keeps most of its story in the second record, so do not reconstruct it from transcripts alone.

1. If the user already gave paths, branch, and the change, use that capsule and stop.
2. Read `memory-bank/activeContext.md` and `memory-bank/progress.md` for the named project.
3. Sweep the shared record with `why`, steered to current state, what was tried and did not hold, and what is still reported. One investigator per source. A null result is a finding. Skip an unavailable source and say so.
4. Optional local transcripts, only for the active workspace, only when a transcript root exists. On Cursor, transcripts live under the user Cursor projects directory, one folder per workspace slug (leading slash dropped, each slash turned into a hyphen), in `agent-transcripts/`. Order by modification time, grep the topic, read matching regions only. Do not glob other workspaces. On harnesses without that root, skip and say so.
5. Verify PRs, branches, and tickets with `git` and `gh`.

## Output contract

- **Capsule.** At most 5 bullets. What this work is and where it stands.
- **Threads.** One line each, prefixed with exactly one tag: `[merged #N]`, `[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`, `[reverted #N]`, or `[planned, not started]`.
- **Problems.** At most 5 recurring ones, including reverted fixes.
- **Next move.** One concrete action.

Write through `unslop`. Cite chat findings by id and shared-record findings by PR, ticket, or permalink.

## Provenance

Adapted from [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT), pstack 0.15.9 (2026-10-03). Native multi-harness hub playbook — not a marketplace plugin copy. Cursor-only harness names stripped per `skills/subagent-routing/SKILL.md`.

*Last updated: 2026-10-03 | Hub version: 0.12.0*

