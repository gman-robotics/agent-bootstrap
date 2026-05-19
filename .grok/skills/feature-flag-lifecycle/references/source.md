# feature-flag-lifecycle.md — Feature Flag Lifecycle Skill

**Purpose**  
A workflow for creating, rolling out, and — critically — removing feature flags. The most common failure mode with flags is never cleaning them up. This skill enforces a cleanup commitment at creation time.

**When to Use**
- Shipping a risky or large feature incrementally
- Running an A/B experiment
- Enabling a feature for specific users/tenants before general availability
- Hiding incomplete work behind a safe default-off toggle

---

## Phase 1: Create

### Naming Convention
```
<area>_<feature>_enabled

Examples:
  document_bundling_v2_enabled
  onboarding_flow_redesign_enabled
  ai_classification_enabled
```

- Use `snake_case`.
- Always suffix with `_enabled` to make boolean intent explicit.
- Prefix with the product area so flags group naturally when listed.

### Default Value
- **Always default to `false` (off).**
- The feature must be explicitly enabled — never enabled by surprise.

### Where to Store Flags

For simple on/off flags scoped to the current environment:
```typescript
// config/default.json  (node-config)
{
  "featureFlags": {
    "document_bundling_v2_enabled": false
  }
}

// config/production.json — override when ready to ship
{
  "featureFlags": {
    "document_bundling_v2_enabled": true
  }
}
```

For per-tenant or per-user flags (gradual rollout):
```typescript
// Store in DB: feature_flags table
// { flag_name, tenant_id | user_id | null (global), enabled, enabled_at }
```

### Set a Cleanup Date — Non-Optional

At creation, record the flag and its intended removal date:
1. Add a `TODO` comment in code at the flag check:
   ```typescript
   // TODO: remove flag document_bundling_v2_enabled after 2026-06-01 once fully rolled out
   if (config.get('featureFlags.document_bundling_v2_enabled')) {
     return bundleV2(documents)
   }
   return bundleV1(documents)
   ```
2. Add an entry to `memory-bank/progress.md` under an "Open Feature Flags" section:
   ```
   - document_bundling_v2_enabled — added 2026-05-01, remove after 2026-06-01
   ```

---

## Phase 2: Implement

Write the flag check at the **highest appropriate level** — not buried inside a utility function where callers can't see it.

```typescript
// Good — flag at the route/service boundary, easy to find and remove
async function generateBundle(tenantId: string, documentIds: string[]) {
  if (config.get('featureFlags.document_bundling_v2_enabled')) {
    return bundleV2(tenantId, documentIds)
  }
  return bundleV1(tenantId, documentIds)
}

// Avoid — flag buried inside a shared utility
function formatPage(page: Page) {
  if (config.get('featureFlags.document_bundling_v2_enabled')) { // wrong layer
    return formatPageV2(page)
  }
  return formatPageV1(page)
}
```

**Test both paths.** Write tests for the flag-off path (existing behavior) and the flag-on path (new behavior). Do not use `jest.mock` to fake the flag — read a real config value in tests.

```typescript
describe("generateBundle with feature flag", () => {
  it("uses v1 bundler when flag is off", async () => {
    config.set('featureFlags.document_bundling_v2_enabled', false)
    // ...
  })
  it("uses v2 bundler when flag is on", async () => {
    config.set('featureFlags.document_bundling_v2_enabled', true)
    // ...
  })
})
```

---

## Phase 3: Roll Out

### Staged Rollout (Recommended)
1. **Internal** — Enable for your own tenant/account in staging. Validate manually.
2. **Beta tenant(s)** — Enable for one or two trusted customer tenants. Watch logs and error rates for 24–48h.
3. **Gradual** — Enable for 10%, 50%, 100% of tenants by flipping DB rows or config.
4. **GA** — Set the flag default to `true` in config (or remove the flag — see Phase 4).

### What to Watch During Rollout
- Error rate on the flagged path (CloudWatch, application logs)
- Latency compared to the control path
- Any tenant-specific complaints or support tickets
- Bull queue job failure rate if the flag affects async processing

### Rollback
To roll back instantly: flip the flag to `false`. No deploy required. This is the main value of a flag.

---

## Phase 4: Remove (Graduation)

A flag that is never removed is technical debt. **Flags must be removed within the window set in Phase 1.**

### When to Remove
- The feature is stable and fully rolled out (flag is `true` everywhere)
- The experiment is concluded
- The flag-off path is no longer needed

### How to Remove
1. Grep for all references to the flag name:
   ```bash
   grep -r "document_bundling_v2_enabled" .
   ```
2. For each reference:
   - In code: delete the flag check and the old path. Keep only the new behavior.
   - In config files: delete the flag key.
   - In the DB feature_flags table: delete the row.
   - In tests: delete the flag-off test; keep (and rename) the flag-on test — it is now the baseline.
3. Search for the `TODO` comment added in Phase 1 and delete it.
4. Remove the entry from `memory-bank/progress.md`.
5. Run the full test suite. It must be green.
6. Submit a PR. The PR description should reference the original flag introduction commit.

### The Cleanup Commit Message
```
chore: graduate document_bundling_v2_enabled flag

V2 bundler is fully rolled out and stable. Removed flag check and v1 code path.
```

---

## Tracking Open Flags

Add and maintain an "Open Feature Flags" section in `memory-bank/progress.md` for the active project:

```markdown
## Open Feature Flags

| Flag | Added | Remove By | Status |
|---|---|---|---|
| document_bundling_v2_enabled | 2026-05-01 | 2026-06-01 | Rolling out to beta |
| onboarding_flow_redesign_enabled | 2026-04-15 | 2026-05-15 | GA — ready to graduate |
```

During any review that touches the area, check this table for flags past their removal date and flag them in the PR review.

---

## Anti-Patterns

| Anti-pattern | Problem |
|---|---|
| No cleanup date | The flag lives forever. Becomes a hidden config dependency nobody understands. |
| Flag buried deep in a utility | Hard to find, hard to remove. Check the caller chain — flags belong near the boundary. |
| Flag default `true` | Destroys the ability to roll back. Always default off. |
| Testing only the flag-on path | The flag-off path can silently break. Test both. |
| Keeping the flag after full rollout | Permanent flags are permanent complexity. Graduate promptly. |

---
