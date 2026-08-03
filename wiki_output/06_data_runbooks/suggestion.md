# Runbook verification — suggestions for improvement

This document summarises the findings from verifying the runbooks in `06_data_runbooks/` against the migration files in `eea.reportnet3/database/src/main/resources/db/migration/` and the source-derived documentation in `CoreDomain/` and `Persistence/`. Issues are grouped by severity.

---

## Critical — will cause SQL errors if run as written

### `Deletion_of_old_dataflows_in_the_database.md`

**Missing delete from `representative_leadreporter`.** The `representative_leadreporter` table (created in `V32__modify_representative_tables.sql`) has a foreign key to `representative` with no `ON DELETE CASCADE`. Step 4 deletes from `representative` without first deleting the corresponding lead reporter rows. This will fail with a FK constraint violation. Add the following before the `representative` delete:

```sql
delete from representative_leadreporter where representative_id in (
    select id from representative where dataflow_id in (dataflowIdToBeDeleted)
);
```

**Missing delete from `contributor`.** The `contributor` table has a FK to `dataflow`. If any contributors exist, the final `delete from dataflow` will fail. Add before the `dataflow` delete:

```sql
delete from contributor where dataflow_id in (dataflowIdToBeDeleted);
```

**Missing delete from `process`.** The `process` table (V65) has a `dataflow_id` column. Process rows for the dataflow being deleted must be cleaned up before the `dataflow` row can be removed.

### `Delete_provider_data_from_dataflow.md`

**Missing delete from `representative_leadreporter`.** Step 3 deletes from `representative` but does not first delete from `representative_leadreporter`. This will fail with a FK constraint violation. Add before Step 3:

```sql
delete from representative_leadreporter where representative_id in (
    select id from representative where dataflow_id = your_dataflowId and data_provider_id = your_provider_id
);
```

**Missing delete from `snapshot`.** The `snapshot` table references `reporting_dataset` via `REPORTING_DATASET_ID`. If snapshots exist for the reporting datasets being deleted, the delete from `dataset` in Step 2 will fail. Add before Step 2:

```sql
delete from "snapshot" where reporting_dataset_id in (
    select id from dataset where dataflowid = your_dataflowId and data_provider_id = your_provider_id
);
```

---

## Significant — incorrect technical claims

### `Get_lock_record_information.md`

**Wrong table name.** The runbook's prose refers to "table: locks" (plural). The actual table name in the metabase is `public.lock` (singular), as defined in `V1__Init_Metabase_BD.sql`. Any SQL written from this runbook targeting a `locks` table will fail with a relation-not-found error. All references should read `lock`.

### `Create_new_database_in_postgres.md`

**DDL is outdated.** The `jobs` and `job_history` DDL shown matches only the initial schema from `V1__Create_Job_And_Job_history_Persistance.sql`. The subsequent migrations have:

- Dropped `process_id` from both tables (V2).
- Added `release`, `dataflow_id`, `provider_id`, and `dataset_id` to both tables (V2).
- Created a separate `job_process` table linking jobs to process IDs (V2/V3).
- Added `preparation_code` to `jobs` (V4).

Running this DDL will create tables that are incompatible with the application's JPA entities. Flyway should be used to initialise the schema automatically. If manual DDL is truly needed, it must incorporate all four migrations.

---

## Moderate — gaps or missing context

### `Add_provider_to_dataflow.md`

The `data_provider` table uses a plain `int8` primary key with no auto-increment sequence. The runbook instructs operators to "add new record with next id" but does not explain how to determine the next safe ID. It also does not mention that `group_id` (FK to `data_provider_group`) must be set correctly, as the Dataflow Service uses the group type to determine how providers are treated in BUSINESS-type dataflows.

### `Manual_deletion_of_data.md` / `Manual_deletion_of_data_.md`

The runbook correctly warns that `TRUNCATE record_value CASCADE` removes all data across all tables in a dataset. However, it does not provide the safer alternative for single-table deletion in a multi-table dataset:

```sql
DELETE FROM record_value WHERE id_table = (
    SELECT id FROM table_value WHERE id_table_schema = '<targetSchemaId>'
);
```

This leaves field_validation and field_value rows orphaned, which would require a follow-up clean-up step, but it restricts the deletion scope correctly. The runbook should document this alternative.

### `Add_or_Recreate_missing_public_files_in_dataflow.md`

The "Re-creating missing files" section references a POST API call without naming the endpoint. Operators need the endpoint URL to perform this operation. The attached Postman collection should either be referenced explicitly or the endpoint should be named in the document.

---

## Minor — duplicates and documentation quality

### Duplicate files

Three pairs of runbooks contain identical content:
- `Access_containers_with_kubectl.md` and `Access_containers_with_kubectl_.md`
- `Manual_deletion_of_data.md` and `Manual_deletion_of_data_.md`
- `Admin_push__Create_Permissions__button.md` and `As_an_Admin_push__Create_Permissions__button.md`

These duplicates increase maintenance burden. They should either be merged (keeping one canonical file) or one should be converted to a redirect/stub linking to the other.

### `Import_Reference_Datasets.md`

This document retains extensive draft annotations in the form of `? QUESTION:` blocks with inline answers. These should be resolved and incorporated into the prose, then the question-and-answer format removed before the document is published as finished documentation.

### `Admin_push__Create_Permissions__button.md` / `As_an_Admin_push__Create_Permissions__button.md`

Both documents read as code walkthroughs rather than operational runbooks. They describe the implementation of `validateAllReporters` in detail but do not explain when an operator should invoke the endpoint, how to confirm it has completed successfully, or what to do if the Kafka event is not emitted. An operational runbook should lead with the trigger condition ("use this when...") and include a confirmation step.

---

## Confirmed correct — no action needed

- `Delete_bad_records_from_dataset.md` — table names `field_value` and `record_value` are correct; deletion order is safe.
- `Deletion_of_hidden_records_in_dataset_.md` — table names `field_validation`, `field_value`, `record_value` are correct; deletion order respects FK constraints.
- `Import_Reference_Datasets.md` (endpoints) — `PUT /referenceDataset/{datasetId}`, `POST /dataset/v2/importFileData/{datasetId}`, `POST /dataset/v1/{datasetId}/etlImport`, and `GET /orchestrator/jobs/pollForJobStatus/{jobId}` are all confirmed correct against the source code.
- `Clone_dataflow_.md` — consistent with schema export/import and CSV zip import mechanisms.
- `Change_schema_in_Datalakes_.md` — consistent with the big-data design-mode constraints described in `dataset.md`.
- `Copy_data_collections_to_eu_dataset_problems_.md` — the `lock` table reference is correct (see note on table name above).
- `Import_file_through_external_integration.md` — consistent with the integration configuration model.
