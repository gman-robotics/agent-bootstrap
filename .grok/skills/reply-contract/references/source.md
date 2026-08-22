---
name: reply-contract
description: "Use when status or your-turn. Write as if the user is new to the project."
version: 1.2.0
---

# reply-contract — Status and your-turn as if they just walked in

**Purpose**  
When more than one project is in flight, slash-jargon and heading walls both fail. Pair with **show-me** (trees / stacks / diffs). Do not reimplement those visuals here.

House style wins. Google / Apple / Red Hat only change voice and marks. See `references/style-sources.md`.

**Trigger**  
Status after another agent finished; “your turn”; smoke / tap-through; anything the human must do or decide; a longer explanation of a system they did not just build.

**Do not use for**  
One-word acks, tool dumps, or an in-session workout remaining card (that skill has its own format).

---

## Pick one visual (show-me)

Smallest view that makes the next action obvious. One primary visual per reply.

| Need | Visual | Photon / iMessage |
|------|--------|-------------------|
| Tap / click order | call tree | yes |
| Where the work sits | file/screen tree | yes |
| What changed | diff | yes |
| Who waits on whom | stack | yes |
| A human must approve/reject a held artifact | spec-gate card (below) | yes |
| A human must answer one question, not gate a decision | clarify card (below) | yes |
| Control flow (desktop/web) | mermaid | no unless asked |
| Dense UI / compare | one HTML file | no unless asked |

Photon/iMessage home: **bold + lists + fenced trees/diffs only.**

The tree *is* the sequence. If you skip the tree, number the steps. Never both. One step → a single bullet, not `1.`

## Gate cards

Two small markdown cards for the two things a human is asked to do mid-task. Both are **fenced text, not HTML, not a dashboard** — same Photon/iMessage-safe rule as every other visual here. Idea credit: a Scout memo comparing swarm-forge's dashboard spec-gate/clarify UI against this hub (`unclebob/swarm-forge`, ideas only — no files, prompts, or dashboard HTML copied; that repo carries no LICENSE). Rewritten here as plain reply-contract markdown.

**Rule: gate ≠ question.** A spec-gate card always resolves to a binary Approve/Reject on a held artifact. A clarify card always resolves to one answer to one question. Never put Approve/Reject on a clarify card, and never leave a spec-gate open-ended — if you need more than a yes/no, it is a clarify card (or a `grill-with-docs` round), not a gate.

### Spec-gate card

Use when a **held artifact** (plan, glossary, ADR, diff) needs a human stamp before the next phase starts — e.g. before `plan-code-review-workflow` CODE, or before `grill-with-docs` hands off to an implement skill. Never ask for this only in chat prose; use the card.

```text
**Spec gate** — spec → <next-phase> · <task-name>

Documents:
- `<path/to/doc-1>`
- `<path/to/doc-2>`

Approve · Reject
```

- `<next-phase>` — the phase this unblocks (`CODE`, `implement`, `PR`).
- `<task-name>` — the thread's stable Name (see **Task name** below); identical on every card for this thread.
- `Documents` — every artifact the human is stamping, named, not pasted inline.
- Reject → state what changes before re-presenting the same card; do not silently keep working.

### Clarify card

Use for one blocking question that is not a gate — you need a fact only the human has, not a decision on a held artifact.

```text
**Request clarification** — <task-name>

<question>

_Reply with your answer, then_ **Submit**.
```

- Pill label is always "Request clarification", never "Approve"/"Reject".
- One question per card. If several are ready, that is a `grill-with-docs` round (numbered ❓ format), not a clarify card.

## Task name

The first time a gate card (spec-gate or clarify) appears in a thread, pick one short Name (2–4 words, stable for the thread's life) and reuse it verbatim on every later card, in `grill-with-docs`, and in `close-out`'s Phase 1 handoff entry for this task. Do not rename mid-thread; if the work outgrows the name, say so explicitly and note the old name for continuity. This is naming discipline only — it is not the four-field envelope `task` field (see `adversarial-coordination-workflow` / `multi-harness-coordination`), though the two should carry the same value when both are in play.

## Content that must still be true

The visual is not a substitute for orientation. New facts must also exist in prose. Next to the visual:

1. **Project** — name + one sentence what it is
2. **Where it stands** — what just landed, in English (SHA after, not instead)
3. **Your turn** — the tree *is* the steps
4. **Words** — only jargon you used; prefer a plain word; if you keep the term, define once then reuse
5. **Leftover vs bug**
6. **Who is waiting**

Skip 3–6 if there is no human action.

## Voice

Write as if they just walked in from another project.

- Second person, active voice. Conditions before the tap.
- Imperative, one action per line. A tree plus four gloss lines beats a six-heading essay.
- Prefer a tree of screens/buttons over milestone codes as the lead.
- No “great” / “perfect” / restating a bot notification.
- No please / simply / easy / quickly / let’s / basically / “as expected” / “please note” / `!`
- No pre-announce. No promised ship date for a leftover.
- Sentence cap ~26 words. Serial commas. Spell out “and”.
- No idioms. Describe what happens (`a message appears`), not a sense (`you see`).
- Don’t use position or color as the only cue.

## Marks

- **Bold** labeled UI
- `code` for tokens, files, flags, SHAs, and values to type
- Placeholder the human must replace: `<value_name>` in code font
- Dates unambiguous (`2026-08-18`). Links name the target — never “click here”. `See` is fine.
- **Words** as a short description list, not a slash-run

## Bad / good

**Bad** — jargon wall

> Tap through: start fixture session → log/remaining/undo/swap-or-drop/close-out → sign out → A empty.

**Also bad** — six headings, no shape.

**Also bad** — numbered list *and* a tree.

**Good** — project line + show-me tree + gloss

> **Wod** is the iPhone workout app. Simulator is already open with the gym loop.
>
> ```text
> Simulator / Wod iPhone 17
>   **Profile** → sign in as A     # fake test user, not Google
>   **Today** → start today’s workout
>   **Session**
>     type two sets on one lift
>     leftover-set counts should move
>     undo last set → it vanishes
>     swap or drop one planned lift
>     close out: finished / short / missed
>   **Profile** → sign out
>   sign in as A again → history empty
> ```
>
> **Words**
> - leftover-set count — sets still owed
> - undo — take back the last typed set
> - close-out — mark the session done
>
> Extra sets still omit from close-out — known leftover. Backend work waits until the human says the loop feels right.

## Pitfalls

1. Slash-lists as the whole instruction
2. Six headings and no tree
3. Mermaid/HTML on Photon without being asked
4. Reimplementing show-me instead of loading it
5. Leading with SHAs / card ids
6. Defining every noun — only what you used
7. Numbered steps *and* a tree
8. New facts only inside the tree
9. Approve/Reject on a clarify card, or an open-ended spec-gate
10. Asking for a gate stamp only in chat prose instead of the card
11. Renaming the task mid-thread without saying so

## Verification

- [ ] show-me loaded when the reply needed more than three sentences
- [ ] One primary visual; channel-legal
- [ ] A new-to-the-thread reader could do the next action
- [ ] Jargon in the reply is glossed or replaced
- [ ] UI is bold; tokens are `code`
- [ ] Who is blocked on the human is explicit, or there is no human action
- [ ] Gate cards used only for held artifacts; clarify cards only for questions — never mixed
- [ ] Task name (if any card used) is stable across this thread
