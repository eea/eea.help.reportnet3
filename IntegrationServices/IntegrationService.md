# Integration Service

The Integration Service manages the configuration and execution of data exchange operations between Reportnet 3 and external transformation tools. In the current implementation the only active tool is FME Server, but the service is designed around a factory pattern that can accommodate additional tools without changing the core API — `IntegrationToolTypeEnum` has an `OTHER` value reserved for that purpose.

An *integration* in Reportnet 3 is a named, persisted configuration that pairs a dataset schema with a specific FME workspace and a set of parameters. Once configured, an integration can be triggered by a user or by the platform to import data into a dataset, export data out of it, or push data into the EU-wide aggregated dataset. The integration configuration is reusable: the same workspace can be executed multiple times against the same dataset with different files, or copied wholesale when a dataflow is cloned.

The integration layer lives entirely within the Dataflow Service (port 8020). It exposes a REST API, owns the `integration` and `fme_jobs` database tables, and calls FME Server's REST API directly. The Dataset Service and Orchestrator Service are participants in the execution flow but do not own integration configuration.

## Flow overview

```mermaid
flowchart TD
    USER[User / Browser]
    DS[Dataset Service]
    ORC[Orchestrator Service]
    INTG[Integration Service\nDataflow Service :8020]
    UMS[User Management Service]
    REP[Representative Service]
    EUDS[EU Dataset Service]
    FME[FME Server]
    DB[(integration +\nfme_jobs tables)]
    KAFKA[Kafka]
    COMM[Communication Service]

    USER -->|POST /integration/{id}/runIntegration| INTG
    DS -->|CONTINUE_FME_PROCESS_EVENT| KAFKA
    KAFKA -->|ExecuteExternalIntegrationEvent| INTG
    ORC -->|POST /integration/private/executeIntegration| INTG
    INTG -->|get/create API key| UMS
    INTG -->|look up countryCode\nIMPORT_FROM_OTHER_SYSTEM| REP
    INTG -->|find EU datasets| EUDS
    INTG -->|upload file + submit job| FME
    INTG -->|save FMEJob| DB
    FME -->|POST /fme/operationFinished| INTG
    INTG -->|completion events| KAFKA
    KAFKA --> COMM
```

---

## Domain model

### Integration and its parameters

The `integration` table (created in V14) holds one row per configured integration. The key fields are `name`, `description`, `tool` (`FME` or `OTHER`), and `operation` (`IMPORT`, `EXPORT`, `EXPORT_EU_DATASET`, or `IMPORT_FROM_OTHER_SYSTEM`). The `dataflow` foreign key links it to the dataflow it belongs to.

Configuration is stored in a single `integration_operation_parameters` table using JPA `SINGLE_TABLE` inheritance with a `PARAMETER_TYPE` discriminator column. Rows with `PARAMETER_TYPE='INTERNAL'` are `InternalOperationParameters`; rows with `PARAMETER_TYPE='EXTERNAL'` are `ExternalOperationParameters`. Both hold a `parameter` key and a `value` string.

**Internal parameters** are managed by Reportnet 3 and describe the workspace to execute and how to find it:

| Key | Purpose |
|---|---|
| `processName` | The FME workspace filename (e.g. `ImportReporting.fmw`) |
| `repository` | The FME Server repository containing the workspace |
| `datasetSchemaId` | The MongoDB schema ID of the dataset this integration applies to |
| `dataflowId` | The dataflow this integration belongs to |
| `fileExtension` | The file extension expected for export output (e.g. `xlsx`, `csv`) |
| `notificationRequired` | Whether the user should receive a completion notification |

**External parameters** are workspace-specific inputs defined by the workspace author. They are whatever extra parameters the FME workspace needs beyond the standard set that Reportnet 3 always provides. Common examples are `DataBaseConnectionPublic` (a named database connection on FME Server) and `schema` (a target schema name). These are passed through verbatim to FME at execution time. The only external parameter that is filtered out and never forwarded is `fileIS` (a file-content parameter that would conflict with the file-upload mechanism).

This split between internal and external parameters is deliberate. Internal parameters are managed by the platform — they express the structural relationship between an integration and the schema it serves. External parameters are opaque to Reportnet 3; it does not interpret them, only forwards them. This allows workspace authors to add new parameters to their workspaces without requiring any change to Reportnet 3.

### Operation types

`IntegrationOperationTypeEnum` defines what an integration does:

- **`IMPORT`** — Accepts a file uploaded by the user, sends it to FME for transformation, and loads the output into the dataset. The file is staged on FME Server's filesystem before the workspace executes.
- **`EXPORT`** — Extracts data from the dataset, transforms it via FME, and makes the result available for download. FME writes the output to an `ExportFiles` directory on its filesystem; the user then downloads from there.
- **`EXPORT_EU_DATASET`** — A specialised export that pushes a reporting dataset's data into the EU-wide aggregated (EU) dataset. This operation type is created automatically by the platform and cannot be created manually.
- **`IMPORT_FROM_OTHER_SYSTEM`** — Like `IMPORT`, but the source is an external system rather than a file uploaded by the user. The workspace receives an additional `countryCode` parameter to handle source-system-specific country code mapping.

### FMEJob

`FMEJob` (table `fme_jobs`) tracks individual FME workspace executions. It exists to correlate an incoming callback from FME with the Reportnet 3 context — which dataset, dataflow, provider, and user are involved. Its `status` field tracks the FME execution lifecycle: `CREATED` (the entity has been saved), `QUEUED` (the job was successfully submitted to FME), `COMPLETED` (FME callback arrived with status 0), and `FAILED` (FME callback arrived with status −1, or the polling job detected a failure).

---

## Architecture: the factory pattern

The integration layer uses two factory patterns: one for CRUD operations (`CrudManagerFactory`) and one for execution (`IntegrationExecutorFactory`). Both are backed by a Spring `Set` of implementations that register themselves by tool type at startup via `@PostConstruct`. Adding support for a new tool means adding a new `AbstractCrudManager` and a new `AbstractIntegrationExecutorService` implementation; the factories discover them automatically.

Currently only `FMEIntegrationManager` and `FMEIntegrationExecutorService` are active. The `OTHER` enum value in `IntegrationToolTypeEnum` is a placeholder.

Within the FME executor, operation-type-specific behaviour is handled by a `switch` on `IntegrationOperationTypeEnum`. This means the executor has a single entry point (`execute()`) but four distinct paths depending on whether the call is an import, export, EU export, or system-to-system import.

The choice to route through factories rather than having separate controllers per tool type keeps the API surface stable. Any call to `POST /integration/private/executeIntegration` works regardless of which tool an integration is configured for; the tool type in the integration configuration drives the routing.

---

## Integration lifecycle

### Creating an integration

`POST /integration/create` accepts an `IntegrationVO` with `tool`, `operation`, `name`, `description`, and the two parameter lists. The service validates three things before saving:

1. The internal parameters must include both `dataflowId` and `datasetSchemaId`. These two values define where the integration belongs; without them it cannot be linked to a dataset.
2. The `operation` must not be `EXPORT_EU_DATASET`. That operation type is created automatically when a design dataset schema is created (via `createDefaultIntegration()`), and the system enforces that it cannot be created or updated to this type manually.
3. The `name` must be unique within the same dataflow and dataset schema. Duplicate names are rejected.

The `EXPORT_EU_DATASET` default integration is always created with the FME workspace `Export_EU_dataset.fmw` in the default repository, plus two external parameters (`DataBaseConnectionPublic` and `schema`). This happens automatically whenever a new dataset schema is provisioned.

### Updating an integration

`PUT /integration/update` follows the same name-uniqueness validation. The only additional restriction is that `operation` cannot be changed to or from `EXPORT_EU_DATASET`.

### Copying integrations

When a dataflow is cloned, `POST /integration/private/copyIntegrations` copies all integrations from the source dataset schemas to the destination. The copy substitutes the destination `dataflowId` and `datasetSchemaId` values from a provided dictionary (`dictionaryOriginTargetObjectId`). If the source has an `EXPORT_EU_DATASET` integration, a fresh default one is created for the destination rather than copying the source entry directly, ensuring the default workspace and parameters are always consistent.

### Deleting integrations

`DELETE /integration/{integrationId}/dataflow/{dataflowId}` performs a straightforward hard delete. `DELETE /integration/private/deleteSchemaIntegrations` deletes all integrations for a given `datasetSchemaId` — called when a design dataset is deleted as part of a dataflow cleanup.

---

## Execution

### Internal execution

`POST /integration/private/executeIntegration` is the internal endpoint called by the Dataset Service and Orchestrator Service as part of the import and export pipelines. The caller passes the tool type, operation type, an optional filename, the dataset ID, the full `IntegrationVO`, and an optional job ID. The service routes to the FME executor.

The executor proceeds as follows:

1. It calls the Dataset Service's metabase endpoint to retrieve the dataflow ID and data provider ID for the dataset.
2. It retrieves (or creates) an API key for the user scoped to that dataflow and provider. This API key is what FME will include in its callback, so the callback endpoint can authenticate the request.
3. It creates a `FMEJob` entity (status `CREATED`) and saves it. The saved entity's database ID becomes the `rn3JobId` that is passed to FME as a workspace parameter — this is the correlation handle.
4. It assembles the `FMEAsyncJob` object. The `NMDirectives` section carries the API key, `rn3JobId`, notification flag, and dataset ID. The `publishedParameters` always include `dataflowId`, `datasetId`, `apiKey`, `baseUrl`, and `rn3JobId`. Operation-specific parameters are added next (see below). Finally, all external parameters from the integration configuration are appended.
5. The operation-specific steps:
   - **IMPORT**: uploads the source file to FME's filesystem under `{datasetId}/{providerId}/`, then adds `inputfile`, `folder`, and `providerId` to the published parameters.
   - **EXPORT**: creates an `ExportFiles` directory in FME's filesystem (accepting `CONFLICT` if it already exists), then adds `exportFileName`, `folder`, and `providerId`.
   - **IMPORT_FROM_OTHER_SYSTEM**: looks up the country code for the provider via the Representative Service, then adds `countryCode` and `providerId`.
   - **EXPORT_EU_DATASET**: adds only the external parameters; no file upload or directory creation is needed.
6. The assembled job is POSTed to `POST /fmerest/v3/transformations/submit/{repository}/{workspace}`. FME responds with a numeric job ID.
7. The `FMEJob` entity is updated: if FME returned a job ID the status becomes `QUEUED`; if FME returned null (submission failed) the status becomes `ABORTED` and failure notifications are released immediately.
8. An `ExecutionResultVO` is returned containing the FME job ID.

### External execution (user-triggered)

`POST /integration/{integrationId}/runIntegration/dataset/{datasetId}` is the user-facing endpoint. It accepts a `replace` boolean parameter that controls whether existing data in the dataset is deleted before the import runs.

If `replace=true`, the service calls `datasetControllerZuul.deleteDataBeforeReplacing()` first. That deletion is asynchronous; the Dataset Service publishes `DATA_DELETE_TO_REPLACE_COMPLETED_EVENT` when it finishes. `ExecuteExternalIntegrationEvent`, a Kafka consumer in the Dataflow Service, handles that event and calls the internal execution path with `replace=false`. This decoupling is necessary because the deletion can take significant time for large datasets, and the import cannot begin until it is complete.

If `replace=false`, the executor checks whether a prior execution already put data in place before proceeding.

Before triggering execution, the service acquires a set of dataset-level locks to prevent concurrent modifications: `INSERT_RECORDS`, `DELETE_RECORDS`, `UPDATE_FIELD`, `UPDATE_RECORDS`, `DELETE_DATASET_VALUES`, `IMPORT_FILE_DATA` or `IMPORT_BIG_FILE_DATA` (depending on the big-data flag), and `INSERT_RECORDS_MULTITABLE`. These are released when the FME callback arrives and the Dataset Service processes the completion event.

### EU dataset export

`POST /integration/v1/executeEUDatasetExport` triggers an export of all reporting datasets in a dataflow into their corresponding EU datasets. The service:

1. Acquires a `POPULATE_EU_DATASET` lock scoped to the dataflow ID, to prevent concurrent EU exports for the same dataflow.
2. Retrieves all EU datasets for the dataflow.
3. Retrieves all `EXPORT_EU_DATASET` integrations for the dataflow.
4. Matches each integration to its EU dataset by comparing the `datasetSchemaId` internal parameter with the EU dataset's schema ID.
5. Executes each matched pair through the internal executor.
6. Releases the `POPULATE_EU_DATASET` lock.

This is the only operation that can run multiple FME jobs in a single API call, one per reporting schema. The executions are sequential within the service call.

---

## Relationships with other services

**Dataset Service.** Calls the integration layer's internal execution endpoint as part of the file import pipeline. Also sends `DATA_DELETE_TO_REPLACE_COMPLETED_EVENT` which triggers deferred execution when `replace=true`. The Dataset Service's `FileTreatmentHelper` is responsible for creating the `Process` record and updating the dataset status to `IMPORTING` before the FME job is submitted.

**Orchestrator Service.** Submits integration execution requests when processing scheduled or queued jobs. Also runs the `JobForFmeStatusPolling` cron job that polls FME Server every ten minutes for stalled jobs and marks them failed if they exceed the callback timeout.

**User Management Service.** Called during execution to retrieve or create the API key that FME will include in its callback. The API key is scoped to the specific dataflow and data provider, so each execution's callback can be authenticated precisely.

**Representative Service.** Called during `IMPORT_FROM_OTHER_SYSTEM` execution to look up the country code for a data provider, which is then passed to the FME workspace as the `countryCode` parameter.

**EU Dataset Service.** Called during `executeEUDatasetExport` to list the EU datasets associated with a dataflow.

**Communication Service.** Receives the Kafka completion events published after FME callbacks arrive and delivers real-time WebSocket notifications to the relevant user.

---

## Process flows

### Create and configure an integration

```
1. User: POST /integration/create
   body: { tool: "FME", operation: "IMPORT", name: "...",
           internalParameters: [{ processName, repository, datasetSchemaId, dataflowId }],
           externalParameters: [{ DataBaseConnectionPublic, schema }] }
2. FMEIntegrationManager.create():
   - Validate internalParameters contains dataflowId and datasetSchemaId
   - Reject if operation == EXPORT_EU_DATASET
   - Reject if name already used in same dataflow+schema
   - integrationRepository.save()  ← cascades parameter rows
```

### Import via FME (user-triggered, replace=true)

```
1. User: POST /integration/{integrationId}/runIntegration/dataset/{datasetId}?replace=true
2. IntegrationService.addLocks(datasetId)  ← acquires 7 dataset locks
3. datasetControllerZuul.deleteDataBeforeReplacing(datasetId, integrationId, IMPORT)
   → Dataset Service deletes records asynchronously
→ Kafka: DATA_DELETE_TO_REPLACE_COMPLETED_EVENT

4. ExecuteExternalIntegrationEvent.execute()
   → integrationService.executeExternalIntegration(datasetId, integrationId, IMPORT, false)

5. FMEIntegrationExecutorService.execute(IMPORT, fileName, datasetId, integration, job):
   a. Get dataflowId, providerId from Dataset Service metabase
   b. Get/create API key (User Management Service)
   c. Create FMEJob (status=CREATED)
   d. Upload file to FME: POST /fmerest/v3/resources/connections/Reportnet3/filesys/{datasetId}/{providerId}
   e. Build FMEAsyncJob with publishedParameters including inputfile, folder
   f. POST /fmerest/v3/transformations/submit/{repository}/{workspace}
      → returns fmeJobId
   g. Update FMEJob (status=QUEUED, jobId=fmeJobId)

--- FME executes workspace ---

6. FME: POST /fme/operationFinished  { apiKey, rn3JobId, StatusNumber=0, datasetId }
7. Validate API key (User Management Service); verify owner == FMEJob.userName
8. Update FMEJob.status = COMPLETED
9. Dataset Service processes completion: refresh materialized view, update dataset status
10. integrationService.releaseLocks(datasetId)
→ Kafka: EXTERNAL_IMPORT_REPORTING_COMPLETED_EVENT
→ Communication Service notifies user
```

### EU dataset export

```
1. User: POST /integration/v1/executeEUDatasetExport?dataflowId={id}
2. Acquire POPULATE_EU_DATASET lock for dataflowId
3. euDatasetControllerZuul.findEUDatasetByDataflowId(dataflowId) → List<EUDatasetVO>
4. integrationRepository.findByOperationAndParameterAndValue(EXPORT_EU_DATASET, DATAFLOW_ID, id)
5. For each integration matched to an EU dataset:
   FMEIntegrationExecutorService.execute(EXPORT_EU_DATASET, null, euDatasetId, integration, null)
   → Build FMEAsyncJob (externalParameters only, no file upload)
   → POST /fmerest/v3/transformations/submit/{repository}/{workspace}
6. releasePopulateEUDatasetLock(dataflowId)
```

---

## Kafka events

| Event | Direction | Trigger |
|---|---|---|
| `CONTINUE_FME_PROCESS_EVENT` | Dataset Service → Dataflow Service | Initiates FME execution from Dataset Service pipeline |
| `DATA_DELETE_TO_REPLACE_COMPLETED_EVENT` | Dataset Service → Dataflow Service | Dataset cleared; triggers deferred FME import |
| `EXTERNAL_IMPORT_REPORTING_COMPLETED_EVENT` | Dataflow Service → all | FME import into a reporting dataset succeeded |
| `EXTERNAL_IMPORT_REPORTING_FAILED_EVENT` | Dataflow Service → all | FME import into a reporting dataset failed |
| `EXTERNAL_IMPORT_DESIGN_COMPLETED_EVENT` | Dataflow Service → all | FME import into a design dataset succeeded |
| `EXTERNAL_IMPORT_DESIGN_FAILED_EVENT` | Dataflow Service → all | FME import into a design dataset failed |
| `EXTERNAL_IMPORT_REPORTING_FROM_OTHER_SYSTEM_COMPLETED_EVENT` | Dataflow Service → all | `IMPORT_FROM_OTHER_SYSTEM` into reporting dataset succeeded |
| `EXTERNAL_IMPORT_REPORTING_FROM_OTHER_SYSTEM_FAILED_EVENT` | Dataflow Service → all | `IMPORT_FROM_OTHER_SYSTEM` into reporting dataset failed |
| `EXTERNAL_EXPORT_REPORTING_COMPLETED_EVENT` | Dataflow Service → all | FME export from a reporting dataset succeeded |
| `EXTERNAL_EXPORT_REPORTING_FAILED_EVENT` | Dataflow Service → all | FME export from a reporting dataset failed |
| `EXTERNAL_EXPORT_DESIGN_COMPLETED_EVENT` | Dataflow Service → all | FME export from a design dataset succeeded |
| `EXTERNAL_EXPORT_DESIGN_FAILED_EVENT` | Dataflow Service → all | FME export from a design dataset failed |
| `EXTERNAL_EXPORT_EUDATASET_COMPLETED_EVENT` | Dataflow Service → all | EU dataset export succeeded |
| `EXTERNAL_EXPORT_EUDATASET_FAILED_EVENT` | Dataflow Service → all | EU dataset export failed |
| `CALL_FME_PROCESS_FAILED_EVENT` | Dataflow Service → all | FME REST API call failed (network or auth error) |

---

## Configuration

```yaml
integration:
  fme:
    host: fme.discomap.eea.europa.eu   # FME Server hostname
    scheme: https                       # Protocol
    token: <bearer-token>               # FME Server API authentication token
    callback:
      urlbase: <reportnet3-base-url>    # Base URL FME uses to POST callbacks
    default:
      repository: <repository-name>     # FME repository used when not specified on an integration
    eu:
      job: Export_EU_dataset.fmw        # FME workspace used for EXPORT_EU_DATASET operations
    topic: <kafka-topic>                # Kafka topic registered in FME notification directives
    polling:
      token: <polling-token>            # Token used by the Orchestrator polling job

scheduling:
  inProgress:
    import:
      fme:
        jobs:
          without:
            callback:
              max.time: 1800000         # ms to wait for a callback before treating as failed
```

**Operational notes.**

`integration.fme.default.repository` sets the fallback FME repository for any integration that does not specify one in its `REPOSITORY` internal parameter. If this property is wrong, job submissions for those integrations will fail with a 404 from FME Server.

`EXPORT_EU_DATASET` integrations are always created with `repository=ReportNetTesting` and `processName=Export_EU_dataset.fmw` hardcoded in `IntegrationServiceImpl.createDefaultIntegration()`. If the EU export workspace is renamed or moved to a different repository on FME Server, these values must be updated in the source code, not in configuration.

Lock acquisition in `addLocks()` acquires seven separate lock entries against the distributed lock table. If the service crashes between acquiring locks and releasing them, those lock entries will persist. Use the Orchestrator's Redis lock admin API (`GET /redis/getActiveRedisLocksByKey`) to inspect and manually release stuck locks.
