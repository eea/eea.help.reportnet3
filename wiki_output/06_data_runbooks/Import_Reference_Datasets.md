---
title: "Import Reference Datasets"
---

# How to import reference datasets

  * **Table of contents**
  * How to import reference datasets
    * Step-by-step
    * Unlock the reference dataset
    * Import data into the reference dataset
    * Using the importFileData endpoint
      * Size limitations
    * Using the etlImport endpoint
      * Poll for job status



[Edit this section](Import_Reference_Datasets/edit.md)

## Step-by-step

Data custodians can use the following steps to update a reference dataset:

  * Unlock the reference dataset
  * Import data into the reference dataset 
    * Using the `/importFileData` endpoint
    * Using the `/etlImport` endpoint


  * ? QUESTION: Is there a step to validate the reference dataset ?  
**You can validate the dataset after unlocking it and by using the endpoints mentioned here:<https://taskman.eionet.europa.eu/projects/reportnet-3/wiki/Validation_api_endpoints>**
  * ? QUESTION: Is there a step to lock the reference dataset ?  
**To lock the dataset, you use the unlock endpoint but set the updatable parameter to false**



? QUESTION: When does the new reference dataset start being used in validation procedures ?  
**Then new reference data are used immediately once they are imported**  
? QUESTION: Which reference data is used for validation procedures while the reference dataset is being updated? ?  
**The new data**  
? QUESTION: What happens happens if an update fails? Is the previous data restored? ?  
**If you update and use replace data, the replace data option removed all data at the beginning. If the import fails after that, the dataset will be empty. You can use manage copies to create snapshots of your data.**  
? QUESTION: What happens if concurrent requests happen? E.g. the reference data is unlocked, and a new unlock request is received?  
Or if an update is ongoing, and another update request is received? ?  
**If a dataset is unlocked and the endpoint to unlock it again is called, nothing will happen. If you are using the /importFileData endpoint and another request is made for the same dataset, the second request will be refused.**

[Edit this section](Import_Reference_Datasets/edit.md)

## Unlock the reference dataset

Before importing data into a reference dataset, the user must unlock it using the following endpoint:
[code] 
    curl --location --request PUT 'https://api.reportnet.europa.eu/referenceDataset/{datasetId}?updatable={true}&dataflowId={dataflowId}' --header 'Authorization: ApiKey {apiKey}'
    
[/code]

[Edit this section](Import_Reference_Datasets/edit.md)

## Import data into the reference dataset

In order to import data in a reference dataset, the user can use the following endpoints:

  * `/importFileData` \- available for CITUS and DLH dataflows
  * `/etlImport` \- available only for CITUS dataflows



? QUESTION: Are there plans to have `/etlImport` working also in the DLH dataflows ?  
**No we are not implementing etlImport for big data dataflows<https://taskman.eionet.europa.eu/issues/287546>**

[Edit this section](Import_Reference_Datasets/edit.md)

## Using the `importFileData` endpoint

? QUESTION: What is the file format. Describe it first. ?  
**The file should be either a csv file or a zip with csv included files. If you want to use other formats like gkpg, xml etc. you need to provide an integrationId (which is the specific declared transformation inside a dataset) for Reportnet3 to send a request to FME to convert the file to a zip with csv inside.**
[code] 
    curl --location --request POST 'https://api.reportnet.europa.eu/dataset/v2/importFileData/{datasetId}?dataflowId={dataflowId}' --header 'Authorization: ApiKey {apiKey}' --form 'file={importFile}'
    
[/code]

Other optional parameters: 

  * `providerId` _< Note: not applicable to reference datasets>_   
This parameter must be used when a REPORTER is updating a reporting dataset.


  * `tableSchemaId`:   
If provided, the file will be imported on the specified table.


  * `replace`:   
By default, the value of the parameter is set to `false`, causing the imported data to be appended to the existing data.  
If the value is set to `TRUE`, the data from all tables of the dataset will be removed.  
? QUESTION: is the data of all tables is removed even if `tableSchemaId` is provided ?  
**If a tableSchemaId is provided, only the data for this table are removed. Otherwise, all data from all tables are removed**


  * `integrationId`:   
If provided, the job will be submitted to FME and FME will callback reportnet3


  * `delimiter`:   
delimiter: by default | when a job is added via the ui, the delimiter's value is ,  
? QUESTION: Clarify the phrase above. What is the default delimiter, if none is provided? What do you mean "when a job is added via the ui"? ?  
**The default delimiter is the symbol | If you are using the Reportnet3 UI to add jobs, then frontend sets the delimiter to comma ,**


  * `jobId` :   
the user does not need to provide this  
? QUESTION: Clarify the phrase above. Why is there a parameter that is not used?   
It is OK not to mention the parameter `jobId`, if it is never used in the context of the REFERENCE data update.  
But then the `providerId` parameter should also be remove from this "How to" document, because data providers should never be authorised to update the REFERENCE data. ?  
**This is used by the frontend service only. We can remove it if you want**


  * fmeJobId: will be provided only by fme



No response is provided to the user if called through an API call.  
? QUESTION: there is no response? even if it fails? Please clarify. ?  
**The method returns a void or throws exceptions. However we are currently implementing a solution where the endpoint returns a hashmap with the jobId and the url to poll for status.**

[Edit this section](Import_Reference_Datasets/edit.md)

### Size limitations

  * After the implementation of [#286941](/issues/286941 "Feature: Limit of field in Citus and DLH for geo spatial.   \(Closed\)") if the spatial data field size exceeds 70MB then a warning is thrown and the field will not be stored  
? QUESTION: Didn't you say above that there's no response? What does "a warning is thrown mean?" ?  
**This is only for when the import is done through the UI. If the endpoint is called directly no such warning will be visible**  
? QUESTION: What does "field size" mean? We had agreed on a limit of 70MB as the maximum size of any geometry in WKB format. ?  
**Exactly. If a geometry has a size of more than 70MB, the value will not be stored and will be left empty.**


  * The file size should be no bigger than 10 gb  
? QUESTION: I'm assuming you mean **10GB**? What is the file format? ?  
**The max file size is 10GB. The file should be either a csv file or a zip with csv included files. If you want to use other formats like gkpg, xml etc. you need to provide an integrationId (which is the specific declared transformation inside a dataset) for Reportnet3 to send a request to FME to convert the file to a zip with csv inside.**



[Edit this section](Import_Reference_Datasets/edit.md)

## Using the `etlImport` endpoint

The `etlImport` endpoint is only operational for citus dataflows.

? QUESTION: Are there other limitations? File format? File size? ?  
**EtlImport does not accept a file, but a payload in the post request with the data. The limitation or the payload is 220MB<https://taskman.eionet.europa.eu/issues/256387>**
[code] 
    curl --location --request POST 'https://api.reportnet.europa.eu/dataset/v1/{datasetId}/etlImport?dataflowId={dataflowId}&replaceData={true or false}' \
    --header 'Authorization: ApiKey {apiKey}' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "tables": [
            {
                "records": [
                    {
                        "countryCode": "XX",
                        "fields": [
                            {"fieldName": "{fieldName}", "value": {value}},
                            ...
                        ]
                    }
                ],
                "tableName":"{tableName}" 
            }
        ]
    }'
      
    
[/code]

The response will be a json object containing the job id and polling Url in order for the user to poll for the job status  

[code]
    {
        "jobId": {jobId},
        "pollingUrl": "/orchestrator/jobs/pollForJobStatus/{jobId}?datasetId={datasetId}&dataflowId={dataflowId}" 
    }
    
[/code]

[Edit this section](Import_Reference_Datasets/edit.md)

### Poll for job status
[code] 
    curl --location --request GET 'https://api.reportnet.europa.eu/orchestrator/jobs/pollForJobStatus/{jobId}?datasetId={datasetId}&dataflowId={dataflowId}&providerId={providerId}' --header 'Authorization: ApiKey {apiKey}'
    
[/code]

The providerId parameter is required for reporters only, in order to authenticate the user's api key with the dataflowId and providerId.  
The response will be:  

[code]
    {
        "status": {jobStatus}
    }
    
[/code]

? QUESTION ? What are the possible values for {jobStatus}? (e.g., PENDING, IN_PROGRESS, COMPLETED, FAILED). ?  
**Possible statuses are QUEUED, IN_PROGRESS, REFUSED, CANCELED, FAILED, FINISHED and CANCELED_BY_ADMIN**

## Verification notes

**Unlock endpoint — verified.** The `PUT /referenceDataset/{datasetId}?updatable=true` endpoint is confirmed in `ReferenceDatasetControllerImpl` (`@RequestMapping("/referenceDataset")`, `@PutMapping("/{datasetId}")`). The `updatable` parameter name matches the controller signature. Correct.

**`importFileData` endpoint — verified.** The endpoint `POST /dataset/v2/importFileData/{datasetId}` is confirmed in `DatasetControllerImpl` at line 434. The parameters `dataflowId`, `tableSchemaId`, `replace`, `integrationId`, `delimiter`, and `jobId` are all present in the controller. Correct.

**`etlImport` endpoint — verified.** The endpoint `POST /dataset/v1/{datasetId}/etlImport` is confirmed in `DatasetControllerImpl` at line 2215. The JSON payload structure and the polling URL pattern (`/orchestrator/jobs/pollForJobStatus/{jobId}`) are confirmed correct. The orchestrator endpoint is `GET /jobs/pollForJobStatus/{jobId}` in `JobControllerImpl`.

**Size limits — verified.** The 220 MB ETL import limit and 10 GB file size limit are referenced in `dataset.md` and are consistent with the source-derived documentation.

**`etlImport` not available for big-data dataflows — verified.** The `etlImportDatasetDL` endpoint (`POST /{datasetId}/etlImportDL`) exists but is separate from the standard `etlImport`. The runbook's note that `/etlImport` is available only for CITUS (standard) dataflows is consistent with the codebase.

**Draft content.** This document retains several unanswered questions (`? QUESTION:`) and embedded editorial notes. These are draft artefacts that should be resolved before the document is published as finished documentation.
