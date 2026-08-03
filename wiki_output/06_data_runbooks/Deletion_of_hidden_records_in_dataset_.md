---
title: "Deletion of hidden records in dataset"
---

# Deletion of hidden records in dataset

[Edit this section](Deletion_of_hidden_records_in_dataset_/edit.md)

## Step 1: Preparation

Database: datasets  
Dataset: 43253  
Schema: dataset_43253  
Task: <https://taskman.eionet.europa.eu/issues/153422>  
Issue: The id_table field was null in the table record_value (null referrer)

[Edit this section](Deletion_of_hidden_records_in_dataset_/edit.md)

## Step 2: Execute sequence

Locate validations for the fields of the records you want to delete
[code] 
    select * from dataset_43253.field_validation fv2 where fv2.id_field in (
    select id from dataset_43253.field_value fv where fv.id_record in (
    select id from dataset_43253.record_value rv where rv.id_table is null )
    )
    
[/code]

if any, delete them
[code] 
    delete from dataset_43253.field_validation fv2 where fv2.id_field in (
    select id from dataset_43253.field_value fv where fv.id_record in (
    select id from dataset_43253.record_value rv where rv.id_table is null )
    )
    
[/code]

Locate field values for the records you want to delete
[code] 
    select * from  dataset_43253.field_value fv where fv.id_record in (
    select id from dataset_43253.record_value rv where rv.id_table is null )
    
[/code]

If any delete them
[code] 
    delete from  dataset_43253.field_value fv where fv.id_record in (
    select id from dataset_43253.record_value rv where rv.id_table is null )
    
[/code]

Locate record_values for the records you want to delete
[code] 
    select * from dataset_43253.record_value rv where rv.id_table is null
    
[/code]

Delete them
[code] 
    delete from dataset_43253.record_value rv where rv.id_table is null
    
[/code]

## Verification notes

All table names used in this runbook are correct. `field_validation`, `field_value`, and `record_value` are all valid tables within a per-dataset schema, as confirmed by `dataset.md` (which lists `FIELD_VALIDATION`, `FIELD_VALUE`, and `RECORD_VALUE` in the per-dataset PostgreSQL data model). The column `id_table` on `record_value` corresponds to the `TABLE_VALUE` foreign key (`ID_TABLE_SCHEMA` in the domain model describes the schema reference, while the FK to the physical `TABLE_VALUE` row is tracked separately); the presence of `null` in that column is the orphaned-record condition the runbook is addressing.

The deletion order — field validations first, then field values, then record values — correctly respects FK constraints. No table names require correction.
