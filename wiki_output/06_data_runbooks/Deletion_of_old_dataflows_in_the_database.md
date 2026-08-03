---
title: "Deletion of old dataflows in the database"
---

# Deletion of old dataflows in the database

[Edit this section](Deletion_of_old_dataflows_in_the_database/edit.md)

## Step 1: Preparation

Go to database **metabase** table dataset and get datasetSchema by dataflowId. This will be used in mongoDb Step 5.  
Query is:  

[code]
    select distinct dataset_schema from dataset where dataflowid = dataflowIdToBeDeleted;
    
[/code]

Replace dataflowIdToBeDeleted with the id of the dataflow.

[Edit this section](Deletion_of_old_dataflows_in_the_database/edit.md)

## Step 2: Retrieve Dataflow schemas to be deleted

Run the following query in database **metabase** and replace dataflowIdToBeDeleted with the id of the dataflow.
[code] 
    select ds.id as dataset_id,coalesce((select 'Dataset-'||ds.id from reporting_dataset rds where rds.id=ds.id),
    (select 'Dataschema-'||ds.id from design_dataset rds where rds.id=ds.id),
    (select 'EUDataset-'||ds.id from eu_dataset rds where rds.id=ds.id),
    (select 'TestDataset-'||ds.id from test_dataset rds where rds.id=ds.id),
    (select 'DataCollection-'||ds.id from data_collection rds where rds.id=ds.id),
    (select 'ReferenceDataset-'||ds.id from reference_dataset rds where rds.id=ds.id),'fail' )as dataset_group_prefix 
    from dataset ds where ds.dataflowid in (dataflowIdToBeDeleted);
    
[/code]
[code] 
    dataset_group_prefix is the dataset name so in the database dataset there will be a dataset with this name
    
[/code]

This query will return a list of datasets, data collections etc we will need to delete.  
e.g.

dataset_id | dataset_group_prefix  
---|---  
1  |  Dataschema-1   
2  |  Dataschema-2   
  
[Edit this section](Deletion_of_old_dataflows_in_the_database/edit.md)

## Step 3: Delete permissions from keycloak

Copy the results of Step 2 to the Delete Dataflows.ods file we use to construct the queries.

This will create the following queries to delete permissions in keycloak schema:

NOTE: add a dash at the end so you do not delete other schemas/dataflows, like this: '%Dataschema-1-%'.  

[code]
    delete from keycloak_group where id in ( select id from keycloak_group where name like '%Dataschema-1-%');
    delete from keycloak_group where id in ( select id from keycloak_group where name like '%Dataschema-2-%');
    
[/code]

These queries will be ran in the **keycloak** database.

[Edit this section](Deletion_of_old_dataflows_in_the_database/edit.md)

## Step 4: Delete data regarding the specific dataflow in database metabase

Execute the following queries in database **metabase** replacing the dataflowIdToBeDeleted with the id of the dataflow we want to delete:
[code] 
    delete from "snapshot" where reporting_dataset_id in (select id from dataset where dataflowid in (dataflowIdToBeDeleted));
    delete from snapshot_schema where design_dataset_id in (select id from dataset where dataflowid in (dataflowIdToBeDeleted));
    delete from eu_dataset where id in (select id from dataset where dataflowid in (dataflowIdToBeDeleted));
    delete from data_collection where id in (select id from dataset where dataflowid in (dataflowIdToBeDeleted));
    delete from reporting_dataset where id in (select id from dataset where dataflowid in (dataflowIdToBeDeleted));
    delete from partition_dataset where id in (select id from dataset where dataflowid in (dataflowIdToBeDeleted));
    delete from test_dataset where id in (select id from dataset where dataflowid in (dataflowIdToBeDeleted));
    delete from design_dataset where id in (select id from dataset where dataflowid in (dataflowIdToBeDeleted));
    delete from reference_dataset where id in (select id from dataset where dataflowid in (dataflowIdToBeDeleted));
    delete from "statistics" where id_dataset in (select id from dataset where dataflowid in (dataflowIdToBeDeleted));
    delete from weblink where dataflow_id in (dataflowIdToBeDeleted);
    delete from "document" where dataflow_id in (dataflowIdToBeDeleted);
    delete from integration_operation_parameters where integration_id in (select id from integration where dataflow_id in (dataflowIdToBeDeleted));
    delete from integration where dataflow_id in (dataflowIdToBeDeleted) ;
    delete from representative where dataflow_id in (dataflowIdToBeDeleted);
    delete from foreign_relations where dataset_id_origin in (select id from dataset where dataflowid in (dataflowIdToBeDeleted));
    delete from foreign_relations where dataset_id_destination in (select id from dataset where dataflowid in (dataflowIdToBeDeleted));
    delete from dataset where dataflowid in (dataflowIdToBeDeleted);
    delete from dataflow where id in (dataflowIdToBeDeleted);
    
[/code]

**After steps 1, 2, 3 and 4 the dataflow is not accessible through the ui so the user can continue his/her work.**

[Edit this section](Deletion_of_old_dataflows_in_the_database/edit.md)

## Step 5: Delete dataflow from mongodb

To delete the schema information from mongoDb we will use the ids we retrieved from Step 1.  
For each id, go to RulesSchema and search with {idDatasetSchema: ObjectId('retrieved_id')}. Delete the entry.  
Then for each id, go to DataSetSchema and search with {_id:ObjectId('retrieved_id')}. Delete the entry.

[Edit this section](Deletion_of_old_dataflows_in_the_database/edit.md)

## Step 6: Delete datasets [Outside of working hours]

**This step needs to be done outside of working hours and queries should run one by one.**

Get the drop schema queries that were constructed from the ods doc in Step 3.

e.g.  

[code]
    drop schema if exists dataset_1 CASCADE;
    drop schema if exists dataset_2 CASCADE;
    
[/code]

If the database is in recovery mode wait for about 15 minutes.

## Verification notes

**Table names — verified correct.** All table names used in Step 4 (`snapshot`, `snapshot_schema`, `eu_dataset`, `data_collection`, `reporting_dataset`, `partition_dataset`, `test_dataset`, `design_dataset`, `reference_dataset`, `statistics`, `weblink`, `document`, `integration_operation_parameters`, `integration`, `representative`, `dataset`, `dataflow`) are confirmed in the migration files (`V1__Init_Metabase_BD.sql` through V85). The `foreign_relations` table (referenced in the delete for `dataset_id_origin` and `dataset_id_destination`) is defined in `V6__Foreing_Relations.sql` (note the typo in the migration filename) as `public.FOREIGN_RELATIONS`; the runbook uses lowercase, which is correct for PostgreSQL unquoted identifiers.

**Missing step — `representative_leadreporter`.** The `representative_leadreporter` table (created in `V32__modify_representative_tables.sql`) stores lead reporter email addresses with a foreign key to `representative`. The runbook deletes from `representative` in Step 4 but does not first delete from `representative_leadreporter`. Unless the FK has `ON DELETE CASCADE` (no cascade is defined in the migration), the delete from `representative` will fail with a foreign key constraint violation. A delete step should be added before the `representative` delete:

```sql
delete from representative_leadreporter where representative_id in (
    select id from representative where dataflow_id in (dataflowIdToBeDeleted)
);
```

**Missing step — `contributor`.** The `contributor` table has a FK to `dataflow`. If contributors exist for the dataflow, the `delete from dataflow` at the end of Step 4 will fail unless contributors are deleted first. Add before the `dataflow` delete:

```sql
delete from contributor where dataflow_id in (dataflowIdToBeDeleted);
```

**Keycloak table.** The `keycloak_group` table in Step 3 is a table in the Keycloak database, not in the Metabase. This is correct but should be verified against the current Keycloak schema version in use, as Keycloak table structures vary between versions.

**orchestrator_db / process table.** The `process` table in the Metabase (created in `V65__create_table_process.sql`) also references datasets via `dataset_id`. If process rows exist for the datasets being deleted, the `dataset` delete will fail unless those rows are cleaned up first. The runbook does not mention this table.
