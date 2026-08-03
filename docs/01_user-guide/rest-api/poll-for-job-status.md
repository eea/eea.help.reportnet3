---
title: "Poll for job status"
source_url: https://help.reportnet.europa.eu/poll-for-job-status/
---

# Poll for job status
Several endpoints like import ([Import API endpoints](import-api-endpoints.md)) and validation ([Validation API endpoints](validation-api-endpoints.md)) provide in their response a url to poll for the job status.

To poll for the job status the request is:
```
curl --location --request GET 'https://api.reportnet.europa.eu/orchestrator/jobs/pollForJobStatus/{jobId}?datasetId={datasetId}&dataflowId={dataflowId}&providerId={providerId}' --header 'Authorization: ApiKey {apiKey}'
```

The providerId parameter is required for reporters only, in order to authenticate the user’s api key with the dataflowId and providerId.
If the user is not a provider, then the providerId should not be provideeed as a parameter

The response will be:
```
{
        "status": {jobStatus}
    }
```

where jobStatus can have the following values: **QUEUED, IN_PROGRESS, REFUSED, CANCELED, FAILED, FINISHED, CANCELED_BY_ADMIN**
