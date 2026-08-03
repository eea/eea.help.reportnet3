# API key authentication

Reportnet3 provides two authentication paths for programmatic access: the standard JWT flow (OAuth2 via Keycloak) and a personal API key system. This document covers the API key system only.

API keys exist because FME Server and external scripts cannot easily participate in an interactive OAuth2 flow. A reporter or custodian generates a key once, stores it securely, and uses it whenever they need to call Reportnet3 endpoints without a browser session. The key is always scoped to a single dataflow and data provider, so a leaked key cannot be used to reach other dataflows or escalate privileges beyond reporter-level access.

---

## What an API key is

An API key is a UUID (version 4) string, 36 characters long, that identifies a user in the context of one dataflow and one data provider. It is stored as a Keycloak user attribute alongside the IDs it is bound to. There is no separate database table — Keycloak is the sole store.

The attribute key is `ApiKeys`. Each entry in the list has the format:

```
<uuid>,<dataflowId>,<dataProviderId>
```

For example:

```
550e8400-e29b-41d4-a716-446655440000,12,3
```

That entry means: UUID `550e8400-e29b-41d4-a716-446655440000`, dataflow 12, data provider 3. Only one active key exists per dataflow + data provider combination per user. Creating a new key for the same pair silently replaces the old one.

---

## Who can create API keys

To call `POST /user/createApiKey`, the authenticated user must hold one of the following roles on the target dataflow:

- `DATAFLOW_LEAD_REPORTER`
- `DATAFLOW_REPORTER_READ`
- `DATAFLOW_REPORTER_WRITE`
- `DATAFLOW_CUSTODIAN`
- `DATAFLOW_EDITOR_WRITE`
- `DATAFLOW_NATIONAL_COORDINATOR`
- `DATAFLOW_STEWARD`
- `DATAFLOW_OBSERVER`
- `DATAFLOW_STEWARD_SUPPORT`

Platform-level `DATA_CUSTODIAN` and `DATA_STEWARD` roles may also create keys if they have reference entity access on the dataflow.

---

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/user/createApiKey` | Generate a new API key for the authenticated user, scoped to a dataflow and data provider |
| GET | `/user/getApiKey` | Retrieve the authenticated user's existing API key for a dataflow and data provider |
| GET | `/user/{userId}/getApiKey` | Retrieve any user's API key by their Keycloak user ID (requires authentication) |
| POST | `/user/authenticateByApiKey/{apiKey}` | Exchange an API key for a `TokenVO` (used by the filter internally) |

Both `createApiKey` and `getApiKey` accept `dataflowId` (required) and `dataProvider` (optional) as query parameters.

---

## How to use an API key

### Step 1 — generate the key

Call `POST /user/createApiKey?dataflowId=12&dataProvider=3` while authenticated with a normal JWT. The response body is the raw UUID string:

```
550e8400-e29b-41d4-a716-446655440000
```

Store this value. It will not be shown again unless you call `GET /user/getApiKey` with the same parameters.

### Step 2 — authenticate with the key

On any subsequent request, pass the key as the `Authorization` header:

```
Authorization: ApiKey 550e8400-e29b-41d4-a716-446655440000
```

The `ApiKeyAuthenticationFilter` runs before the standard JWT filter on every request. When it sees a header starting with `ApiKey `, it extracts the UUID, calls `authenticateUserByApiKey()` internally, and — if the key is valid — sets up the Spring Security context exactly as a JWT login would. The downstream service receives an authenticated request with the user's identity and permitted groups already resolved. No separate login step is needed.

### What the filter does

`ApiKeyAuthenticationFilter` is a `OncePerRequestFilter` that:

1. Reads the `Authorization` header.
2. Checks whether the value starts with `ApiKey ` (note the trailing space).
3. Strips the prefix and passes the UUID to `UserManagementControllerZull.authenticateUserByApiKey()`.
4. If a `TokenVO` is returned, calls `AuthenticationUtils.performAuthentication()` to set the security context.
5. Always calls `filterChain.doFilter()` — the chain continues whether or not authentication succeeded.

### What groups are granted

When authenticated via API key, the filter does not grant the user's full set of Keycloak groups. It restricts the token to only those groups that are reporter-level on the specific dataflow the key is bound to:

- `Dataflow-{id}-LEAD_REPORTER`
- `Dataflow-{id}-REPORTER_READ`
- `Dataflow-{id}-REPORTER_WRITE`
- `Dataflow-{id}-EDITOR_WRITE`

This means an API key cannot be used to perform custodian or steward operations even if the user holds those roles in their Keycloak account. The restriction is intentional: API keys are meant for data submission, not for administrative actions.

---

## How the validation works internally

`KeycloakSecurityProviderInterfaceService.authenticateApiKey()` performs a linear scan over all users in Keycloak:

1. For each user that has an `ApiKeys` attribute, it searches the list for an entry starting with the provided UUID.
2. When found, it extracts the dataflow ID from the attribute value (the second comma-separated field).
3. It then fetches the user's Keycloak groups and filters them to the four reporter-level group names for that dataflow.
4. It returns a `TokenVO` containing the user ID, username, filtered groups, and Keycloak roles.

If no user is found with that key, it returns `null` and the request proceeds unauthenticated. If more than one user is found — which should never happen since UUIDs are random — the service logs an error and also returns `null`.

The result is cached under the `api_key` cache in Redis, so repeated calls with the same UUID do not hit Keycloak on every request.

---

## FME Server integration

The most significant consumer of API keys is the FME Server integration. When the Dataflow Service dispatches a job to FME Server, it needs to provide a credential that FME can use to call Reportnet3 back (for example, to write import results to a dataset). The service cannot use a user's browser JWT because FME is a server-side system running outside the user's session.

`FMEIntegrationExecutorService` resolves this by calling `GET /user/getApiKey` before building the FME job request. If no key exists for the dataflow and data provider, it calls `POST /user/createApiKey` to generate one on the fly. The key is then passed to FME Server in two ways:

- As an FME directive named `ApiKey`, with just the raw UUID as its value.
- As a published parameter also named `ApiKey`, with the value `ApiKey <uuid>` (that is, with the `ApiKey ` prefix included, matching the HTTP header format that Reportnet3 expects).

FME Server stores the key and uses it to authenticate its callback requests to Reportnet3 endpoints such as `POST /dataset/{datasetId}/etlImport`.

---

## Relationships with other services

The API key system touches three services:

- **User Management Service** — owns key creation, retrieval, and validation. All other services call it via Feign.
- **Dataflow Service** — creates and retrieves keys automatically when dispatching FME jobs. Does not manage keys directly; delegates entirely to the User Management Service.
- **Common utilities (`common-utitlities`)** — provides `ApiKeyAuthenticationFilter`, `AuthenticationUtils`, and `EeaSecurityExpressionRoot.checkApiKey()`. Every microservice that includes the common security configuration gets the filter automatically. This is why API key authentication works transparently across all services without each one implementing its own key logic.

---

## Key lifecycle

- **Creation**: user calls `POST /user/createApiKey`. A UUID is generated, stored in Keycloak, and returned.
- **Rotation**: calling `POST /user/createApiKey` again for the same dataflow + data provider replaces the old key. The old UUID immediately stops working because the attribute entry is overwritten.
- **Deletion**: there is no explicit delete endpoint. Keys are removed only by rotation (creating a new key for the same scope). The `getUserWithoutKeys()` method strips all API keys from a user representation; it is used in certain internal attribute update flows to prevent keys from being overwritten accidentally.
- **Cache invalidation**: the `api_key` Redis cache is not explicitly evicted when a key is rotated. A rotated key will continue to authenticate successfully from cache until the cache entry expires. This is a current limitation of the implementation.

---

## Configuration

There are no Consul or application.yml settings specific to API key behaviour. The behaviour is controlled entirely by the security configuration in `SecurityConfiguration` in `common-utitlities`, which registers `ApiKeyAuthenticationFilter` in the Spring Security filter chain ahead of the standard JWT filter.
