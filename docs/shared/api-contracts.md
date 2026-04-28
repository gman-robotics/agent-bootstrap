# Shared API Contracts

> **Scope**: Team-wide API standards and conventions that apply across all projects.  
> For project-specific endpoints, see `docs/projects/<name>/api-contracts.md`.

---

## API Design Conventions

### URL Structure
- Use `kebab-case` for all URL segments: `/api/v1/user-profiles`
- Version prefix all public APIs: `/api/v1/`, `/api/v2/`
- Use plural nouns for resource collections: `/users`, `/projects`
- Nest sub-resources up to 2 levels deep max: `/users/{id}/settings`

### HTTP Methods
| Method | Use |
|---|---|
| `GET` | Read (never mutates state) |
| `POST` | Create resource or non-idempotent action |
| `PUT` | Full replacement of a resource |
| `PATCH` | Partial update of a resource |
| `DELETE` | Remove a resource |

### Request Conventions
- Content-Type: `application/json` for all request bodies
- Authentication: Bearer token in `Authorization` header
- Pagination: `?page=1&limit=50` (default limit: 50, max: 200)
- Filtering: Query params, e.g. `?status=active&created_after=2025-01-01`

### Response Conventions

**Success envelope:**
```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "limit": 50,
    "total": 243
  }
}
```

**Error envelope:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [
      { "field": "email", "issue": "must be a valid email address" }
    ]
  }
}
```

### HTTP Status Codes
| Code | Use |
|---|---|
| `200` | Success (GET, PATCH, PUT) |
| `201` | Created (POST) |
| `204` | No content (DELETE) |
| `400` | Bad request / validation error |
| `401` | Unauthenticated |
| `403` | Forbidden (authenticated but not authorized) |
| `404` | Not found |
| `409` | Conflict (e.g., duplicate resource) |
| `422` | Unprocessable entity |
| `429` | Rate limited |
| `500` | Internal server error |

---

## Authentication Standards

### Bearer Token
All authenticated endpoints expect:
```
Authorization: Bearer <token>
```

### Token Lifecycle
- Access tokens: short-lived (project-specific, see project docs)
- Refresh tokens: long-lived (project-specific)
- Token format: JWT (preferred) or opaque (document in project api-contracts)

---

## Field Naming Conventions

- **JSON fields**: `snake_case`
- **IDs**: `string` UUIDs (not integers) — portable across services
- **Timestamps**: ISO 8601 UTC — `"2025-04-28T17:00:00Z"`
- **Booleans**: `is_` prefix — `is_active`, `is_deleted`
- **Counts**: `_count` suffix — `user_count`, `item_count`
- **Enum values**: `SCREAMING_SNAKE_CASE` — `"status": "PENDING_REVIEW"`

---

## Versioning Strategy

- Increment major version (`v1` → `v2`) for breaking changes
- Maintain previous version for minimum 6 months after deprecation notice
- Deprecation notice: Add `Deprecation` and `Sunset` headers to deprecated endpoints
- Document breaking changes in the relevant project's `decisions.md`

---

## Rate Limiting

Document per-project in project api-contracts. Minimum standards:
- Always return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers
- Use `429 Too Many Requests` with `Retry-After` header

---

## Cross-Origin (CORS)

- Allow origins: configured per environment (dev: localhost, prod: allow-listed domains)
- Never use wildcard `*` in production for authenticated APIs

---

*Last updated: 2026-04-28 | Update when team-wide API standards change*
