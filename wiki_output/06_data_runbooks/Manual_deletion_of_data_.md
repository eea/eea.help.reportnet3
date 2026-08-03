---
title: "Manual deletion of data"
---

# Manual deletion of data

During the data deletion of a dataset table with a very large amount of data in production the delete operation was never ending. We manually deleted the dataset data by opening a postgres sql console for the dataset and running the following query:

**truncate table record_value cascade;**

which will delete all records from table record_value and from related tables. This query can't be applied if the dataset contains more than 1 tables and only one of them needs to be deleted, as truncate will delete all data from all tables.

## Verification notes

This file is a duplicate of `Manual_deletion_of_data.md`. The table name `record_value` is correct and matches the `RECORD_VALUE` entity in the Dataset Service's per-dataset schema. The `CASCADE` qualifier correctly handles dependent rows in `field_value`, `field_validation`, `record_validation`, and `table_validation`. The caveat about multi-table datasets is accurate. See `Manual_deletion_of_data.md` for the full verification note.
