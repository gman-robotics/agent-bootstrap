---
name: grill-with-docs
description: "Use when aligning on a plan or design before code: grill the user in rounds, keep CONTEXT.md as a glossary, and offer ADRs only for hard-to-reverse trade-offs. Do not implement until the user confirms shared understanding."
version: 1.0.0
---

# grill-with-docs — Align, then write the language down

**Purpose**
Close the communication gap *before* anyone writes code. Interview until the design tree is empty. Capture **terms** in `CONTEXT.md` as they resolve. Offer an ADR only when the decision is hard to reverse.

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (`grill-with-docs` + `grilling` + `domain-modeling`, MIT). Native hub playbook — not an `npx skills add` copy. Matt’s original is a two-skill router; this file is the combined procedure.

**Trigger**
“Grill this”, “grill-with-docs”, “align on the domain”, “build CONTEXT.md”, or any change where the agent might build the wrong thing.

**Do not use for**
- A change the user already accepted and wants coded → `plan-code-review-workflow`
- Status / your-turn → `reply-contract`
- A whole-repo representation audit → `codebase-simplification-audit`
- Recording an ADR the user already decided, no interview → `docs-protocol`

---

## Hard rule — no implement until they confirm

Until the user **explicitly confirms** shared understanding (“yes, that’s it”, “implement”, “go”):

1. **Do not** invoke `plan-code-review-workflow`, `write-tests`, `task-loop-7-phase`, or any implementer role.
2. **Do not** start a feature branch, open a PR, or “just scaffold.”
3. Allowed writes: `CONTEXT.md` / `CONTEXT-MAP.md` (glossary only) and an ADR you **offered and they accepted**.
4. **Do not** treat `CONTEXT.md` as a spec, scratch pad, or implementation dump.

After confirm: stop this skill. Load `plan-code-review-workflow` + `write-tests` for the agreed slice only.

---

## Companions

| Skill | Role here |
|---|---|
| `docs-protocol` | If the project already records decisions under `docs/projects/<name>/`, put the ADR there instead of a second tree |
| `memory-bank-protocol` | Session state stays in the bank. `CONTEXT.md` is **domain language**, not progress |
| `reply-contract` | Present the “frontier empty — confirm?” close as if they just switched projects |
| `subagent-routing` | Look up **facts** yourself (or via a cheap worker). Never ask the user what you can read |

---

## Words

- **Fact** — true of the environment (code, files, tickets). Your job. Look it up.
- **Decision** — a choice only the user can make. Put it to them.
- **Frontier** — decisions whose prerequisites are already settled. Ask the whole frontier this round.
- **Glossary** — `CONTEXT.md`. What a term *is*. Not how it is implemented.

---

## Steps

### 1. Orient

Read, if they exist: root `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/adr/`, project `docs_path` from `manifest.yaml`, hot memory-bank files.

If `CONTEXT-MAP.md` exists, pick the context for this topic (ask if unclear).

**Done when:** you know which glossary file you will update, or that none exists yet.

### 2. Grill in rounds

Map the work as a **design tree**. Each decision branches into the ones that hang off it.

Each round:

1. Compute the frontier. A question that depends on an unanswered question this round belongs to a *later* round.
2. Ask **every** frontier question in one message. Number them. Give your recommended answer.
3. Wait. Do not start the next round until they answer.

Format:

```text
❓ **Q1** - **<title>**: <body; choices if useful>

➡️ <your recommended answer>
```

Facts: dispatch a lookup; do not block the rest of the frontier on it. Downstream questions wait; the others go now.

Challenge fuzzy or conflicting language immediately. If they say a term that contradicts `CONTEXT.md` or the code, surface it: “glossary says X, you just said Y — which is it?”

**Done when:** the frontier is empty — every branch visited, nothing silently assumed.

### 3. Write the language down (as terms resolve)

When a term is settled, update `CONTEXT.md` **now** (create lazily). Format: `references/context-format.md`.

Rules:

- Opinionated: pick one word; list aliases under `_Avoid_`.
- One or two sentences. What it *is*, not what it does.
- Only terms unique to this project’s domain. No general programming vocabulary.
- No implementation details.

Offer an ADR only when **all three** are true:

1. Hard to reverse
2. Surprising without context
3. A real trade-off (rejected alternatives worth remembering)

If any is missing, skip. Format: `references/adr-format.md`. Default path `docs/adr/NNNN-slug.md` (scan highest number, increment). If this project already uses `docs-protocol` decisions, add there instead.

**Done when:** every resolved term is in the glossary; offered ADRs are written or explicitly declined.

### 4. Stop and confirm

Use `reply-contract`. Show: settled decisions, glossary/ADR paths touched, leftover open questions (should be none).

Ask: **confirm shared understanding** before any implement skill.

---

## Common pitfalls

1. Asking the user for a fact you could `rg`.
2. One question per message when the whole frontier is ready.
3. Dumping a spec into `CONTEXT.md`.
4. Starting `plan-code-review-workflow` because the last answer “felt like go.”
5. An ADR for an easy-to-reverse or obvious choice.
6. Batching glossary updates until the end (they get lost).

---

## Verification checklist

- [ ] Frontier empty; no silent assumptions
- [ ] Facts looked up; only decisions asked
- [ ] `CONTEXT.md` is glossary-only
- [ ] ADRs only when all three tests passed (or none offered)
- [ ] Did **not** invoke implement skills
- [ ] User must confirm before any code change beyond glossary/ADR

*Last updated: 2026-08-16 | Hub version: 0.6.0*
