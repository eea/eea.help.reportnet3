---
title: "Release manually"
updated: "2022-11-15 10:59"
updated_by: "KOURETAS Fotios"
---

# Release-Validate manually

[Edit this section](Release_manually_/edit.md)

## For datasets with blocked releases to data collection:

\- Check for locks in the lock table of the metabase for the provider/dataset/dataflow  
<https://taskman.eionet.europa.eu/projects/reportnet-3/wiki/Get_lock_record_information>

\- Check if dataset table in metabase has releasing boolean to false (if not change to false)

[Edit this section](Release_manually_/edit.md)

## Manual release

\- Call the api for generating token for admin user. The token will be used in subsequent calls  
POST [https://api.reportnet.europa.eu/user/generateToken?username=adminUser&password=adminPassword](https://api.reportnet.europa.eu/user/generateToken?username=adminUser&password=adminPassword)

**Old way of manual validation/release (without jobs):**

\- Perfom first the validation for every dataset of the provider  
PUT <https://api.reportnet.europa.eu/validation/dataset/{datasetId>} with Bearer token

\- When all validations are over, run the release without the validation  
POST <https://api.reportnet.europa.eu/snapshot/dataflow/{dataflowId}/dataProvider/{dataProviderId}/release?validate=false> with Bearer token

**New way of manual validation/release (with jobs):**

\- Perfom first the validation for every dataset of the provider  
PUT <https://api.reportnet.europa.eu/orchestrator/jobs/addValidationJob/{datasetId>} with Bearer token

\- When all validations are over, run the release without the validation  
POST <https://api.reportnet.europa.eu/orchestrator/jobs/addRelease/dataflow/{dataflowId}/dataProvider/{dataProviderId>} with Bearer token  
You can add the following parameters: 

  * validate: default is true (this will add a validation job first)
  * restrictFromPublic: default false (if set to true the data of the provider will be private)
  * silentRelease: default false (if true, no notifications will be sent to the users. Also the date of the historic releases will not be modified)



For silentRelease , date should be null and DC released should be null and you should see in the logs of dataset 'Releasing datasets process ends. DataflowId: x DataProviderId: x DatasetId: x, JobId: x '.  
RELEASE_PROVIDER_COMPLETED_EVENT is not sent for silent releases.

[Edit this section](Release_manually_/edit.md)

## Monitor process

\- If the release is successful it will appear in logs :   
[https://logs.eea.europa.eu/search?q=RELEASE_PROVIDER_COMPLETED_EVENT&rangetype=relative&streams=5f4cf19377af2f0012fe8548&relative=172800](https://logs.eea.europa.eu/search?q=RELEASE_PROVIDER_COMPLETED_EVENT&rangetype=relative&streams=5f4cf19377af2f0012fe8548&relative=172800)

\- if the release is ongoing you should see logs like :   
[https://logs.eea.europa.eu/search?q=Releasing&rangetype=relative&streams=5f4cf19377af2f0012fe8548&relative=172800](https://logs.eea.europa.eu/search?q=Releasing&rangetype=relative&streams=5f4cf19377af2f0012fe8548&relative=172800)

Example :

Releasing datasets process begins. DataflowId: 615 DataProviderId: 68  
...  
Releasing datasets process ends. DataflowId: 615 DataProviderId: 68

[Edit this section](Release_manually_/edit.md)

## Connection error during provider deletion from dataCollection

If the process fails while deleting provider code from dataCollection, the deletion of provider in the dataCollection should be done manually

e.g. delete from dataset_127.record_value where data_provider_code ='BG';

where dataset_127 should be replaced with dataCollectionId  
and data_provider_code ='BG' should be replaced with data provider code that should be deleted. If we know the dataProviderId, we can find the dataProviderCode from metabase table data_provider.

By running this query, the data from related tables are also deleted. After the deletion, we should remove locks and start release process again.

[Edit this section](Release_manually_/edit.md)

## Database monitor process (* this MUST be executed *)

We monitor 33706 postgres processes in the dataset database (Copy in) and these need to finalize before the next provider release.   
When not the delete query create locks.   

[code]
    SELECT pid,  age(clock_timestamp(), query_start),  usename,  application_name,  query
    FROM  pg_stat_activity 
    WHERE state != 'idle'  AND  query NOT ILIKE '%pg_stat_activity%' ORDER BY query_start DESC;
    
[/code]

[Edit this section](Release_manually_/edit.md)

## Recovery process  
(Example for dataset id dataset release to data collection)  
In case the process is blocked/stopped/failed the recovery flow is:

1) Identify the snapshot id of the release either from the snapshot table of the metabase :

![](Release_manually_/attachments/clipboard-202211151059-ah96n.png)

or from the graylog :

![](Release_manually_/attachments/clipboard-202211151100-vxwf2.png)

2) Open a shell in a recordstore pod in rancher/kubernetes and check the snapshot files to see if the restore snapshot process is blocked:

![](Release_manually_/attachments/clipboard-202211151104-slrcx.png)

This release process has been completed without error

3) If there is an error like the snapshot id 51497

![](Release_manually_/attachments/clipboard-202211151111-ceuqh.png)

There will be files in the form of snapshot_{datasetid}_{split}_table_FieldValue.snap  
The process has stopped in file snapshot_51497_6_table_FieldValue.snap

SnapshotId = 51497

Get the dataset and the data collection ids by query in the snapshot table in the metabase

![](Release_manually_/attachments/clipboard-202211151115-fihsc.png)

Data collectionId : 37706  
Dataset id : 37930

Check if the last and the first record of the file is in the database:

Get the id  
![](Release_manually_/attachments/clipboard-202211151118-ite0t.png)

Search for the record in in the datacollection record_value table  
![](Release_manually_/attachments/clipboard-202211151128-seehk.png)

**last record doesn not exist**

![](Release_manually_/attachments/clipboard-202211151609-joe3q.png)

first record does not exists

![](Release_manually_/attachments/clipboard-202211151610-rv8ov.png)

Therefore the file snapshot_51497_6_table_FieldValue.snap has not been imported in the data-collection dataset.   
The recovery process should start from file 6 to file 60 and the commands are :

get the token

curl -F 'password=xxxxxx' -F 'username=xxxxxxxx' -X POST 'https://api.reportnet.europa.eu/user/generateToken'

start recovery

curl -F 'datasetId=37706' -F 'idSnapshot=51497' -F 'startingNumber=6' -F 'endingNumber=60' -F 'type=FIELD' -X POST 'https://api.reportnet.europa.eu/recordstore/restoreSpecificFileSnapshotData' -H 'Authorization: Bearer 79e4f4dc-9a3a-40ac-87cb-765fafc814ee'

**Important note:** If records for file snapshot_51497_6_table_FieldValue.snap existed in dataCollection dataset, then we would delete the file snapshot_51497_6_table_FieldValue.snap and start the recovery from  
file 7.

## Verification notes

This document was last updated in November 2022. The API endpoints it references should be compared against the current source.

The "Old way" endpoint `PUT https://api.reportnet.europa.eu/validation/dataset/{datasetId}` and the old release endpoint `POST https://api.reportnet.europa.eu/snapshot/dataflow/{dataflowId}/dataProvider/{dataProviderId}/release` are described as pre-jobs-system. These paths are not confirmed to still exist; the current orchestrator-based paths should be used instead.

The "New way" endpoints are confirmed against source. `PUT /orchestrator/jobs/addValidationJob/{datasetId}` is implemented at `JobControllerImpl.java` line 157. `POST /orchestrator/jobs/addRelease/dataflow/{dataflowId}/dataProvider/{dataProviderId}/release` is implemented at line 236 of the same file. The parameters `validate`, `restrictFromPublic`, and `silentRelease` are all confirmed as actual parameters in that endpoint (lines 245–247).

The `silentRelease` behaviour described (null date, no `RELEASE_PROVIDER_COMPLETED_EVENT`) is consistent with the `isSilentRelease` check at `JobControllerImpl.java` line 1027 and the logic in `CheckBlockersDataSnapshotCommand.java`.

The recovery endpoint `POST https://api.reportnet.europa.eu/recordstore/restoreSpecificFileSnapshotData` with parameters `datasetId`, `idSnapshot`, `startingNumber`, `endingNumber`, and `type=FIELD` cannot be directly confirmed without reading the recordstore controller, but the `.snap` file naming pattern (`snapshot_{datasetId}_{split}_table_FieldValue.snap`) is consistent with the file-based snapshot mechanism confirmed in `JdbcRecordStoreServiceImpl.java`. The example `dataCollectionId` value `33706` appears in the monitoring section but then differs from `37706` used elsewhere in the same document — this is likely a typo at the header of the "Database monitor process" section.
