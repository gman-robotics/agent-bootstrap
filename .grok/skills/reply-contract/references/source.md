---
name: reply-contract
description: "Use when status or your-turn. Write as if the user is new to the project."
version: 1.1.0
---

# reply-contract — Status and your-turn as if they just walked in

**Purpose**  
When more than one project is in flight, slash-jargon and heading walls both fail. Pair with **show-me** (trees / stacks / diffs). Do not reimplement those visuals here.

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
| Control flow (desktop/web) | mermaid | no unless asked |
| Dense UI / compare | one HTML file | no unless asked |

Photon/iMessage home: **bold + lists + fenced trees/diffs only.**

## Content that must still be true

The visual is not a substitute for orientation. Next to it:

1. **Project** — name + one sentence what it is
2. **Where it stands** — what just landed, in English (SHA after, not instead)
3. **Your turn** — the tree *is* the steps
4. **Words** — only jargon you used, one line each
5. **Leftover vs bug**
6. **Who is waiting**

Skip 3–6 if there is no human action.

## Voice

- Assume they do not remember this project’s vocabulary
- Prefer a tree of screens/buttons over milestone codes as the lead
- A tree plus four gloss lines beats a six-heading essay
- No “great” / “perfect” / restating a bot notification

## Bad / good

**Bad** — jargon wall

> Tap through: start fixture session → log/remaining/undo/swap-or-drop/close-out → sign out → A empty.

**Also bad** — six headings, no shape.

**Good** — project line + show-me tree + gloss

> **Wod** is the iPhone workout app. Simulator is already open with the gym loop (today’s workout → type sets → finish the day).
>
> ```text
> Simulator / Wod iPhone 17
>   Profile → sign in as A          # fake test user, not Google
>   Today → start today’s workout
>   Session
>     type two sets on one lift
>     leftover-set counts should move
>     undo last set → it vanishes
>     swap or drop one planned lift
>     close out: finished / short / missed
>   Profile → sign out
>   sign in as A again → history empty
> ```
>
> **Words:** leftover-set count = sets still owed. undo = take back last typed set. swap/drop = change or remove a planned lift. close-out = mark the session done.
>
> Extra/bonus sets still omit from close-out — known leftover. Backend work waits until the human says the loop feels right.

## Pitfalls

1. Slash-lists as the whole instruction
2. Six headings and no tree
3. Mermaid/HTML on Photon without being asked
4. Reimplementing show-me instead of loading it
5. Leading with SHAs / card ids
6. Defining every noun — only what you used

## Verification

- [ ] show-me loaded when the reply needed more than three sentences
- [ ] One primary visual; channel-legal
- [ ] A new-to-the-thread reader could do the next action
- [ ] Jargon in the reply is glossed or replaced
- [ ] Who is blocked on the human is explicit, or there is no human action
