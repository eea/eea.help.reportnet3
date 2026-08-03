---
title: "Delete provider data from dataflow"
---

# Delete provider data in dataflow from database

[Edit this section](Delete_provider_data_from_dataflow/edit.md)

## Step 1: Preparation

Go to database **metabase** table dataset and get the id using dataflowId(your_dataflowId) and data_provider_id(your_provider_id) as paremeters (where). This will be used in database "datasets" Step 3.  
Query is:  

[code]
    select * from dataset where dataflowid = your_dataflowId and data_provider_id = your_provider_id;
    
[/code]

Replace your_dataflowId with the id of the dataflow and your_provider_id with the id of the provider.

The resulst should be a list if ids (id column) of the datasets for deletetion. eg id_1, id_2, id_3  
Keep that list for Step 3

[Edit this section](Delete_provider_data_from_dataflow/edit.md)

## Step 2: Delete from database **metabase** table dataset

Query is:  

[code]
    delete from dataset where dataflowid = your_dataflowId and data_provider_id = your_provider_id;
    
[/code]

[Edit this section](Delete_provider_data_from_dataflow/edit.md)

## Step 3: Delete from database **metabase** table representative

It is possible to remove the email of the lead reporter from "Manage Lead Reporters" but not possible to remove the representing organization and country. Therefore, you have to delete it from the database

Query is:  

[code]
    delete from representative where dataflow_id = your_dataflowId and data_provider_id = your_provider_id;
    
[/code]

[Edit this section](Delete_provider_data_from_dataflow/edit.md)

## Step 4: Delete dataset schemas from database **datasets** [Outside of working hours]

In database "datasets" replace id_1 in dataset_id_1 with the id from Step 1.

Eg for id 111 the query will be :   

[code]
    drop schema if exists dataset_111 CASCADE;
    
[/code]

Final query is:  

[code]
    drop schema if exists dataset_id_1 CASCADE;
    drop schema if exists dataset_id_2 CASCADE;
    drop schema if exists dataset_id_3 CASCADE;
    
[/code]

## Verification notes

**Table names — verified correct.** The `dataset` and `representative` table names used in Steps 1–3 are confirmed in `V1__Init_Metabase_BD.sql`. The column names `dataflowid` and `data_provider_id` on `dataset`, and `dataflow_id` and `data_provider_id` on `representative`, are all confirmed correct (note the different casing convention: `dataset` uses `dataflowid` without underscore, while `representative` uses `dataflow_id` with underscore).

**Missing step — `representative_leadreporter`.** The `representative_leadreporter` table (created in `V32__modify_representative_tables.sql`) stores lead reporter email addresses linked to each representative row. There is no `ON DELETE CASCADE` defined on its FK to `representative`. Step 3 deletes from `representative` without first deleting the corresponding `representative_leadreporter` rows, which will cause a foreign key constraint violation. The following step should be added before Step 3:

```sql
delete from representative_leadreporter where representative_id in (
    select id from representative where dataflow_id = your_dataflowId and data_provider_id = your_provider_id
);
```

**Missing step — `snapshot`.** The `snapshot` table has a FK to `reporting_dataset` (via `REPORTING_DATASET_ID`). If any snapshots exist for the datasets being deleted, the `delete from dataset` in Step 2 will fail unless snapshots are deleted first. Add before Step 2:

```sql
delete from "snapshot" where reporting_dataset_id in (
    select id from dataset where dataflowid = your_dataflowId and data_provider_id = your_provider_id
);
```
