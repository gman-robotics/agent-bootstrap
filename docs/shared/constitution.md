# Constitution — New Invariants

> **Scope**: Team-wide, short. Records **new** invariants only — rules not already covered by an existing skill, standard, or ADR. This file is not the pointer to the hub; `AGENTS.md` remains the single source of truth for all agent instructions. See `AGENTS.md` §2 and `skills/INDEX.md` for the full rule set.

Each article is a short, testable rule plus the skill(s) that enforce it. No article restates a whole skill; it names the invariant and points at where it lives operationally. Add new articles at the bottom, numbered sequentially. Do not rewrite an existing article — supersede it explicitly and say so.

Provenance note: the invariants below were prompted by a Scout memo comparing `unclebob/swarm-forge`'s coordination format against this hub. Ideas only — no files, prompts, scripts, or dashboard HTML were copied. That repo carries no LICENSE, so nothing from it is vendored, quoted at length, or assumed to carry a license here.

---

## Article 1 — Spec gate

**Scope**: this article binds only the card-using skills/personas named under **Enforced by** below — it is not a claim that every phase-transition gate in the hub already uses the card. A skill not listed there is out of scope until it is migrated; that is a gap to close in a future change, not a silent exception to this article.

Within scope, a held artifact (plan, glossary, ADR, diff) that gates a phase transition must be stamped by a human with a binary **Approve** or **Reject** against a named `Documents` list — never approved implicitly by silence, and never requested only in chat prose. Two refinements close the common ways this gets faked:

- **The stamp is the literal word.** Only an explicit **Approve** or **Reject** counts. "Ok", "looks good", "sounds right", or silence are not a stamp; re-present the same card.
- **No leftover questions beside Approve.** A card must not show `Approve` while an open question from the same session sits next to it. Resolve every question first (another grill round, or a clarify card for one blocking fact) — a card with leftovers is not ready to gate anything.

**Enforced by**: `skills/reply-contract/SKILL.md` (spec-gate card format), `skills/grill-with-docs/SKILL.md` (Step 4, before any implement skill), `agents/software-architect.md` (Plan-phase closer), `AGENTS.md` §4 PLAN (points here instead of a chat-prose question).

**Explicitly out of scope (not migrated by this article)**: `skills/plan-code-review-workflow/SKILL.md`'s own literal Phase 1 Step 5 text still asks in chat prose. That file is intentionally not rewritten here; when its Architect role is played via `agents/software-architect.md`, the persona's card closer applies, but the workflow file's own wording is unchanged pending a dedicated update.

## Article 2 — Clarify is not a gate

A single blocking question that needs a fact, not a decision on a held artifact, must never carry Approve/Reject. Use the clarify card (question + one-line answer + Submit) instead.

**Enforced by**: `skills/reply-contract/SKILL.md` (clarify card format), `skills/grill-with-docs/SKILL.md`.

## Article 3 — Stable task name

Once a thread has a gate card, it has exactly one short task Name for its life, reused verbatim on every later card and in the close-out handoff entry. Renaming mid-thread must be explicit, with the old name noted.

**Enforced by**: `skills/reply-contract/SKILL.md` ("Task name"), `skills/close-out/SKILL.md` (Step 1), `skills/grill-with-docs/SKILL.md`.

## Article 4 — Envelope stanza is descriptive, not a bus

A four-field markdown stanza (`type` / `to` / `priority` / `task`) may head a handoff or finding as a quick-triage aid. It is plain markdown, never a message-bus contract: no SHA-based identity, no outbox file paths, no stdout `TASK:`/`NO_TASK` helper convention, no auto-generated bodies.

**Enforced by**: `skills/adversarial-coordination-workflow/SKILL.md`, `skills/multi-harness-coordination/SKILL.md`.

## Article 5 — No vendored runtime from unlicensed sources

Ideas may be adapted in-house from a repository with no LICENSE (e.g. `unclebob/swarm-forge`); files, scripts, prompts, dashboard HTML, or constitution `.prompt` files from such a repository may never be copied or vendored, and no LICENSE is invented on their behalf. Cite the source repo and the idea in the PR body, not as copied text.

**Enforced by**: this file (provenance note above), PR review discipline in `skills/expert-pr-review/SKILL.md`.

---

*Last updated: 2026-08-22 | Pointer only — `AGENTS.md` remains the single source of truth for all agent instructions.*
