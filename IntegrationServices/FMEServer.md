# FME Server integration

FME Server (Feature Manipulation Engine, by Safe Software) is the external data transformation platform that Reportnet 3 uses for non-trivial import and export operations. Where a simple CSV upload can be handled entirely within Reportnet 3, an operation that requires coordinate reprojection, format conversion, conditional field mapping, or country-code-based routing is delegated to FME. The EEA operates its own FME Server instance at `fme.discomap.eea.europa.eu`; Reportnet 3 communicates with it over HTTPS via FME's REST API.

From Reportnet 3's perspective FME is a compute backend: a workspace (a transformation script authored in FME Desktop) is uploaded to FME Server once, and Reportnet 3 triggers executions of it with per-job parameters. FME does the heavy lifting; Reportnet 3 tracks the job, receives the result, and notifies the user. The integration is entirely asynchronous — a job is submitted and the result arrives either via a webhook callback from FME or, as a fallback, is detected by a polling job running every ten minutes.

FME is used for two main purposes: migrating legacy data from Reportnet 2 into Reportnet 3, and converting non-CSV input files (Excel, XML, custom formats) into the CSV format that Reportnet 3's native import pipeline expects. FME has been identified as a potential performance bottleneck — because it is a shared external service, concurrent jobs from multiple dataflows compete for the same FME Server capacity, and large files impose a long round-trip before Reportnet 3 can proceed with its own import pipeline.

The EEA has also developed an open-source **Reportnet 3 FME Reader package** that allows FME workspaces to read data directly from Reportnet 3 using a Dataflow ID and an API key. It is published on FME Hub (`hub.safe.com/publishers/eea/packages/reportnet`) and the EEA GitHub organisation. This makes Reportnet 3 a usable data source within FME, not only a target — useful for harvesting data out of the platform into downstream processes.

## Flow overview

```mermaid
flowchart TD
    DS[Dataset Service]
    DF[Dataflow Service :8020]
    ORC[Orchestrator Service]
    UMS[User Management Service]
    COMM[Communication Service]
    FME[FME Server\nfme.discomap.eea.europa.eu]
    FMEJOBS[(fme_jobs table)]
    ORCHDB[(orchestrator_db)]
    KAFKA[Kafka\nDATA_REPORTING_TOPIC]

    DS -->|CONTINUE_FME_PROCESS_EVENT| KAFKA
    KAFKA -->|ReplacingDataPreviousFMECallCommand| DF
    DF -->|upload file + submit job\nPOST /fmerest/v3/transformations/submit| FME
    DF -->|save FMEJob record| FMEJOBS
    DF -->|validate API key| UMS
    FME -->|POST /fme/operationFinished callback| DF
    ORC -->|poll GET /fmerest/v3/transformations/jobs/id/{id}\nevery 10 min| FME
    ORC -->|update job status| ORCHDB
    DF -->|completion events| KAFKA
    KAFKA -->|notify user| COMM
```

---

## Domain model

### Integration

An `Integration` record represents a configured link between a dataflow and an FME workspace. It stores the workspace name, which FME repository it lives in, and any custom parameters that workspace expects. A single dataflow can have multiple integrations covering different operations (import, export, EU dataset export). The configuration is split between two parameter tables:

**Internal parameters** (`integration_operation_parameters`) hold the fixed properties that Reportnet 3 manages:

| Parameter key | Purpose |
|---|---|
| `PROCESS_NAME` | The FME workspace filename to execute (e.g. `ImportReporting.fmw`) |
| `REPOSITORY` | The FME Server repository containing the workspace |
| `DATASET_SCHEMA_ID` | The MongoDB schema ID of the target dataset |
| `DATAFLOW_ID` | The dataflow this integration belongs to |
| `FILE_EXTENSION` | File extension expected for export output |
| `NOTIFICATION_REQUIRED` | Whether to send a user notification on completion |

**External parameters** (`integration_operation_parameters` with a different type flag) hold workspace-specific parameters defined by the workspace author — any extra inputs the FME workspace needs that are not covered by the standard set. These are passed through to FME verbatim. The only external parameter that is suppressed (never forwarded to FME) is `fileIS`, which would be a file content parameter that would conflict with the file-upload mechanism.

The `operation` field on the integration records what kind of work this configuration handles: `IMPORT`, `EXPORT`, `EXPORT_EU_DATASET`, or `IMPORT_FROM_OTHER_SYSTEM`.

### FMEJob

`FMEJob` (table `fme_jobs`, created in V16 and V17) is Reportnet 3's record of a single FME execution. It exists so the platform can correlate an incoming callback from FME with the user who triggered the operation, the dataset being affected, and the result that should follow.

| Field | Notes |
|---|---|
| `id` | Reportnet 3's internal job ID; this value is passed to FME as `rn3JobId` and returned in the callback, which is how the webhook endpoint knows which job has completed |
| `jobId` | The corresponding Orchestrator `Job` record ID |
| `datasetId` | The dataset being imported into or exported from |
| `dataflowId` | The parent dataflow |
| `providerId` | The data provider, if applicable; null for design dataset operations |
| `fileName` | The source file name (import) or expected output file name (export) |
| `userName` | The Reportnet 3 user who triggered the operation; used to verify the callback's API key belongs to the same user |
| `operation` | `IMPORT`, `EXPORT`, `EXPORT_EU_DATASET`, or `IMPORT_FROM_OTHER_SYSTEM` |
| `status` | `CREATED`, `QUEUED`, `SUCCESS`, or `FAILURE` |

### FMEUser

`FMEUser` (table `fme_user`, created in V40) stores FME Server authentication credentials. A `Dataflow` record with type `BUSINESS` has an `fme_user_id` foreign key pointing to an `FMEUser` row. In practice the password field is not used for authentication in the current implementation — authentication to FME Server uses a shared Bearer token from configuration rather than per-user credentials. The `FMEUser` table represents an earlier design intent that was not fully carried forward; the username field is currently the only meaningful value.

---

## How it works

### Submitting a job to FME

When a user triggers an integration execution (import or export), the Dataflow Service's `FMEIntegrationExecutorService` takes over. The sequence is:

1. A `FMEJob` record is created with status `CREATED`.
2. For import operations: the source file is uploaded to FME Server's shared filesystem. FME Server exposes a filesystem resource named `Reportnet3`; files are placed under the path `{datasetId}/{providerId}/` for reporting datasets or `{datasetId}/design/` for design datasets. The upload is a multipart POST with a two-hour timeout, because import files can be large.
3. For export operations: an `ExportFiles` directory is created in FME's filesystem at the same path (a `CONFLICT` response from FME, meaning the directory already exists, is treated as success).
4. An `FMEAsyncJob` object is built containing three sections:
   - **NMDirectives** — notification instructions. This includes the API key that FME should include in its callback, the `rn3JobId`, and the Kafka topics FME should fire on success or failure (used by FME's own notification engine).
   - **TMDirectives** — execution controls: run-till-completion flag, time-to-complete, queue time-to-live, priority, and optional routing tags.
   - **publishedParameters** — the workspace parameters. These always include `dataflowId`, `datasetId`, `apiKey`, `baseUrl`, `providerId`, `folder`, `rn3JobId`, and `notificationRequired`. Import jobs also pass `inputfile` (the uploaded filename); export jobs pass `exportFileName`. Any external parameters from the integration configuration are appended.
5. The assembled job is POSTed to `POST /fmerest/v3/transformations/submit/{repository}/{workspace}`. FME responds with a numeric job ID.
6. The FME job ID is stored on the `FMEJob` record, its status is updated to `QUEUED`, and the Orchestrator's `Job` record stores it in the `fmeJobId` field.

The submission step is wrapped in a Kafka-driven flow: the Dataset Service publishes a `CONTINUE_FME_PROCESS_EVENT` event, `ReplacingDataPreviousFMECallCommand` consumes it, routes through `IntegrationExecutorFactory` to `FMEIntegrationExecutorService`, and the above sequence runs. This decouples the original HTTP request from the FME submission and allows retries without blocking the caller.

### Receiving results: the callback webhook

FME Server is configured with a notification that POSTs to Reportnet 3's webhook endpoint when a job finishes. The endpoint is `POST /fme/operationFinished` on the Dataflow Service. The request body carries:

```json
{
  "apiKey": "ApiKey {user-api-key}",
  "rn3JobId": 12345,
  "StatusNumber": 0,
  "notificationRequired": true,
  "datasetId": 67890
}
```

`StatusNumber` is `0` for success and `-1` for failure. `rn3JobId` is the `FMEJob.id` that was passed to FME as a published parameter — this is the correlation handle.

Before processing the callback, `FMECommunicationService.authenticateAndAuthorize()` validates the API key against Keycloak through the User Management Service, then checks that the authenticated user matches the `FMEJob.userName` stored when the job was submitted. If the API key is invalid the endpoint returns HTTP 401; if it is valid but belongs to a different user, it returns HTTP 403. This prevents any FME workspace from triggering callbacks for jobs it did not originate.

On a successful callback:
- `FMEJob.status` is updated to `SUCCESS` or `FAILURE`.
- Import locks on the dataset are released.
- The appropriate Kafka event is published (`EXTERNAL_IMPORT_REPORTING_COMPLETED_EVENT`, `EXTERNAL_EXPORT_DESIGN_COMPLETED_EVENT`, etc.) and the Communication Service delivers a notification to the user's browser.

A special case exists for import operations: if FME reports success (`StatusNumber=0`) but the `fmeCallback` flag on the Orchestrator `Job` record is still false (meaning no file was delivered back), the service fires `FME_IMPORT_JOB_FAILED_EVENT_NO_FILE_RETURNED` to notify the user that FME finished but produced no output.

### Receiving results: the polling fallback

The callback mechanism depends on FME Server being able to reach Reportnet 3's webhook. If connectivity fails or FME's notification engine silently drops the callback, the job would hang forever. `JobForFmeStatusPolling` in the Orchestrator Service runs every ten minutes on a cron schedule (`0 */10 * * * *`) and polls `GET /fmerest/v3/transformations/jobs/id/{fmeJobId}` for every import job that is still `IN_PROGRESS` and has a non-null `fmeJobId`.

The response carries the FME-side status (`SUBMITTED`, `QUEUED`, `PULLED`, `ABORTED`, `FME_FAILURE`, `JOB_FAILURE`, or `SUCCESS`) and a `timeFinished` timestamp. The Orchestrator updates the `Job.fmeStatus` field and, on any failure status, immediately marks the Reportnet 3 job as failed, cancels the associated processes, removes locks, and sends a Kafka failure notification.

A specific time-out case handles jobs that FME reports as `SUCCESS` but for which no callback arrived. If `timeFinished` is older than `scheduling.inProgress.import.fme.jobs.without.callback.max.time` (default 30 minutes), the poller treats the job as failed and fires `FME_IMPORT_JOB_FAILED_EVENT_NO_FILE_RETURNED`.

### Downloading export results

For export operations, after FME completes it places the output file in the `ExportFiles` directory on FME's filesystem. Reportnet 3 retrieves it by calling `GET /fmerest/v3/resources/connections/Reportnet3/filesys/{datasetId}/{providerId}/ExportFiles/{fileName}?accept=contents&disposition=attachment`. The file bytes are streamed back to the user.

### The `IMPORT_FROM_OTHER_SYSTEM` operation

This operation type handles the case where data arrives from an external system that uses different country codes or data formats that require remapping before they can be loaded into a Reportnet 3 reporting dataset. In addition to the standard parameters, FME receives a `countryCode` parameter. The FME workspace is responsible for interpreting the source system's encoding and mapping it to Reportnet 3's schema.

### Workspace and repository discovery

The Dataflow Service provides two endpoints that allow the front-end to browse FME Server's content catalogue so users can select which workspace to associate with an integration:

- `GET /fmerest/v3/repositories?limit=-1&offset=-1` — lists all repositories on FME Server.
- `GET /fmerest/v3/repositories/{repository}/items?type=WORKSPACE` — lists all workspaces in a repository.

Both return `FMECollection` objects with `name`, `title`, `description`, and metadata fields. These are called at integration-configuration time, not at job execution time.

---

## Relationships with other services

**Dataflow Service.** Owns the `Integration`, `FMEJob`, and `FMEUser` entities. Hosts the `/fme/operationFinished` callback endpoint. Calls FME Server's REST API directly for file upload, directory creation, job submission, and workspace discovery. Publishes and consumes Kafka events to initiate and complete FME operations.

**Orchestrator Service.** Stores the `fmeJobId` and `fmeStatus` on its `Job` entity. Runs the polling cron job that detects failed or stalled FME jobs. Calls the Recordstore and Dataset Service to mark jobs and processes as failed when polling detects a problem.

**User Management Service.** Called by the Dataflow Service during callback authentication to validate the API key carried in the FME callback request. Without this call the webhook has no way to verify the callback is legitimate.

**Dataset Service.** Triggers FME integration execution by publishing `CONTINUE_FME_PROCESS_EVENT`. Receives completion notifications via Kafka and updates dataset state accordingly (e.g. marking an import as complete and refreshing the materialized view).

**Communication Service.** Receives the Kafka events published on FME completion and delivers real-time WebSocket notifications to the triggering user's browser.

---

## Process flows

### Import via FME

```
1. User uploads file to Dataset Service
2. Dataset Service: publishes CONTINUE_FME_PROCESS_EVENT
   payload: { datasetId, fileName, jobId, integrationId }
3. Dataflow Service: ReplacingDataPreviousFMECallCommand consumes event
4. IntegrationExecutorFactory → FMEIntegrationExecutorService
5. Create FMEJob record (status=CREATED)
6. POST /fmerest/v3/resources/connections/Reportnet3/filesys/{datasetId}/{providerId}
   (upload source file, 2-hour timeout)
7. Build FMEAsyncJob:
   - NMDirectives: { apiKey, rn3JobId, notificationRequired }
   - TMDirectives: { rtc=true, priority, ttc, ttl }
   - publishedParameters: { dataflowId, datasetId, apiKey, baseUrl, inputfile,
                             folder, rn3JobId, notificationRequired, + external params }
8. POST /fmerest/v3/transformations/submit/{repository}/{workspace}
   → returns fmeJobId (Integer)
9. Update FMEJob.status = QUEUED; store fmeJobId on Orchestrator Job record

--- FME executes workspace transformation ---

10a. FME POSTs to /fme/operationFinished
     body: { apiKey, rn3JobId, StatusNumber=0, datasetId }
     OR
10b. JobForFmeStatusPolling (every 10 min) polls FME status API

11. Validate API key via User Management Service
12. Verify API key owner matches FMEJob.userName
13. Update FMEJob.status = SUCCESS
14. Release dataset import locks
→ Kafka: EXTERNAL_IMPORT_REPORTING_COMPLETED_EVENT
→ Communication Service notifies user via WebSocket
```

### Export via FME

```
1. User requests export from Dataflow Service
2. Dataflow Service: IntegrationService.executeExternalIntegration()
3. Create FMEJob record (status=CREATED)
4. POST /fmerest/v3/resources/connections/Reportnet3/filesys/{datasetId}/{providerId}
   body: directoryname=ExportFiles  (create output directory)
5. Build FMEAsyncJob with exportFileName instead of inputfile
6. POST /fmerest/v3/transformations/submit/{repository}/{workspace}
7. Update FMEJob.status = QUEUED

--- FME executes workspace and writes output to ExportFiles/ ---

8. FME POSTs callback OR poller detects SUCCESS
9. Update FMEJob.status = SUCCESS
→ Kafka: EXTERNAL_EXPORT_REPORTING_COMPLETED_EVENT

10. User downloads result:
    GET /fmerest/v3/resources/connections/Reportnet3/filesys/
        {datasetId}/{providerId}/ExportFiles/{fileName}
```

### Polling fallback for stalled jobs

```
JobForFmeStatusPolling (cron: every 10 minutes)
1. Query Orchestrator DB: SELECT jobs WHERE status=IN_PROGRESS AND fmeJobId IS NOT NULL
2. For each job:
   GET /fmerest/v3/transformations/jobs/id/{fmeJobId}
   → { status: "FME_FAILURE" | "JOB_FAILURE" | "ABORTED" | "SUCCESS", timeFinished }
3a. If failure status:
    - Update Job.status = FAILED
    - Cancel associated Process records
    - Remove import locks
    → Kafka: FME_IMPORT_JOB_FAILED_EVENT
3b. If SUCCESS but no callback received AND timeFinished > maxWaitTime:
    - Update Job.status = FAILED
    → Kafka: FME_IMPORT_JOB_FAILED_EVENT_NO_FILE_RETURNED
3c. Otherwise: update Job.fmeStatus and continue waiting
```

---

## Configuration

```yaml
integration:
  fme:
    host: fme.discomap.eea.europa.eu    # FME Server hostname
    scheme: https                        # Protocol (https in production)
    token: <bearer-token>                # Bearer token for FME REST API authentication
    callback:
      urlbase: <reportnet3-base-url>     # Base URL FME uses to reach /fme/operationFinished
    default:
      repository: <repository-name>      # FME repository used when not specified on integration
    eu:
      job: <workspace-name>              # FME workspace for EU dataset export operations
    topic: <kafka-topic>                 # Kafka topic used for FME internal notifications
    polling:
      token: <polling-token>             # Token used by the polling job to call FME status API

scheduling:
  inProgress:
    import:
      fme:
        jobs:
          without:
            callback:
              max.time: 1800000          # ms before a SUCCESS-with-no-callback is treated as failed (default 30 min)
```

**`integration.fme.callback.urlbase`.** This must be reachable from FME Server. In a Kubernetes cluster behind a load balancer, this is the external ingress URL. If this property is misconfigured, FME will not be able to POST callbacks and all FME jobs will rely entirely on the 10-minute polling cycle to detect completion.

**`integration.fme.token`.** This is a long-lived FME Server API token. There is no token refresh mechanism in Reportnet 3; if the token expires on the FME side, all job submissions will fail with HTTP 401 from FME's REST API. The `CALL_FME_PROCESS_FAILED_EVENT` Kafka event will be published and the user will receive a failure notification.

**`scheduling.inProgress.import.fme.jobs.without.callback.max.time`.** The window between FME reporting success and Reportnet 3 timing out the job because no file arrived. Workspaces that produce large output files may need this value increased to prevent false failures. The default of 30 minutes is conservative; very large datasets may need 60–120 minutes.

---

## Kafka events summary

| Event | Direction | Trigger |
|---|---|---|
| `CONTINUE_FME_PROCESS_EVENT` | Dataset Service → Dataflow Service | User triggers import/export; routes to FME executor |
| `EXTERNAL_IMPORT_REPORTING_COMPLETED_EVENT` | Dataflow Service → all | Import to reporting dataset succeeded |
| `EXTERNAL_IMPORT_REPORTING_FAILED_EVENT` | Dataflow Service → all | Import to reporting dataset failed |
| `EXTERNAL_IMPORT_DESIGN_COMPLETED_EVENT` | Dataflow Service → all | Import to design dataset succeeded |
| `EXTERNAL_IMPORT_DESIGN_FAILED_EVENT` | Dataflow Service → all | Import to design dataset failed |
| `EXTERNAL_IMPORT_REPORTING_FROM_OTHER_SYSTEM_COMPLETED_EVENT` | Dataflow Service → all | `IMPORT_FROM_OTHER_SYSTEM` succeeded |
| `EXTERNAL_IMPORT_REPORTING_FROM_OTHER_SYSTEM_FAILED_EVENT` | Dataflow Service → all | `IMPORT_FROM_OTHER_SYSTEM` failed |
| `EXTERNAL_EXPORT_REPORTING_COMPLETED_EVENT` | Dataflow Service → all | Export from reporting dataset succeeded |
| `EXTERNAL_EXPORT_REPORTING_FAILED_EVENT` | Dataflow Service → all | Export from reporting dataset failed |
| `EXTERNAL_EXPORT_DESIGN_COMPLETED_EVENT` | Dataflow Service → all | Export from design dataset succeeded |
| `EXTERNAL_EXPORT_DESIGN_FAILED_EVENT` | Dataflow Service → all | Export from design dataset failed |
| `EXTERNAL_EXPORT_EUDATASET_COMPLETED_EVENT` | Dataflow Service → all | EU dataset export succeeded |
| `EXTERNAL_EXPORT_EUDATASET_FAILED_EVENT` | Dataflow Service → all | EU dataset export failed |
| `CALL_FME_PROCESS_FAILED_EVENT` | Dataflow Service → all | FME REST API call itself failed (HTTP error) |
| `FME_IMPORT_JOB_FAILED_EVENT` | Orchestrator Service → all | Poller detected FME failure status |
| `FME_IMPORT_JOB_FAILED_EVENT_NO_FILE_RETURNED` | Dataflow/Orchestrator → all | FME succeeded but sent no file back |

---

## Design notes

**Why two result-detection paths.** The callback webhook is the primary mechanism because it is immediate — the user sees the result as soon as FME finishes. But FME Server's notification engine is not guaranteed to fire in all failure scenarios (e.g. a network partition between FME and the callback URL). The polling fallback ensures that no job hangs indefinitely even if the callback never arrives. The cost of the fallback is up to ten minutes of latency between job completion and Reportnet 3 detecting it.

**Why `rn3JobId` is passed as an FME parameter.** The callback endpoint is unauthenticated at the HTTP level (no token in the URL); authentication is done by validating the API key in the request body. To close the gap between "this is a valid API key" and "this key belongs to the person who submitted this specific job", the `rn3JobId` is stored on the `FMEJob` record alongside the `userName`. On callback, the service validates that the API key authenticates as the same user. This means a compromised API key cannot be used to inject false completion events for other users' jobs.

**Why FMEUser exists but is not used for authentication.** The `fme_user_id` foreign key on `Dataflow` and the `FMEUser` table suggest an original design where different dataflows (particularly `BUSINESS` type) would authenticate to FME Server with different credentials, perhaps to partition access to FME repositories by organisation. The current implementation uses a single shared Bearer token instead. The `FMEUser` table remains in the schema and is referenced by `BUSINESS` type dataflows, but the credential it stores is not used in any active code path.
