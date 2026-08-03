---
title: "Fix cannot add records for attachment field"
---

# Fix cannot add records for attachment field

[Edit this section](Fix_cannot_add_records_for_attachment_field/edit.md)

### Need the dataset_schema_id, table_schema_ids and dataset_id

dataset_schema_id can be found in the dataset table in metabase.  
table_schema_ids can be found either in mongodb or in the url in the dataset page

[Edit this section](Fix_cannot_add_records_for_attachment_field/edit.md)

### Check and fix dataset_value

Check, in postgresql database datasets, if a record with the dataset_schema_id exists in dataset_[dataset_id].dataset_value  

[code]
    SELECT * FROM dataset_[dataset_id].dataset_value
    WHERE id_dataset_schema = '[dataset_schema_id]';
    
[/code]

If not add it  

[code]
    INSERT INTO dataset_[dataset_id].dataset_value VALUES(dataset_id, dataset_schema_id, false);
    
[/code]

[Edit this section](Fix_cannot_add_records_for_attachment_field/edit.md)

### Check and fix table_value

For each table:

Check, in postgresql database datasets, if a record with the table_schema_id exists in dataset_[dataset_id].table_value  

[code]
    SELECT * FROM dataset_[dataset_id].table_value
    WHERE id_table_schema = '[table_schema_id]';
    
[/code]

If not add it  

[code]
    INSERT INTO dataset_[dataset_id].table_value VALUES(nextval('table_sequence'), table_schema_id, dataset_id);
    
[/code]

## Verification notes

No source code verification applicable — operational runbook.

**Schema structure confirmed.** `DatasetValue.java` confirms the `DATASET_VALUE` table has columns `ID`, `ID_DATASET_SCHEMA`, and `VIEW_UPDATED` (boolean). The INSERT statement in the wiki — `VALUES(dataset_id, dataset_schema_id, false)` — maps to `(ID, ID_DATASET_SCHEMA, VIEW_UPDATED)` in that order. The `ID` column is serial (auto-generated) but the wiki supplies it explicitly as `dataset_id`; this is intentional since the wiki is inserting a row whose `ID` must equal the dataset's own ID, which is a specific Reportnet3 convention for `DATASET_VALUE`.

**Table sequence confirmed.** `TableValue.java` confirms the sequence generator is named `table_sequence`, matching the `nextval('table_sequence')` call in the INSERT. The `TABLE_VALUE` columns are `ID`, `ID_TABLE_SCHEMA`, and `DATASET_ID` (foreign key to `DATASET_VALUE`), which matches the three-value INSERT.
