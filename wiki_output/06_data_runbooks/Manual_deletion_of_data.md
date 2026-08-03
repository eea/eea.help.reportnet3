---
title: "Manual deletion of data"
---

# Manual deletion of data

During the data deletion of a dataset table with a very large amount of data in production the delete operation was never ending. We manually deleted the dataset data by opening a postgres sql console for the dataset and running the following query:

**truncate table record_value cascade;**

which will delete all records from table record_value and from related tables. This query can't be applied if the dataset contains more than 1 tables and only one of them needs to be deleted, as truncate will delete all data from all tables.

## Verification notes

The table name `record_value` is correct and matches the `RECORD_VALUE` entity defined in the Dataset Service's per-dataset schema. The `CASCADE` qualifier is appropriate because `field_value`, `record_validation`, `field_validation`, and `table_validation` rows all depend on records in `record_value` via foreign keys.

The caveat about multi-table datasets is accurate: `TRUNCATE record_value CASCADE` removes all records across all tables in the dataset, because all `record_value` rows share the same schema regardless of which `table_value` they belong to. For single-table deletion within a multi-table dataset, a `DELETE FROM record_value WHERE id_table = (SELECT id FROM table_value WHERE id_table_schema = '<targetSchemaId>')` pattern would be safer. This runbook does not suggest that alternative, which is a gap worth noting.
