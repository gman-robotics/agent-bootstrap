---
name: reflect
description: "Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect."
version: 1.0.0
---

# reflect

**Purpose**
Mine the active transcript for durable learnings and route approved items to concrete skill edits.

**Trigger**
User says "reflect" after substantive work worth institutionalizing.

**Do not use for**
- Trivial or off-topic conversations
- One-off preferences → `automate-me` mode skill instead

## Companions

| Skill | Role here |
|---|---|
| `docs-protocol` + `close-out` Step 8 | Hub skill authoring for substantive edits |
| `pstack-principles` | encode-lessons-in-structure — prefer lint/script over prose when possible |
| `reply-contract` | User approval before applying Accepted items |

**Verification**
- Three reviewers spawned in parallel; synthesizer output presented before edits
- Touched skills pass environment validator when available

---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

## When to invoke

Invoke when the user says "reflect" or "reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## Process

### 1. Locate the active transcript

The parent finds its own transcript file before fanning out. The system prompt names the active workspace's `harness transcript storage for the active workspace` directory. Use that path. Do not glob across unrelated workspace transcript roots. That crosses workspace boundaries and reads private chats from unrelated projects.

```bash
ls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10
```

Three transcript layouts: legacy flat (`<id>.jsonl`), current nested (`<id>/<id>.jsonl`), and subagent (`<parent>/subagents/<child>.jsonl`).

For each candidate, read the first JSONL line and check that `message.content[0].text` contains the conversation's opening user prompt. Take the matching path. If no path resolves, write a tight digest of the session and pass that instead.

### 2. Spawn three reviewers in parallel

One message, three `Task` calls, `subagent_type: generalPurpose`, explicit `model:` on each, agent mode (`readonly: false`). Reviewers need MCP access for context lookups (tickets, chat threads, observability traces referenced in the transcript). Readonly strips MCPs.

| Lens | `model` | Prompt template |
|---|---|---|
| Judgment | your configured reflect-judgment model (default Sonnet-tier model (see skills/subagent-routing/SKILL.md)) | `references/judgment-reviewer.md` |
| Tooling | your configured reflect-tooling model (default Sonnet-tier model (see skills/subagent-routing/SKILL.md)) | `references/tooling-reviewer.md` |
| Divergent | your configured reflect-judgment model (default Sonnet-tier model (see skills/subagent-routing/SKILL.md)) | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in the `Task` response body.

### 3. Synthesize

One `Task` call, `subagent_type: generalPurpose`, using your configured reflect-judgment model (default Sonnet-tier model (see skills/subagent-routing/SKILL.md)), agent mode (`readonly: false`). The synthesizer's quality check includes spot-verifying citations, which can require MCP access. Readonly strips MCPs. Use `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. The synthesizer returns a structured Accepted / Rejected / Backlog list.

### 4. Structural enforcement check

Sanity-check the synthesizer's Accepted list. For any item that would be enforced more reliably by a lint rule, script, metadata flag, or runtime check, move it from Accepted to Backlog. See the **pstack-principles** (encode-lessons-in-structure) principle.

### 5. Apply

Before applying any Accepted edit, present the synthesizer's full Accepted/Rejected/Backlog output to the user and wait for explicit approval. The user picks which subset to apply and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

Backlog items file to whatever devex / backlog tracker your team uses automatically. Only the Accepted list waits for approval.

For each approved Accepted item, follow the Routing field exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): parent does directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): follow hub skill authoring (`skills/docs-protocol/SKILL.md` + `skills/close-out/SKILL.md` Step 8).
- `tune description: <skill path>`: revise frontmatter `description` per `docs-protocol` trigger guidance.
- `new skill: <kebab-name>`: create under `skills/<kebab-name>/` per `docs-protocol`; do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done. Skip this step if it doesn't.

### 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.

## Provenance

Adapted from [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT). Native multi-harness hub playbook — not a marketplace plugin copy. Cursor-only harness names stripped per `skills/subagent-routing/SKILL.md`.

*Last updated: 2026-09-15 | Hub version: 0.11.0*
