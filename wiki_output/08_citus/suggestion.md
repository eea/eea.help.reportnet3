---
title: "Citus documentation — suggested additions and corrections"
---

# Citus documentation — suggested additions and corrections

This document records the findings from verifying the five Citus wiki pages against the `eea.reportnet3` source code, specifically `recordstore-service/src/main/java/` and `recordstore-service/src/main/resources/`. It is intended as a guide for anyone updating the wiki.

---

## The most important missing fact: reference tables, not distributed tables

Every wiki page in this folder implicitly assumes that Reportnet3 uses Citus's sharded distributed tables. It does not. All per-dataset tables are registered as Citus **reference tables** using `SELECT create_reference_table(...)`. There is no `SELECT create_distributed_table(...)` call anywhere in the codebase.

Reference tables are replicated in full to every node in the cluster, including the coordinator. They do not have a distribution column, do not have shards in the traditional sense, and do not benefit from parallel query across workers in the way that distributed tables do. The implication is:

- `rebalance_table_shards()` and `citus_drain_node()` do nothing useful on a cluster where all tables are reference tables. This explains the findings in `Citus_findings_coordinator_workers.md`.
- Adding or removing a worker node does not require shard rebalancing. Instead, reference table copies must be replicated to new workers with `SELECT replicate_reference_tables()`.
- The coordinator holding copies of all data is not a misconfiguration — it is the expected behaviour of reference tables.

A new deep-dive document for Citus in Reportnet3 should open with this architectural decision and explain why reference tables were chosen over distributed tables. The most plausible reason is that cross-table joins (record–field–validation) are frequent and reference tables avoid cross-shard joins entirely, at the cost of storing the full dataset on every node.

---

## Shard strategy and distribution column

Because reference tables are used, there is no distribution column. The concept does not apply to the current deployment. The `pg_dist_partition` system table is queried in `JdbcRecordStoreServiceImpl.getNotdistributedDatasets()` solely to identify which dataset schemas have not yet had `create_reference_table` called on them:

```sql
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name LIKE 'dataset_%'
  AND schema_name NOT IN (
    SELECT replace(logicalrelid::text, '.dataset_value', '')
    FROM pg_dist_partition
    WHERE logicalrelid::text LIKE '%dataset_value'
  )
ORDER BY random()
LIMIT <batchDistributeDataset>
```

This query treats the absence of a row in `pg_dist_partition` for `<schema>.dataset_value` as a signal that the schema has not been distributed yet. The batch size is controlled by the Consul KV property `batchDistributeDataset`.

---

## Which tables are distributed and which are not

All eleven per-dataset tables are registered as reference tables when `datasetInitCommandsCitusComplete.txt` is applied:

| Table | Citus type | File that registers it |
|---|---|---|
| `dataset_value` | reference table | `datasetInitCommandsCitusComplete.txt` |
| `table_value` | reference table | `datasetInitCommandsCitusComplete.txt` |
| `record_value` | reference table | `datasetInitCommandsCitusComplete.txt` |
| `field_value` | reference table | `datasetInitCommandsCitusComplete.txt` |
| `attachment_value` | reference table | `datasetInitCommandsCitusComplete.txt` |
| `validation` | reference table | `datasetInitCommandsCitusComplete.txt` |
| `dataset_validation` | reference table | `datasetInitCommandsCitusComplete.txt` |
| `table_validation` | reference table | `datasetInitCommandsCitusComplete.txt` |
| `record_validation` | reference table | `datasetInitCommandsCitusComplete.txt` |
| `field_validation` | reference table | `datasetInitCommandsCitusComplete.txt` |
| `temp_etlexport` | reference table | `datasetInitCommandsCitusComplete.txt` |

The `datasetInitCommandsCitus.txt` file registers only the first five tables (omitting the validation tables and `temp_etlexport`). It is used only in test code and should not be applied in production.

The `datasetDistributeCitus.txt` file registers only the six validation tables and `temp_etlexport`. It is used by `distributeTables()`, the REST endpoint `PUT /private/dataset/create/dataCollection/finish/{datasetId}`. This means the full set of eleven tables is only registered when both `datasetInitCommands.txt` (which creates the tables) and `datasetDistributeCitus.txt` (which registers the validation tables) have been applied, or when `datasetInitCommandsCitusComplete.txt` is applied by the cron job path. The split is worth documenting explicitly.

---

## How the Record Store Service abstracts Citus

The `JdbcRecordStoreServiceImpl` class is the sole point of interaction with Citus. It abstracts three operations:

1. **Schema and table creation** — `createEmptyDataSet()` and `createSchemas()` both read `datasetInitCommands.txt` and execute its SQL line by line after substituting `%dataset_name%` with the actual schema name (`dataset_<id>`) and `%user%` with the configured PostgreSQL user. This creates the schema and all eleven tables as plain PostgreSQL tables (no Citus registration yet).

2. **Partial reference table registration** — `distributeTables()` reads `datasetDistributeCitus.txt` and calls `create_reference_table` on the six validation tables and `temp_etlexport`. This is triggered by the REST endpoint called at the end of a DataCollection creation flow.

3. **Full reference table registration** — `distributeTablesJob()` reads `datasetInitCommandsCitusComplete.txt` and calls `create_reference_table` on all eleven tables. This was intended to be triggered by a scheduled cron job (`CitusJob.executeTableDistribution()`), but the scheduling code is commented out in the current source. The job can only be triggered if the commenting-out is reversed and `enableTableDistributionJob` is set to a valid cron expression via Consul. At present this path is effectively dead code.

---

## Specific corrections needed in the wiki

### `Reportnet3_citus_setup.md`

- Steps 5 and 6 both contain a path typo: `recordsotre-service` should be `recordstore-service`.
- Step 6 says to apply `datasetInitCommandsCitusComplete.txt`. This registers all tables as reference tables. The document should make clear that these are reference tables, not sharded distributed tables, and explain what that means for the cluster topology.
- The Citus version is not stated. The image tag `eeacms/citus-postgis:2022-06-27T0919` identifies the build date but not the Citus or PostgreSQL version inside it.

### `Create_new_dataset_from_code.md`

- The file `datasetDistribute.txt` named in the wiki does not exist. The actual filename is `datasetDistributeCitus.txt`. This should be corrected.
- The statement that `CitusJob` runs if `enableTableDistributionJob` is set is outdated. The scheduler code is commented out; the job never runs in the current source regardless of the property value.

### `Add_worker_node.md`

- Uses `--net citus_demo_network` but the setup guide does not create a named network. The two documents are inconsistent.
- Missing step: after adding a worker, `SELECT replicate_reference_tables()` must be run to push existing reference table data to the new node.

### `Remove_worker_node.md`

- The drain step (step 1) may be a no-op on a cluster that uses only reference tables, since there are no distributed-table shard placements to move. Operators should verify this against the live cluster before relying on the drain to make the node empty before removal.

### `Citus_findings_coordinator_workers.md`

- Findings 3 and 4 (coordinator retaining shards despite `rebalance_table_shards` and `citus_drain_node`) are not anomalies. They are the expected behaviour when all tables are reference tables. This context should be added to the document so the reader does not conclude that the cluster is misconfigured.

---

## Consul KV properties to document

The following properties are referenced in `JdbcRecordStoreServiceImpl` and are not documented anywhere in the wiki:

| Property | Purpose |
|---|---|
| `batchDistributeDataset` | Maximum number of undistributed dataset schemas to register as reference tables in a single `CitusJob` execution |
| `enableTableDistributionJob` | Cron expression for the `CitusJob` scheduler; currently unused because the scheduling code is commented out |
| `dataset.users` | Comma-separated list of PostgreSQL users granted privileges on each new dataset schema |
