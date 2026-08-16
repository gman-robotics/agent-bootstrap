# CONTEXT.md format

Used by `grill-with-docs`. Glossary only — not a spec, not memory-bank, not implementation notes.

## Single-context repo (usual)

Root `CONTEXT.md`:

```md
# {Context Name}

{One or two sentences: what this context is and why it exists.}

## Language

**Order**:
{One or two sentences: what it IS.}
_Avoid_: Purchase, transaction

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

## Rules

- Pick one word. List the rest under `_Avoid_`.
- Tight definitions. What it is, not what it does.
- Only terms unique to this project’s domain. Timeouts, error types, and utility patterns do not belong.
- Group under subheadings when clusters appear; otherwise a flat list.

## Multi-context repo

If `CONTEXT-MAP.md` exists at the root, it lists contexts and relationships:

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md) — invoices and payments

## Relationships

- **Ordering → Billing**: shared `CustomerId`; Billing does not own Customer
```

Infer:

- `CONTEXT-MAP.md` present → read it, update the matching context
- only root `CONTEXT.md` → single context
- neither → create root `CONTEXT.md` when the first term resolves

Create files lazily.

Adapted from mattpocock/skills `domain-modeling/CONTEXT-FORMAT.md` (MIT).
