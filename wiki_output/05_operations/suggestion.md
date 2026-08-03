# Suggestions for improving the operations wiki

This document records actionable improvements identified during verification of the `05_operations/` wiki pages against the Reportnet 3 source code and source-derived documentation.

---

## Critical corrections

### `Handle_stuck_jobs.md` — wrong HTTP method for `checkLocks`

The runbook shows the lock-check endpoint used as an HTTP GET with query parameters in a browser URL:

```
https://api.reportnet.europa.eu/dataset/checkLocks?dataflowId=123&dataProviderId=&datasetId=
```

In `DatasetControllerImpl.java` the endpoint is declared `@PostMapping(value = "/checkLocks")`. It is a POST request, not a GET. The `dataflowId`, `dataProviderId`, and `datasetId` values are `@RequestParam` values, which means they can be passed as query string parameters on a POST, but the endpoint will not respond to a GET at all. The runbook should be updated to show a `curl -X POST` or API client call rather than a URL that implies a browser GET.

### `Handle_stuck_jobs.md` — "FINALIZE task type" does not exist in current code

The section "Job has status IN_PROGRESS and in the tasks table there are two FINALIZE tasks" implies there is a `FINALIZE` task type. The `TaskType` enum (`common-interfaces/.../vo/metabase/TaskType.java`) contains only: `VALIDATION_TASK`, `IMPORT_TASK`, `RELEASE_TASK`, `COPY_TO_EU_DATASET_TASK`, `RESTORE_REPORTING_DATASET_TASK`, `RESTORE_DESIGN_DATASET_TASK`, and `COPY_REFERENCE_DATASET_TASK`. There is no `FINALIZE` value. Either the section refers to an informal label applied in a SQL query (not a persisted enum value), or this procedure describes a state that no longer arises in the current schema. The section needs clarification — either explain that `FINALIZE` is the literal string value stored in an older `task_type` column, or update/remove the section if this case no longer occurs.

### `Postgres_recovery_in_kubernetes.md` — typo makes the security context patch invalid

The `securityContext` snippet shows `"fsaGroup": 2000`. The correct Kubernetes field name is `"fsGroup"`. As written, the patch will be accepted by Kubernetes but the `fsGroup` setting will not take effect, so the pod may not be able to write to the volume. This should be corrected to `"fsGroup": 2000`.

### `Released_data_not_visible_in_public_page.md` — `dc_released` column not mentioned

The procedure sets `date_released` and `restrict_from_public` in the `snapshot` table but does not mention `dc_released`. According to `V18__Alter_Snapshot_Add_EUDataset.sql`, the `dc_released` column (renamed from `release`) controls whether the snapshot is considered released to the data collection. If `dc_released` is `false`, setting `date_released` alone may not make the data visible publicly. The procedure should instruct operators to also verify and set `dc_released = true` on the relevant snapshot row.

---

## Significant gaps

### `Operation_guidelines.md` — missing Orchestrator Service entirely

The document, last updated in October 2020, predates the Orchestrator Service. There is no `config/orchestrator/` Consul key section, no Zuul route for the orchestrator, and the "Restart a particular process" section lists only the original eight services (`api-gateway, dataflow, dataset, validation, communication, document, ums, rod`). Three services present in the current codebase are not listed at all: `orchestrator`, `collaboration`, and `indexsearch`. The document should be updated to add Consul key tables and deployment names for these services.

### `Operation_guidelines.md` — hardcoded environment-specific values are misleading

The metrics endpoint table lists specific NodePort values on `kvm-rn3prod-04.pdmz.eea` (e.g. port `32727` for API Gateway). These change with every redeployment and will not match any environment other than the one they were recorded from. The table should either be removed in favour of a note explaining how to find the current NodePorts (`kubectl -n reportnet get svc`), or clearly labelled as a snapshot from a specific date.

### `BackupRestore_plan.md` — no backup procedure for Metabase or Datasets databases

The `Postgres_daily_backup.md` page provides a CronJob manifest that backs up only the Keycloak database. There is no equivalent automated backup for the Metabase DB or the Datasets DB, which are arguably more critical for application recovery. A dedicated backup CronJob for each should be created and documented.

### `Fix_stuck_processes_.md` — Citus reference is unexplained

The document opens with "If citus is in recovery mode". Citus is not referenced anywhere else in the documentation or source code. This context is confusing to a reader unfamiliar with the platform's history. Either explain briefly what Citus was (a formerly evaluated sharding extension), confirm that the procedure is also valid outside of Citus recovery, or remove the Citus qualifier and describe the trigger conditions more generically (e.g. "after a database failover or a deployment that interrupted running processes").

---

## Minor issues and improvements

### `Locate_mongo_record_duplicates.md` — typographical error in heading

Line 73 reads "Search the PKCataglogue records". The collection name is `PKCatalogue`. This should be corrected to avoid confusion when operators are searching for the correct collection name.

### `Check_And_Fix_Database_Errors.md` — `mongo` shell command may be obsolete

The procedure instructs operators to type `mongo` to enter the MongoDB shell. From MongoDB 5.0 onwards the `mongosh` (MongoDB Shell) replaces the legacy `mongo` binary. If the MongoDB cluster has been upgraded beyond version 4.x, `mongo` will not be available and the command should be `mongosh`. The document should note which version is deployed and use the appropriate shell command.

### `Handle_stuck_jobs.md` — `JobForRemovingIcebergTablesWithExpiredEditingLocks` not documented

The file `JobForRemovingIcebergTablesWithExpiredEditingLocks.java` exists in the orchestrator scheduling package but is not mentioned in the Scheduled Tasks section of `Handle_stuck_jobs.md`. While this job does not relate directly to stuck jobs, the Scheduled Tasks section appears to be a comprehensive reference and the omission is inconsistent. It should be added with a note that it targets Iceberg big-data dataflow editing locks, not the standard job queue.

### `FME_processes.md` — schedules should be independently verified

The page lists specific FME schedule times (e.g. `WISE_RN3_METADATA_WIGEON` at 20:00 and 08:00 daily). These are recorded from 2023 and may have changed. Someone with access to the FME Server should verify these schedules periodically. The page should include a note that the schedule information was last verified in August 2023 and must be checked against the live FME Server configuration before being acted upon.

### `BackupRestore_plan.md` — path inconsistency in restore procedure

The restore procedure uses a `postgis/postgis` Docker image but navigates to `/bitnami/postgresql/dump` inside the container. The Bitnami path is correct for the production Bitnami-based Kubernetes pods, not for the intermediate `postgis/postgis` container which stores data under `/var/lib/postgresql`. The procedure should clarify that this path applies only when accessing the production pod shell via `docker exec`, not to the intermediate standalone container created during the restore.

---

## Staleness summary

| File | Last updated | Staleness assessment |
|---|---|---|
| `Operation_guidelines.md` | 2020-10-02 | High — missing three services, hardcoded endpoints, Rancher v1 URLs |
| `FME_processes.md` | 2023-08-21 | Medium — FME schedules may have changed |
| `Released_data_not_visible_in_public_page.md` | 2023-11-09 | Low — procedure is correct but incomplete (missing `dc_released`) |
| `Handle_stuck_jobs.md` | 2025-12-19 | Low — one wrong HTTP method, one ambiguous task type |
| `Replicated_Postgres_troubleshooting.md` | 2026-03-13 | Low — content is brief and accurate |
| All others | No date or pre-2023 | Procedural content; accuracy depends on infrastructure not source |
