# Index Search Service

The Index Search Service is an early-stage prototype whose stated purpose was to provide full-text search and event-audit capabilities over Reportnet3 entities — datasets, dataflows, and organisations — backed by Elasticsearch. The service was never completed. Most of the planned functionality is commented out in the source, and the only production-affecting behaviour that actually runs today is a single Kafka consumer that records dataset-connection creation events into an Elasticsearch index. No other service calls this service synchronously, and no Feign client for it exists in `common-interfaces`.

The service is included in this document because it occupies a slot in the microservice ecosystem, consumes a platform-wide Kafka event, and its data model reveals what the feature was designed to become.

## Flow overview

```mermaid
flowchart TD
    RS[Record Store Service]
    KAFKA[Kafka\nDATA_REPORTING_TOPIC]
    IDX[Index Search Service :9030]
    ES[(Elasticsearch\nlead index)]
    CLIENT[Browser / Caller]

    RS -->|CONNECTION_CREATED_EVENT| KAFKA
    KAFKA -->|CreateConnectionCommand| IDX
    IDX -->|IndexRequest — write sparse audit document| ES
    CLIENT -->|GET /index| IDX
    IDX -->|matchAllQuery — returns all documents| ES
    CLIENT -->|DELETE /index/{id}| IDX
    IDX -->|DeleteRequest| ES
```

---

## Domain model

The service defines five domain classes used as Elasticsearch documents. None of them are stored in a relational database; they are serialised as JSON and written directly to Elasticsearch.

`ElasticSearchData` is the top-level document that gets indexed:

| Field | Type | Meaning |
|---|---|---|
| `id` | String (UUID) | Document identifier, generated at index time |
| `registerUserName` | String | The username of whoever triggered the event |
| `registerUserAuthorization` | String | Unused in current live code |
| `registerUserURL` | String | Unused in current live code |
| `roleName` | String | Unused in current live code |
| `organizationName` | String | Unused in current live code |
| `elasticUser` | `ElasticUser` | Unused in current live code |
| `elasticCrossoverFilter` | `ElasticCrossoverFilter` | Unused in current live code |
| `entityEvent` | `EntityEvent` | What happened and to which entity |

`EntityEvent` describes the event that caused the document to be written:

| Field | Meaning |
|---|---|
| `entityType` | The type of entity affected (not populated by current code) |
| `eventType` | The name of the Kafka event that triggered the write (e.g. `CONNECTION_CREATED_EVENT`) |
| `entityURL` | The JDBC connection string plus schema path for the new dataset database |
| `entityName` | The dataset name (in the form `dataset_<id>`) |
| `eventDescription` | Not populated by current code |

`ElasticUser` (defined but not populated in live code) was intended to hold a user identifier and a favourite flag, suggesting a planned per-user bookmarking feature.

`ElasticCrossoverFilter` (defined but not populated in live code) was intended to hold cross-entity filter values — dataflow data, dataset data, data collection data, and organisation — for use in faceted search queries.

`ElasticDataset` is a separate domain class that was never wired into any live code path. It holds dataset-level summary fields (`Name`, `Countries`, `Issue`, `Release`, `AccesURL`) alongside an `ElasticUser`, and represents what a searchable dataset record was supposed to look like.

---

## What it actually does

### Kafka consumer — `CreateConnectionCommand`

This is the only live code path that has any side effect. The command listens on the `CONNECTION_CREATED_EVENT` Kafka topic.

The Record Store Service emits this event every time it successfully provisions a new per-dataset PostgreSQL database. The event payload contains a `ConnectionDataVO` (holding the JDBC connection string, schema name, and database user) and the dataset name string.

When `CreateConnectionCommand` receives the event, it:

1. Extracts the `ConnectionDataVO` and the dataset name from the event payload.
2. Generates a random UUID as the document ID.
3. Builds an `ElasticSearchData` document with `registerUserName` set to the database user from the connection data, and an `EntityEvent` whose `entityName` is the dataset name, `eventType` is `CONNECTION_CREATED_EVENT`, and `entityURL` is the JDBC connection string concatenated with the schema name.
4. Serialises the document to a JSON map using Jackson.
5. Sends an `IndexRequest` to the Elasticsearch `lead` index using `RestHighLevelClient`.

The practical effect is that every time a new dataset database is created anywhere in the platform, a document recording that creation lands in Elasticsearch. This was the beginning of an audit trail.

### REST endpoints

The service exposes three endpoints under `/index`:

`GET /index` calls `findAll()`, which issues a `matchAll` query against the `lead` index and returns every document as a list of `ElasticSearchData` objects. There is no pagination, filtering, or access control beyond the JWT check applied at the gateway level.

`DELETE /index/{id}` deletes a single document from the `lead` index by its document ID.

`GET /index/macros` does nothing. The method body is empty; the implementation using a Command pattern was commented out before it was completed.

All other CRUD and search operations (create, update, find by ID, search by name, search by technology) are commented out in both the controller and the service implementation.

---

## Elasticsearch index structure

The service targets a single Elasticsearch index named `lead`, using document type `lead`. The use of explicit types is a Elasticsearch v6-era API pattern; in Elasticsearch v7, types were deprecated, and in v8 they were removed. The `elasticsearch-rest-high-level-client` dependency version is inherited from the parent POM without a pinned version, which means the actual Elasticsearch version in use is determined by the platform deployment configuration rather than the source code.

There is no index mapping definition in the service. Elasticsearch will auto-map the JSON fields on first insert. The `id` field collides with Elasticsearch's built-in `_id` metadata field because `IndexRequest` is called with the UUID as the document ID parameter, so the stored `id` field in the document source is redundant.

---

## Relationships with other services

The Index Search Service has no outbound synchronous calls to any other service and exposes no Feign interface in `common-interfaces`. It participates in the platform only through one inbound Kafka event.

**Kafka event consumed:**

- `CONNECTION_CREATED_EVENT` — emitted by the Record Store Service after a new dataset database is provisioned. The Index Search Service uses this to write an audit document to Elasticsearch.

The Dataset Service also consumes `CONNECTION_CREATED_EVENT` for its own purpose (initialising the dataset schema and tables), so both services react independently to the same event. The two consumers do not coordinate.

No other service reads from Elasticsearch or calls the Index Search Service's REST API in any production code path currently present in the repository.

---

## Current state and what was intended

The data model is notably more complete than the implementation, which reveals the original design intent clearly.

`ElasticCrossoverFilter` — with fields for dataflow, dataset, data collection, and organisation — was designed to support cross-entity faceted search: a user would be able to search across the whole platform and filter results by the entity type and organisation. `ElasticUser` with a `FavoriteFlag` suggests that search results were to be personalised, with users able to bookmark datasets or dataflows they care about.

`ElasticDataset` shows that datasets themselves (not just connection events) were intended to be indexed as searchable documents, with summary fields like `Countries`, `Issue`, and `Release` drawn from the dataset and dataflow metadata.

The commented-out search endpoints — search by name (`GET /index/name-search`) and search by technology (`GET /index/search?technology=...`) — confirm that general text search was planned, not just audit logging.

`executeMacros()` was a placeholder for a Command pattern dispatcher that would have allowed batch re-indexing operations to be triggered on demand, likely to rebuild the Elasticsearch index from current platform state.

None of this was completed. What shipped is a consumer that writes connection events to Elasticsearch and a `findAll` endpoint that can read them back.

---

## Configuration

| Key | Location | Purpose |
|---|---|---|
| `server.port` | `application.yml` | Index Search Service listens on port **9030** |
| `elasticsearch.host` | Consul KV (`indexsearch` config namespace) | Hostname of the Elasticsearch node |
| `elasticsearch.port` | Consul KV (`indexsearch` config namespace) | Port of the Elasticsearch node (typically 9200) |
| Consul host/port | `bootstrap.yml` (`${CONSUL_HOST}`, `${CONSUL_PORT}`) | Service discovery and configuration source |

The Elasticsearch client is configured with empty username and password credentials in `ElasticSearchClientConfiguration`, meaning it expects an Elasticsearch instance with no authentication, or that basic-auth credentials are injected through another mechanism at deployment time.
