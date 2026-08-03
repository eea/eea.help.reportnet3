---
title: "Validation API endpoints"
source_url: https://help.reportnet.europa.eu/validation-api-endpoints/
---

# Validation API endpoints
A custodian or a reporter can add validation jobs, poll for their statuses and retrieve the validation results using the endpoints that are described below.

**Add Validation job**
```
curl --location --request PUT 'https://api.reportnet.europa.eu/orchestrator/jobs/addValidationJob/{datasetId}?dataflowId={dataflowId}&providerId={providerId}' --header 'Authorization: ApiKey {apiKey}'
```

The providerId parameter is required for reporters only, in order to authenticate the user’s api key with the dataflowId and providerId.

The response of the request is the jobId.

**Poll for status**
```
curl --location --request GET 'https://api.reportnet.europa.eu/orchestrator/jobs/pollForJobStatus/{jobId}?datasetId={datasetId}&dataflowId={dataflowId}&providerId={providerId}' --header 'Authorization: ApiKey {apiKey}'
```

The providerId parameter is required for reporters only, in order to authenticate the user’s api key with the dataflowId and providerId.

The response will be:
```
{
        "status": {jobStatus}
    }
```

where jobStatus can have the following values: QUEUED, IN_PROGRESS, REFUSED, CANCELED, FAILED, FINISHED, CANCELED_BY_ADMIN

The process to poll for the status is also described here: [Poll for job status](poll-for-job-status.md)

**Retrieve validation results**
```
curl --location --request GET 'https://api.reportnet.europa.eu/validation/listGroupValidationsDL/{datasetId}?dataflowId={dataflowId}&providerId={providerId}' --header 'Authorization: ApiKey {apiKey}' (bigData)

    curl --location --request GET 'https://api.reportnet.europa.eu/validation/listGroupValidations/{datasetId}?dataflowId={dataflowId}&providerId={providerId}' --header 'Authorization: ApiKey {apiKey}' (citus)
```

The providerId parameter is required for reporters only, in order to authenticate the user’s api key with the dataflowId and providerId.

The response is a json object that contains the validation results.
