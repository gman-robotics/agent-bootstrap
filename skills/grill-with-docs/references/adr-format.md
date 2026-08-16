# ADR format (grill-with-docs)

Default location: `docs/adr/`. Sequential names: `0001-slug.md`, `0002-slug.md`. Create the directory only when the first ADR is needed.

If the project already records decisions via `docs-protocol` (`docs/projects/<name>/decisions.md` or `docs/shared/decisions.md`), add the entry there instead of starting a second tree.

## Template

```md
# {Short title}

{1–3 sentences: context, what we decided, why.}
```

A paragraph is enough. Record *that* a decision was made and *why*.

## Optional (only if they earn their space)

- **Status:** `proposed` | `accepted` | `deprecated` | `superseded by ADR-NNNN`
- **Considered options** — rejected alternatives worth remembering
- **Consequences** — non-obvious downstream effects

## Numbering

Scan the ADR directory for the highest number; increment by one.

## Offer an ADR only when all three are true

1. Hard to reverse
2. Surprising without context
3. A real trade-off

Skip easy reversals, obvious choices, and “we did the only thing.”

### Usually qualifies

- Architectural shape (monorepo, event-sourced write model, …)
- How contexts talk (events vs sync HTTP)
- Lock-in tech (database, bus, auth, deploy target) — not every library
- Ownership boundaries and explicit no-s
- Deliberate deviations from the obvious path
- Constraints the code does not show (compliance, latency contracts)

Adapted from mattpocock/skills `domain-modeling/ADR-FORMAT.md` (MIT).
