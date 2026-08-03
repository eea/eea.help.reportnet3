---
title: "Validation api endpoints"
---

# Validation api endpoints

A custodian or a reporter can add validation jobs, poll for their statuses and retrieve the validation results using the endpoints that are described below.

[Edit this section](Validation_api_endpoints/edit.md)

## Add validation job
[code] 
    curl --location --request PUT 'https://api.reportnet.europa.eu/orchestrator/jobs/addValidationJob/{datasetId}?dataflowId={dataflowId}&providerId={providerId}' --header 'Authorization: ApiKey {apiKey}'
    
[/code]

The providerId parameter is required for reporters only, in order to authenticate the user's api key with the dataflowId and providerId.

The response of the request is the jobId.

[Edit this section](Validation_api_endpoints/edit.md)

## Poll for status
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

where jobStatus can have the following values: QUEUED, IN_PROGRESS, REFUSED, CANCELED, FAILED, FINISHED, CANCELED_BY_ADMIN

[Edit this section](Validation_api_endpoints/edit.md)

## Retrieve validation results
[code] 
    curl --location --request GET 'https://api.reportnet.europa.eu/validation/listGroupValidationsDL/{datasetId}?dataflowId={dataflowId}&providerId={providerId}' --header 'Authorization: ApiKey {apiKey}' (bigData)
    
    curl --location --request GET 'https://api.reportnet.europa.eu/validation/listGroupValidations/{datasetId}?dataflowId={dataflowId}&providerId={providerId}' --header 'Authorization: ApiKey {apiKey}' (citus)
    
[/code]

The providerId parameter is required for reporters only, in order to authenticate the user's api key with the dataflowId and providerId.  
The response is a json object that contains the validation results.

## Verification notes

**Add validation job endpoint — correct.** `PUT /orchestrator/jobs/addValidationJob/{datasetId}` is confirmed at line 157 of `JobControllerImpl.java`. The response of the job ID is accurate.

**Poll for status endpoint — correct.** `GET /orchestrator/jobs/pollForJobStatus/{jobId}` is confirmed at line 760 of `JobControllerImpl.java`.

**Job status values — correct.** All seven values (`QUEUED`, `IN_PROGRESS`, `REFUSED`, `CANCELED`, `FAILED`, `FINISHED`, `CANCELED_BY_ADMIN`) correspond exactly to the values in `JobStatusEnum.java`.

**Retrieve validation results — endpoint paths are correct, but the routing context is wrong.** `GET /validation/listGroupValidations/{id}` and `GET /validation/listGroupValidationsDL/{id}` are confirmed in `ValidationControllerImpl.java`. However, both endpoints use path variable `{id}` internally, not `{datasetId}`. The query parameters `dataflowId` and `providerId` are not shown in the controller signatures — verification of whether they are passed as query params or resolved from context would require deeper inspection, but the base paths are accurate.

**Missing public trigger endpoint.** The wiki describes how to add a validation job via the orchestrator, but does not document the direct validation trigger `PUT /validation/dataset/{id}` on the Validation Service itself, which is what the orchestrator actually calls to start execution. This endpoint is the one used in the `Manual_validation.md` Gatling test and is the primary execution entry point in `ValidationControllerImpl.java` at line 148.
