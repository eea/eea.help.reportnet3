# Idea: user-bound API keys with configurable dataflow access

## Problem

Today every API key is permanently bound to a single dataflow and data provider pair at creation time. The key format stored in Keycloak is:

```
<uuid>,<dataflowId>,<dataProviderId>
```

A user who submits data to five dataflows therefore holds five separate API keys. Any FME workspace or external script that touches more than one dataflow must be configured with a different `Authorization: ApiKey …` header per dataflow. When a key is rotated — because a user offboards, or because a key leaks — every script and every FME workspace that referenced that key must be updated individually. The operational cost compounds as the number of integrations grows.

The goal of this idea is to let a user hold a single long-lived API key and explicitly grant it access to whichever dataflows they choose, without changing the security model: the key still cannot reach dataflows it has not been granted, and it still cannot escalate beyond the user's role within each dataflow.

---

## Current architecture summary

The relevant code is concentrated in three places:

- **`KeycloakSecurityProviderInterfaceService`** (`user-management-service`) — `createApiKey()` at lines 816–848 generates a UUID and appends the `<uuid>,<dataflowId>,<dataProviderId>` entry to the `ApiKeys` Keycloak user attribute. `authenticateApiKey()` at lines 691–745 scans all Keycloak users to find the owner of a given UUID and returns a `TokenVO` whose groups are filtered to reporter-level groups for that one dataflow only.

- **`EeaSecurityExpressionRoot`** (`common-utitlities`) — `checkApiKey()` at lines 225–244 rejects a request if the API key's embedded dataflow ID does not match the resource being accessed. `secondLevelAuthorizeWithApiKey()` at lines 106–109 composes this check with role-based access.

- **`ApiKeyAuthenticationFilter`** (`common-utitlities`) — intercepts every request whose `Authorization` header starts with `ApiKey `, resolves the `TokenVO`, and populates the Spring Security context. The filter is transparent to all downstream services.

The FME flow in `FMEIntegrationExecutorService` calls `GET /user/getApiKey` (or `POST /user/createApiKey` if none exists) and passes the key as a published parameter to FME Server. FME then uses it in callback requests to Reportnet3.

---

## Proposed model

Instead of each entry encoding exactly one dataflow, the `ApiKeys` attribute would hold entries that encode a key bound to the user with a list of permitted dataflow+provider pairs:

```
<uuid>;<dataflowId1>:<dataProviderId1>,<dataflowId2>:<dataProviderId2>,...
```

A custodian entry (no data provider) would use an empty string or `0` for the provider field:

```
<uuid>;<dataflowId1>:0,<dataflowId2>:0
```

A user creates the key once. They then grant and revoke dataflow access through a separate management operation. The UUID never changes; only the access list changes.

---

## What changes are needed

### 1. Keycloak storage format

The simplest migration-safe approach is to introduce a new storage format alongside the old one and detect the format at parse time. Old entries contain exactly two commas (`uuid,dfId,dpId`); new entries contain a semicolon (`uuid;dfId:dpId,...`). Both formats can coexist in the same `ApiKeys` attribute list during a transition period, letting old keys continue to work.

**`KeycloakSecurityProviderInterfaceService`** — the private parse method that splits on comma (currently used in `authenticateApiKey()` around line 702) must be extended to handle both formats.

### 2. New lifecycle methods on the service

These three new methods would be added to `KeycloakSecurityProviderInterfaceService` and exposed through `UserManagementControllerImpl`:

- **`createApiKey(userId)`** — creates a key with an empty access list. No dataflowId required.
- **`grantDataflowAccess(apiKey, dataflowId, dataProviderId)`** — appends a `dataflowId:dataProviderId` entry to the key's access list.
- **`revokeDataflowAccess(apiKey, dataflowId, dataProviderId)`** — removes an entry.
- **`getApiKeyScopes(apiKey)`** — returns the full list of granted dataflow+provider pairs.

The existing `createApiKey(dataflowId, dataProviderId)` endpoint can remain for backwards compatibility during the transition, but internally it would create a key in the new format with a single entry pre-granted.

### 3. `authenticateApiKey()` return value

Currently the method filters the user's Keycloak groups down to reporter-level groups for the one dataflow the key is bound to. Under the new model it must return groups for **all** dataflows in the key's access list. The `TokenVO` already carries a groups list; the change is in the filtering logic — instead of matching against a single dataflow ID, it matches against the full set of permitted IDs.

This has an implication for `checkApiKey()` (see below): the access list must either be embedded in the `TokenVO` itself or re-derived from the stored key on each check. Embedding it in the `TokenVO` is simpler and consistent with how groups work today.

### 4. `checkApiKey()` in `EeaSecurityExpressionRoot`

Today this method verifies that the dataflow ID extracted from the key attribute matches the `dataflowId` parameter of the current request. Under the new model, it must instead check whether the `dataflowId` parameter appears in the access list that was embedded in the `TokenVO` during authentication. The change is localised to `EeaSecurityExpressionRoot` and does not affect `secondLevelAuthorizeWithApiKey()`.

### 5. API endpoints

Three new endpoints in `UserManagementControllerImpl`:

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/user/createApiKey` | Create a user-bound key with no initial access (new behaviour; old signature kept for compatibility) |
| POST | `/user/apiKey/{apiKey}/grantAccess` | Grant a dataflow+provider pair to the key |
| DELETE | `/user/apiKey/{apiKey}/revokeAccess` | Remove a dataflow+provider pair |
| GET | `/user/apiKey/{apiKey}/scopes` | List all granted dataflow+provider pairs |

The existing `GET /user/getApiKey?dataflowId=…` can continue to work: it would return the single key that includes the requested dataflow in its access list.

Authorisation rules remain the same: a user may only grant access to a dataflow for which they hold a reporter or custodian role.

### 6. Frontend changes

The `ApiKeyDialog` component at `frontend-service/src/views/_components/ApiKeyDialog/ApiKeyDialog.jsx` currently shows a single key tied to one dataflow and a generate-new-key button. It would need to become a management panel:

- Show the single user-level key (or a prompt to generate one if none exists).
- Show a list of dataflows the key is currently granted access to, with a remove button per entry.
- Provide an "add dataflow" control for granting access to another dataflow the user has a role in.

The configuration endpoints in `DataflowConfig.js` and repository methods in `DataflowRepository.js` would need counterparts for the new grant/revoke/list operations.

### 7. FME integration

`FMEIntegrationExecutorService` currently calls `getApiKey(dataflowId, dataProviderId)` and creates a key if none exists. Under the new model it would:

1. Call `getApiKey()` (no parameters) to retrieve the user's single key — or create one if the user has none.
2. Call `grantDataflowAccess(apiKey, dataflowId, dataProviderId)` if the dataflow is not already in the access list.
3. Pass the key to FME as before.

This is a safe change: the key is still scoped to at most the dataflows the user has roles in.

### 8. Redis cache

The current cache key is the API key UUID. The cached value is a `TokenVO` whose groups reflect the single-dataflow scope. Under the new model, the `TokenVO` groups reflect all granted dataflows, so the cache is still valid as long as the access list does not change. Cache invalidation must be triggered when `grantDataflowAccess` or `revokeDataflowAccess` is called — the entry for that UUID must be evicted from the `api_key` Redis cache. Today there is already a known limitation that rotation does not evict the cache; this would be a good moment to address that gap as part of this work.

---

## Migration path

1. Deploy a version of `authenticateApiKey()` that understands both the old `uuid,dfId,dpId` format and the new `uuid;dfId:dpId,...` format. Existing keys continue to work unchanged.
2. Release the new create/grant/revoke endpoints and the updated frontend.
3. Users who want a consolidated key generate a new one and grant their dataflows to it. Their old per-dataflow keys remain valid.
4. Once a user has migrated, FME workspaces and scripts are updated to use the single key.
5. After a transition period, the old format can be deprecated and old keys removed.

There is no forced migration. Old keys can remain in service indefinitely; they simply carry a one-dataflow access list in the old format.

---

## What does not change

- The HTTP header format (`Authorization: ApiKey <uuid>`) is unchanged.
- The filter chain and `ApiKeyAuthenticationFilter` are unchanged.
- Role-based access control is unchanged. A key can only grant what the user's Keycloak roles permit on each dataflow.
- Keys are still stored only in Keycloak; no new database table is needed.
- The restriction to reporter-level groups (no custodian or steward escalation via API key) remains in place.
