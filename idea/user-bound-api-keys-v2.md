# Idea: parallel database-backed API keys with multi-dataflow scope

## Problem with the previous proposal

The document `user-bound-api-keys.md` describes modifying the existing Keycloak-attribute-based system. That approach inherits the worst property of the current design: at every authentication request, the system must either talk to Keycloak or rely on a Redis cache that has no explicit invalidation. The current `authenticateApiKey()` is an O(n-users) scan of all Keycloak users. Even with Redis, every cache miss hits that scan.

This document proposes a different approach: build a second, independent API key system on top of the existing one, backed by the shared PostgreSQL database. The old system is left completely untouched. Both systems coexist in the same filter chain. Users who want multi-dataflow keys migrate voluntarily.

---

## Why the database avoids heavy Keycloak interaction

In the current system, the authentication lookup has two steps:

1. **Find the key owner** — scan all Keycloak users until one has the UUID in their `ApiKeys` attribute. This is the expensive step. Keycloak has no index on user attributes.
2. **Build the token** — retrieve that user's groups, filter to reporter-level groups for the embedded dataflow, return a `TokenVO`.

A database-backed system eliminates step 1 entirely. The key is stored in a table with the owner's Keycloak user ID already attached, indexed on the UUID column. Step 1 becomes a single `SELECT` with a primary-key lookup.

Step 2 still needs to know the user's current Keycloak groups. But because we now know *which* user to ask about upfront, the Keycloak call is `realmResource.users().get(userId).groups()` — one user, not all users. That result can be cached by `userId` with a long TTL (roles change rarely) rather than by the API key UUID. When a user's roles change across dataflows, a single cache eviction by `userId` covers all their keys at once.

---

## New data model

Two new tables are added to the shared `public` schema via a Flyway migration in the `database` module.

**`api_key_v2`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` | Primary key. The value sent in the `Authorization` header. |
| `user_id` | `varchar(255)` | Keycloak user ID of the owner. Not a foreign key — Keycloak is the authority. |
| `name` | `varchar(255)` | User-given label, e.g. "FME production workspace". |
| `created_at` | `timestamptz` | Set at creation. |
| `last_used_at` | `timestamptz` | Updated on every successful authentication. Useful for auditing unused keys. |
| `active` | `boolean` | `true` by default. Set to `false` to revoke without deleting. |

**`api_key_v2_scope`**

| Column | Type | Notes |
|--------|------|-------|
| `api_key_id` | `uuid` | Foreign key to `api_key_v2.id`. |
| `dataflow_id` | `bigint` | The dataflow this key is permitted to access. |
| `data_provider_id` | `bigint` | Nullable. `null` means custodian-level access (no provider restriction). |

`(api_key_id, dataflow_id, data_provider_id)` is a unique constraint — duplicate grants are idempotent rather than an error.

There is no dependency on the Keycloak schema. The `user_id` is stored as a plain string because Keycloak is the source of truth for user identity; this table does not try to replicate it.

---

## Authentication flow

When the `ApiKeyAuthenticationFilter` receives a request with `Authorization: ApiKey <uuid>`, it currently delegates to `userManagementControllerZull.authenticateUserByApiKey()`. The filter would be extended to try the new system first:

1. Look up the UUID in `api_key_v2` (`SELECT id, user_id, active FROM api_key_v2 WHERE id = ?`).
2. If not found or `active = false`, fall through to the existing Keycloak-attribute path. Old keys continue to work without any change.
3. If found, load the scopes: `SELECT dataflow_id, data_provider_id FROM api_key_v2_scope WHERE api_key_id = ?`.
4. Fetch the user's Keycloak groups via `getUserById(userId).groups()`. This result is cached by `userId` in Redis (suggested TTL: 10 minutes), separate from the existing `api_key` cache.
5. Filter the groups to reporter-level names for each dataflow in the scope list.
6. Build a `TokenVO` with the user ID, username, filtered groups, and the scope list embedded as a custom claim.
7. Populate the Spring Security context as normal.

The total Keycloak interaction per cache miss is one `GET /users/{id}/groups` call for one user. The current system's miss cost is a full user-attribute scan.

The fallback to the old system in step 2 means the filter change is strictly additive — no old code is removed or altered.

---

## What the `TokenVO` carries for multi-dataflow keys

The existing `TokenVO` was designed for single-dataflow keys: it carries one set of groups for one dataflow. For the new system the same structure is reused — the groups list simply contains reporter-level entries for all permitted dataflows simultaneously:

```
Dataflow-12-LEAD_REPORTER
Dataflow-12-REPORTER_WRITE
Dataflow-47-REPORTER_WRITE
Dataflow-63-REPORTER_READ
```

The downstream `checkApiKey()` in `EeaSecurityExpressionRoot` must be extended for new-style keys. For old-style keys, the check is "does the key's embedded dataflow ID match the requested resource?". For new-style keys, the check is "does the requested dataflow appear in the scope list stored on the `TokenVO`?". The two paths are distinguishable because new-style tokens carry a flag or a non-null scope list; old-style tokens do not.

---

## New API endpoints

These endpoints are added to `UserManagementControllerImpl`. They only manage the new database-backed keys; old Keycloak-attribute keys are unaffected.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/user/v2/createApiKey` | Create a new key for the authenticated user. Body: `{ "name": "..." }`. Returns the UUID. |
| GET | `/user/v2/getApiKeys` | List all active keys for the authenticated user, with their names and scope counts. Does not expose UUIDs after creation — that value is shown once. |
| POST | `/user/v2/apiKey/{keyId}/grantScope` | Grant a dataflow+provider pair. Parameters: `dataflowId`, `dataProvider` (optional). Requires the user to hold a reporter or custodian role on that dataflow. |
| DELETE | `/user/v2/apiKey/{keyId}/revokeScope` | Remove a dataflow+provider pair from the key's scope list. |
| DELETE | `/user/v2/apiKey/{keyId}` | Deactivate the key (`active = false`). Immediate effect — no cache lag. |
| GET | `/user/v2/apiKey/{keyId}/scopes` | List the granted scopes for a key the authenticated user owns. |

Authorisation for scope grants follows the same `@PreAuthorize` expressions used by the existing create endpoint: the user must hold a qualifying role on the dataflow being granted.

---

## Redis cache strategy

The new system introduces a second cache key namespace alongside the existing `api_key` cache:

- **`api_key_v2:{uuid}`** — caches the full `TokenVO` for a resolved key. Evicted when the key is deactivated or its scope list changes.
- **`user_groups:{userId}`** — caches the raw Keycloak groups for a user. Evicted when a scope grant or revoke happens for any key owned by that user. A longer TTL than the key cache is appropriate here because group changes in Keycloak are relatively rare.

Because deactivating a key or changing its scopes always triggers an explicit cache eviction (unlike today's rotation-with-no-eviction pattern), the cache is correct by construction rather than eventually consistent.

---

## Frontend changes

The `ApiKeyDialog` component would grow a second tab or section for "persistent keys" (the new system). The existing tab remains unchanged for users who prefer per-dataflow keys. The new section shows:

- A list of the user's named keys, each showing its creation date and the number of dataflows it can access.
- A "create key" button — the UUID is shown once in a copy-and-dismiss dialog.
- A detail view per key: the granted dataflows with remove buttons, and an "add dataflow" picker populated with dataflows the user has a role in.
- A revoke button per key.

The `DataflowService.js` and `DataflowRepository.js` files would gain counterpart methods for the new v2 endpoints.

---

## FME integration

`FMEIntegrationExecutorService` currently auto-creates a v1 key if none exists. For the new system the equivalent behaviour would be:

1. Look for an existing v2 key for the user that already includes the current dataflow in its scope list.
2. If found, use it as-is.
3. If not found, check whether the user has any v2 key. If yes, grant the current dataflow to it. If no, create a new v2 key named "FME auto-generated", grant the dataflow, and cache the key ID in the user's attributes or in a Consul key for reuse.

The key is passed to FME Server in the same header format as today. FME does not need to know which system issued the key.

---

## Coexistence and migration

No existing behaviour changes. Old per-dataflow Keycloak-attribute keys continue to be created, retrieved, and authenticated exactly as before. The only change to shared code is:

- `ApiKeyAuthenticationFilter` — try the DB lookup first; fall back to the Keycloak path on miss.
- `checkApiKey()` — handle both token styles.

A user who wants to consolidate their keys can create a single v2 key, grant their dataflows, update their FME workspaces and scripts to use the new UUID, and leave the old keys in place or let them expire naturally. There is no forced migration and no migration script.

If the v1 system is eventually retired, the fallback branch in `ApiKeyAuthenticationFilter` is removed and the Keycloak-attribute management endpoints are deprecated. That is a separate decision and does not block shipping the new system.

---

## What Keycloak interaction remains

After this change, Keycloak is contacted for a new-style API key authentication only when the `user_groups:{userId}` cache misses. The call is a single `GET /admin/realms/{realm}/users/{id}/groups` request. This replaces the full-user-attribute scan. For a deployment with hundreds of users, the performance difference is significant. For a deployment with thousands of active API keys belonging to tens of users, the `user_groups` cache will almost always be warm, and Keycloak will rarely be involved in the authentication path at all.

Keycloak is still the authority for user identity and role assignments. That relationship is not removed — only the hot path of key resolution is moved out of it.
