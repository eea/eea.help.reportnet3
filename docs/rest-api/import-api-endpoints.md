---
title: "Import API endpoints"
source_url: https://help.reportnet.europa.eu/import-api-endpoints/
---

# Import API endpoints
In order to import data in a reference dataset, the user can use the following endpoints:

  * **/importFileData** – available for CITUS and Big Data dataflows
  * **/etlImport** – available only for CITUS dataflows

**Using the`importFileData` endpoint**
```
curl --location --request POST 'https://api.reportnet.europa.eu/dataset/v2/importFileData/{datasetId}?dataflowId={dataflowId}' --header 'Authorization: ApiKey {apiKey}' --form 'file={importFile}'
```

**File parameter:** The file should be either a csv file or a zip with csv included files. If the user wants to use other formats like gkpg, xml etc. an integrationId must be provided (which is the specific declared transformation inside a dataset) for Reportnet3 to send a request to FME to convert the file to a zip with csv inside.

**Size limitations for file:**

  * If the spatial data field size exceeds 70MB, the field value will not be stored and left empty. In the Reportnet3 UI, a warning will be shown to the user.
  * For Big Data dataflows, the file size should be no bigger than 10GB.
  * For Citus dataflows, the file size should be up to 2GB.

The process to generate an api key is described here: [Rest API](index.md)

**Other optional parameters:**

  * `providerId` _:_
This parameter must be used when a REPORTER is updating a REPORTING dataset.
  * `tableSchemaId`:
If provided, the file will be imported on the specified table.
  * `replace`:
By default, the value of the parameter is set to `false`, causing the imported data to be appended to the existing data.
If the value is set to `TRUE`, then if a tableSchemaId is provided, only the data for this table are removed. **Otherwise, all data from all tables are removed**
  * `integrationId`:
If provided, the job will be submitted to FME and FME will callback reportnet3
  * `delimiter`:
delimiter: by default is the symbol **|**
If the user is using the Reportnet3 UI to add jobs without FME, then frontend sets the delimiter to comma **,**
  * fmeJobId: will be provided only by the FME

**Response:**

The response of the call is a json object with the jobId and an endpoint to poll for status.The same API KEY can be used for the polling. Below you can find an example:
```
{"jobId":23385,"pollingUrl":"/orchestrator/jobs/pollForJobStatus/23385?datasetId=35432&dataflowId=11720"}
```

**Read only and fixed number of records attributes:**

If the dataset is in DESIGN state, then attributes like read only fields, read only tables or fixed number of records tables do not affect the import process. The data will be appended or replace the old ones (based on the replace parameter value). Once the data collection has been created, then those attributes are applied.
So if for example a table is read only, the user will not be able to modify its data.
If a field is read only, no values can be modified for this field.
If a table is fixed number of records, no records can be removed or added.

**Using the`etlImport` endpoint**

The `etlImport` endpoint is only operational for **Citus** dataflows (not Big Data).

The request for etlImport is:
```
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
```

EtlImport does not accept a file, but a payload in the post request with the data. The limitation or the payload is 220MB

The response will be a json object containing the job id and polling Url in order for the user to poll for the job status
```
{
        "jobId": {jobId},
        "pollingUrl": "/orchestrator/jobs/pollForJobStatus/{jobId}?datasetId={datasetId}&dataflowId={dataflowId}"
    }
```

**Reference dataset:**

Before importing data into a reference dataset, the user must unlock it first. After the import is completed, the user must lock the reference dataset again. The endpoint to lock/unlock the reference dataset is the same and the only difference is the value of the **updatable** parameter. **If updatable is true, the reference dataset is unlocked. If updatable is false, the reference dataset is locked.** Once the reference dataset is locked, its public files are recreated based on the new data.
```
curl --location --request PUT 'https://api.reportnet.europa.eu/referenceDataset/{datasetId}?updatable={true/false}&dataflowId={dataflowId}' --header 'Authorization: ApiKey {apiKey}'
```

**Poll for job status:**

The process to poll for the status is described here: [Poll for job status](poll-for-job-status.md)
