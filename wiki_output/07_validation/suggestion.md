---
title: "Validation wiki — documentation suggestions"
---

# Validation wiki — documentation suggestions

This document identifies gaps, errors, and missing coverage in the current validation wiki pages, based on comparison against the validation-service source code and the `CoreDomain/validation.md` deep-dive.

---

## What the validation engine actually is

The current wiki pages never name the validation engine. A developer coming to these pages for the first time will not know that:

- For datasets backed by PostgreSQL (Citus), validation is driven by **Drools**. Rules are compiled into a `KieBase` via a Velocity template (`templateRules.drl`) by `KieBaseManager`. Each rule becomes a Drools rule with a `when` clause derived from the rule's `whenCondition` and a `then` clause that calls `ValidationRuleDrools.fillValidation()`.
- For big-data datasets backed by S3 and Dremio, there is **no Drools**. Rules are dispatched as Kafka commands to three specialised Java executors: `DremioSqlRulesExecuteServiceImpl`, `DremioNonSqlRulesExecuteServiceImpl`, and `DremioExpressionRulesExecuteServiceImpl`. These evaluate rules directly against Dremio via REST or JDBC.
- Drools is documented internally as being phased out in favour of the native Java evaluation pattern that the Dremio path already uses.

This distinction is the single most important architectural fact about the validation engine and it is entirely absent from the wiki.

---

## What rule types exist

The `AutomaticRuleTypeEnum` defines seven automatic rule types: `FIELD_TYPE`, `FIELD_SQL_TYPE`, `FIELD_CARDINALITY`, `TABLE_COMPLETNESS`, `FIELD_LINK`, `TABLE_UNIQUENESS`, and `MANDATORY_TABLE`. The `EntityTypeEnum` defines the four scope levels for all rules: `FIELD`, `RECORD`, `TABLE`, `DATASET`. None of the current wiki pages explain this taxonomy.

Custom rules fall into three categories not described anywhere in the wiki: field-level expression rules (boolean expression referencing the field value), record-level expression rules (operator tree using `recordIfThen`, `recordAnd`, `recordOr` etc., stored in `expressionText`), and table-level SQL rules (a designer-written `SELECT` returning failing `record_id` values). Understanding the distinction matters because each type follows a different execution path and has different validation requirements (SQL rules must pass `validateSqlRule` before they can be activated).

---

## End-to-end flow a developer needs to understand

No single wiki page explains the full lifecycle of a validation job. The following is what a developer would need to know and where to look in the source:

1. **Job creation.** A user or external caller sends `PUT /orchestrator/jobs/addValidationJob/{datasetId}`. The Orchestrator's `JobServiceImpl.checkEligibilityOfJob()` determines whether the job should be `QUEUED` or `REFUSED`. The check is broader than the wiki states: any active `VALIDATION`, `RELEASE`, `IMPORT`, `ETL_IMPORT`, or `DELETE` job for the same dataset will cause a refusal, not just validation jobs.

2. **Execution trigger.** The Orchestrator scheduler (`JobForExecutingQueuedJobs`) picks up the queued job and calls `PUT /validation/dataset/{id}` on the Validation Service (`ValidationControllerImpl.validateDataSetData()`). This endpoint creates a process record via the Recordstore Service and then delegates to either `ValidationHelper.executeValidation()` (Citus path) or `ValidationHelper.executeValidationDL()` (Dremio path) depending on whether the dataflow has `bigData=true`.

3. **Task dispatch via Kafka.** Both paths break the run into tasks and publish Kafka commands. The PostgreSQL path publishes `COMMAND_VALIDATE_FIELD`, `COMMAND_VALIDATE_RECORD`, `COMMAND_VALIDATE_TABLE`, and `COMMAND_VALIDATE_DATASET` events. The data lake path publishes `COMMAND_VALIDATE_DL` (field/non-SQL rules via `ExecuteValidationCommandDL`), `COMMAND_VALIDATE_EXPRESSION_DL` (record-level expression rules), `COMMAND_VALIDATE_DL_WITH_SQL` (SQL rules and constraints), and `COMMAND_VALIDATE_EMPTY_RULE` for rules with no active condition.

4. **Task scheduling within the Validation Service.** The `ValidationScheduler` runs on a fixed schedule. It reads whether this instance is configured as `HIGH` or `LOW` priority (Consul key `validation.instance.priority`) and applies either `HighPriorityTaskReaderStrategy` or `LowPriorityTaskReaderStrategy` to decide which process tasks to pick up next. The process priority (20–70) is calculated by `ValidationHelper.getPriority()` based on the dataflow's deadline relative to today, using thresholds from `validation.priority.days`.

5. **Results storage.** PostgreSQL-path failures are written to `field_validation`, `record_validation`, `table_validation`, and `dataset_validation` tables. Dremio-path failures are written as Parquet files to the `_validate/` folder in S3. The two result stores are read by `LoadValidationsHelper` and `LoadValidationsHelperDL` respectively, both exposed via `GET /validation/listGroupValidations/{id}` and `GET /validation/listGroupValidationsDL/{id}`.

6. **Completion signal.** When all tasks for all processes in the job finish, `ValidationHelper` publishes `VALIDATION_FINISHED_EVENT` to Kafka. The Orchestrator picks this up to close the job and trigger downstream steps (release, notifications). There are also several failure events: `VALIDATION_FAILED_SYSTEM_ERROR_EVENT`, `VALIDATION_FAILED_ICEBERG_EXISTS_EVENT`, `VALIDATION_FAILED_ILLEGAL_CHARACTER_EVENT`, and `VALIDATION_FAILED_DATASET_LOCKED_FOR_EDITING_EXISTS_EVENT`.

---

## Specific corrections to existing pages

### `Validation_.md`

The property controlling the maximum number of concurrent in-progress validation jobs is `scheduling.inProgress.validation.maximum.jobs`, not `scheduling.inProgress.import.maximum.jobs` as stated. These are separate properties in `JobServiceImpl.java` (lines 69 and 72).

### `Validation_Priority_Model.md`

The priority table is missing a level. The source (`ValidationHelper.getPriority()`) produces six priority values: 70, 60, 50, 40, 30, and 20. The wiki table shows only five, omitting priority 60 (which applies when the deadline exists but is further away than `periodDays[0]` in either direction — very far future or very far past). The day thresholds in the wiki (90, 60, 30, 7) are plausible defaults but are entirely configurable via `validation.priority.days` and not hardcoded.

### `Check_if_dataflow_validation_is_stuck.md`

The SQL query contains `interval '3::hours'`, which is invalid PostgreSQL syntax. The correct form is `INTERVAL '3 hours'`. The `WHERE dataset_id = dataset_id` clause is also a self-comparison that will always be true. A corrected query would be:

```sql
SELECT *, AGE(now(), date_start)
FROM process
WHERE dataset_id = <target_dataset_id>
  AND status = 'IN_PROGRESS'
  AND date_finish IS NULL
  AND AGE(now(), date_start) > INTERVAL '3 hours';
```

The page also omits mention of the API-level equivalents: `GET /validation/listInProgressValidationTasks/{timeInMinutes}` lists task IDs exceeding a time threshold, and `PUT /validation/restartTask/{taskId}` can restart a stuck task without touching the database directly.

### `Fix_export_for_NULL_values.md`

This page is filed under the validation wiki but the `EXPORT_DATASET_FAILED_EVENT` is owned by the Dataset Service (`FileTreatmentHelper.java`, `ExportDatasetFailedEvent.java`). The fix involves the `field_value` table in the datasets PostgreSQL schema, which has no connection to the Validation Service. The page would be better placed under a dataset or export section.

---

## Missing pages

The following topics are not covered anywhere in the current wiki but represent common developer needs:

- **How to write and validate a SQL rule.** The `POST /rules/validateSqlRule` → `POST /rules/runSqlRule` workflow for creating and testing table-level SQL rules is the most common rule authoring task and has no page.
- **Rule import and export.** `POST /rules/exportQC/{datasetId}` and `POST /rules/importRulesSchema` are used routinely when setting up new dataflows based on existing schemas. No page describes the CSV format or the caveats around importing rules into a schema with different field IDs.
- **Cancellation and restarting validation.** There is no page explaining what happens when a task is cancelled (the `BLOCKER` severity implication for releases), how to use `PUT /validation/restartTask/{taskId}`, or when to use `DELETE /validation/deleteLocksToReleaseProcess/{datasetId}`.
- **The Drools vs Dremio path decision.** No page explains when a dataset uses one path vs the other, or what the `bigData` flag on a dataflow means in practice.
