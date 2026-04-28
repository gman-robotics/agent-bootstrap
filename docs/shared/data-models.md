# Shared Data Models

> **Scope**: Common entity definitions, field conventions, and data types used across all projects.  
> For project-specific schemas, see `docs/projects/<name>/data-models.md`.

---

## Common Field Conventions

All entities across all projects follow these baseline field standards:

### Universal Fields

Every persisted entity SHOULD have:

| Field | Type | Notes |
|---|---|---|
| `id` | `string` (UUID v4) | Primary key. Never expose auto-increment integers in APIs. |
| `created_at` | `string` (ISO 8601 UTC) | Set on creation, never mutated. |
| `updated_at` | `string` (ISO 8601 UTC) | Updated on every write. |
| `created_by` | `string` (UUID) | User ID of creator. Nullable for system-generated records. |

### Soft Delete Pattern

Prefer soft deletes for user-facing data:

| Field | Type | Notes |
|---|---|---|
| `deleted_at` | `string` (ISO 8601 UTC) or `null` | `null` = active. Set on delete, never truly remove the row. |
| `deleted_by` | `string` (UUID) or `null` | User ID of deleter. |

---

## Shared Entity Definitions

### User

Base user entity shared across projects that have user authentication.

```
User {
  id:           string (UUID)
  email:        string (lowercase, unique)
  display_name: string
  role:         enum [ADMIN, MEMBER, VIEWER]
  is_active:    boolean (default: true)
  created_at:   datetime
  updated_at:   datetime
  deleted_at:   datetime | null
}
```

### Organization / Team

For projects with multi-tenancy:

```
Organization {
  id:          string (UUID)
  name:        string
  slug:        string (URL-safe, unique)
  plan:        enum [FREE, PRO, ENTERPRISE]
  is_active:   boolean
  created_at:  datetime
  updated_at:  datetime
}

Membership {
  id:        string (UUID)
  user_id:   string (FK → User)
  org_id:    string (FK → Organization)
  role:      enum [OWNER, ADMIN, MEMBER]
  joined_at: datetime
}
```

---

## Type Conventions

| Concept | Type | Example |
|---|---|---|
| IDs | `string` (UUID v4) | `"a1b2c3d4-..."` |
| Timestamps | `string` ISO 8601 UTC | `"2025-04-28T17:00:00Z"` |
| Money / Currency | `integer` (cents/smallest unit) | `4999` = $49.99 |
| Percentages | `number` (0.0–1.0) | `0.75` = 75% |
| Counts | `integer` | `42` |
| Enums | `string` SCREAMING_SNAKE_CASE | `"PENDING_REVIEW"` |
| Flags | `boolean` | `true`, `false` |
| Free-form text | `string` | UTF-8 |
| Structured JSON | `object` | Document schema in project data-models |

---

## Validation Rules (Cross-Project Baseline)

| Field Type | Rule |
|---|---|
| Email | Lowercase, RFC 5322 compliant, max 254 chars |
| URL slug | `^[a-z0-9-]+$`, 3–50 chars, no leading/trailing hyphens |
| Display name | 1–100 chars, no leading/trailing whitespace |
| Free text (short) | Max 255 chars unless documented otherwise |
| Free text (long) | Max 10,000 chars unless documented otherwise |
| UUID | Must be valid UUID v4 format |

---

## Relationship Notation

Use this notation in project-specific data models:

```
EntityA {
  field: type     # inline comment if needed
}

EntityA 1--* EntityB (field_name)   # one-to-many via field_name FK
EntityA *--* EntityC via JoinTable  # many-to-many via join table
```

---

## Schema Change Process

1. Document the change in the relevant project's `docs/projects/<name>/data-models.md`.
2. If it affects a shared entity above, update this file and note the change date.
3. Create an ADR in `decisions.md` if the change is breaking or architectural.
4. Never change a field's type or remove a field without a migration plan and deprecation period.

---

*Last updated: 2026-04-28 | Update when shared entities or type conventions change*
