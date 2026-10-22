---
name: lean-context
description: "Keep agent context small: extract only needed text with rg, jq, markitdown, and trafilatura; prefer targeted reads over full dumps."
version: 1.1.0
---

# lean-context

**Purpose**
Keep working context small by pulling only the slices an agent needs instead of dumping whole files, logs, or web pages into the transcript.

**Trigger**
Large logs or docs, HTML or PDF inputs, JSON blobs, or any task where reading everything would crowd out reasoning.

**Do not use for**
- Session-start memory-bank reads → `memory-bank-protocol`
- Explaining how a subsystem works end-to-end → `how`
- Writing docs or ADRs → `technical-writing` / `docs-protocol`

## Companions

| Skill | Role here |
|---|---|
| `how` | When extraction is done but the agent still needs architecture context |
| `show-me` | One visual shape of what was extracted (file tree, call tree) |
| `unslop` | Tight summaries written to files for later turns |

**Verification**
- Used `rg` / `jq` / converters before pasting large raw text into chat
- Wrote summaries or extracts to a file when output would exceed a few dozen lines
- Did not install tools with sudo on shared machines (`scripts/box-tools.sh` is user-space)

---

# Lean context

Agents forget and contexts fill up. Treat the transcript as precious: load pointers and extracts, not entire corpora.

## Tooling

Run `bash scripts/box-tools.sh --check` from the repo root to see which helpers are present. On a Linux box, install missing tools with `bash scripts/box-tools.sh --install` (add `--with-rtk` only when you need the optional `rtk` filter); it never uses sudo or edits shell rc files and installs under `~/.local`. On macOS use `brew install ripgrep jq` and `pip install --user markitdown trafilatura lxml_html_clean`.

| Tool | Use |
|---|---|
| `rg` | Find symbols, errors, or config keys; pass `-n` and a tight glob |
| `jq` | Slice JSON API responses; never pretty-print whole payloads into chat |
| `markitdown` | Convert office/PDF/HTML attachments to markdown for a bounded read |
| `trafilatura` | Extract main text from a URL when you need article body without chrome |
| `rtk` | Optional: shrink noisy command output before it hits the model |

## Workflow

1. **Scope** — State what you need (one function, one error line, one config key).
2. **Search** — `rg` with path globs; cap matches (`| head`) when exploring.
3. **Structured data** — `jq` with explicit keys; write large results to `/tmp` or `evidence/` and cite the path.
4. **Documents** — `markitdown` on the file; read headings and the section you need, not the whole conversion in chat.
5. **Web** — `trafilatura` or fetch-then-extract; summarize in your own words in ≤10 bullets.
6. **Summarize** — If the extract is still long, write a short summary file and point the next turn at it.

Prefer the editor read tool on a line range after `rg` tells you where to look. Avoid `cat` on large trees.

## Anti-patterns

- Pasting full CI logs, lockfiles, or OpenAPI specs into the transcript
- Reading every match from a repo-wide `rg` without narrowing
- Re-fetching the same URL every turn instead of saving the extract once

## Provenance

Hub skill distilled from shared lean-context practice (GMA-351). Last updated: 2026-10-22.
