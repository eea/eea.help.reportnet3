---
title: "Create new dataset from code"
---

# Create new dataset from code

[Edit this section](Create_new_dataset_from_code/edit.md)

#### In repo `eea.reportnet3` we can find the following scripts

[Edit this section](Create_new_dataset_from_code/edit.md)

##### Dataset initialization

  * `datasetInitCommands.txt`



[Edit this section](Create_new_dataset_from_code/edit.md)

##### Distribute dataset tables

  * these scripts do not include all tables 
    * `datasetDistribute.txt`
    * `datasetInitCommandsCitus.txt`
  * the following includes all tables 
    * `datasetInitCommandsCitusComplete.txt`



Of the distribution scripts, `datasetInitCommandsCitus.txt` is not being used (apart from in tests).

[Edit this section](Create_new_dataset_from_code/edit.md)

##### Script `datasetInitCommands.txt` is used in two rest endpoints

  * `RecordStoreControllerImpl.createSchemas()`
  * `RecordStoreControllerImpl.createEmptyDataset()`



[Edit this section](Create_new_dataset_from_code/edit.md)

##### Script `datasetDistribute.txt` (which has missing tables) is used in one rest endpoint

  * `RecordStoreControllerImpl.distributeTables()`



[Edit this section](Create_new_dataset_from_code/edit.md)

##### Script `databaseInitCommandsCitusComplete.txt` (which includes all tables) is used in a cron job configured in CitusJob.

This job references a property `enableTableDistributionJob` which should be the cron job expression.  
If not set, the job is never scheduled, so the complete distribution never runs.  
Property enableTableDistributionJob cannot be found in any application file, so it must be set externally.

## Verification notes

The file names and their roles are confirmed by `JdbcRecordStoreServiceImpl`. The three resource files are injected as Spring `@Value` classpath resources:

- `datasetInitCommands.txt` → field `resourceFile` — used by `createEmptyDataSet()` and `createSchemas()`, confirming the two endpoints named in the wiki.
- `datasetDistributeCitus.txt` → field `resourceDistributeFile` — used by `distributeTables()`, confirming the endpoint `RecordStoreControllerImpl.distributeTables()`. The wiki names this file `datasetDistribute.txt`; the actual filename on disk and in the code is `datasetDistributeCitus.txt`. This is a discrepancy.
- `datasetInitCommandsCitusComplete.txt` → field `resourceCitusFile` — used by `distributeTablesJob()`, which is called from `CitusJob.executeTableDistribution()`. The cron job is configured via `@Value("${enableTableDistributionJob}")` but the scheduler code is entirely commented out in the current source. `CitusJob.init()` logs "Cronjob for CitusJob scheduler is disabled" and never schedules the task regardless of the property value. The wiki's claim that "if not set, the job is never scheduled" is partially correct in outcome but misleading about the mechanism: the job is unconditionally disabled in the source, not conditionally disabled by the property.
- `datasetInitCommandsCitus.txt` → field `resourceDistributeFirstFile` — the wiki correctly states this file is only used in tests. The production code injects it but there is no method in `JdbcRecordStoreServiceImpl` that reads from `resourceDistributeFirstFile`; it appears as an unused injected field.

All five resource files (`datasetInitCommands.txt`, `datasetInitCommandsCitus.txt`, `datasetInitCommandsCitusComplete.txt`, `datasetDistributeCitus.txt`, `datasetInitCommandsCitusComplete.txt`) are confirmed to exist under `recordstore-service/src/main/resources/`.

The content of all distribution scripts uses `SELECT create_reference_table(...)` exclusively. No `SELECT create_distributed_table(...)` call exists in any of these files. All per-dataset tables are therefore registered as Citus reference tables.
