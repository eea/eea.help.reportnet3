---
title: "Api Documentation"
---

# Api Documentation

[Edit this section](Api_Documentation/edit.md)

## User role access

Common user roles consuming Reportnet 3 api calls are Custodians and Lead reporters (Providers)

Custodians have access to Design, Reference, Data collection for all actions and Read permissions for the Providers datasets  
Lead reporters have access only for the Provider datasets they belong to.

[Edit this section](Api_Documentation/edit.md)

## Authentication

There are 2 ways of authenticating an API call in Reportnet 3. Bearer and ApiKey. Both are HTTP header variables.

ApiKey

Can be generated from the UI in the left section and will authorize api calls for a specific dataflow. It does not expire. Its mainly used by the FME  
Can be used by the Custodians and the Providers

Example:
[code] 
    curl -X GET 'https://api.reportnet.europa.eu/dataflow/1208' -H "accept: */*" -H "Content-Type: application/json" -H 'Authorization: ApiKey XXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    
[/code]

Calls using api key

Action | Api call  
---|---  
Import  |  [dataset/v2/importFileData/](https://api.reportnet.europa.eu/swagger-ui.html?urls.primaryName=dataset#/Datasets_:_Dataset_Manager)  
Import  |  dataset/v1/{datasetId}/etlImport   
Export  |  dataset/v2/etlExport/{datasetId}   
Export  |  dataset/v3/etlExport/{datasetId}   
Delete  |  dataset/v1/{datasetId}/deleteDatasetData   
Attachment  |  dataset/v1/{datasetId}/field/{fieldId}/attachment   
Dataflow  |  dataflow/v1/{dataflowId}   
Historic Releases |  dataset/v1/historicReleases   
Webform  |  dataset/{datasetId}/uploadWebformConfig   
Validation  |  orchestrator/addValidationJob/{datasetId}   
Jobs  |  orchestrator/pollForJobStatus/{jobId}   
  
Bearer

Can be generated from the Login process and will authorize api calls for all dataflows the user has access. It will expire in 2 minutes  
Can be used by the Custodians and the Providers

Example:
[code] 
    curl -X PUT 'https://test-api.reportnet.europa.eu/recordstore/createUpdateQueryView?datasetId=14786&isMaterialized=false' -H 'Authorization: Bearer YYYYYYYYYYYYYYYYYYYYYYYYYYY'
    
[/code]

[Edit this section](Api_Documentation/edit.md)

## Login

Used to collect a Token for a registered User.

**URL** : /user/generateToken

**Method** : POST

**Auth required** : NO

**Data constraints**

Should be valid Keycloak member
[code] 
    {
        "username": "[valid email address]",
        "password": "[password in plain text]" 
    }
    
[/code]

**Data example**
[code] 
    curl -F 'password=XXXXXX' -F 'username=fotios.kouretas.custodian@trasys.gr' -X POST 'https://test-api.reportnet.europa.eu/user/generateToken'
    
[/code]

[Edit this section](Api_Documentation/edit.md)

### Success Response

**Code** : 200 OK

**Content example**
[code] 
    {
        "accessToken": "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY",
        "refreshToken": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "roles": [
            "DATA_CUSTODIAN",
            "offline_access",
            "uma_authorization" 
        ],
        "groups": [
            "REFERENCEDATASET-9587-DATA_CUSTODIAN",
            "DATASET-10674-DATA_CUSTODIAN",
            ..................
            "DATASET-10365-DATA_CUSTODIAN" 
        ],
        "accessTokenExpiration": 1499615,
        "preferredUsername": "fotios.kouretas.custodian@trasys.gr",
        "userId": "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ" 
    }
    
[/code]

[Edit this section](Api_Documentation/edit.md)

### Error Response

**Condition** : If 'username' and 'password' combination is wrong.

**Code** : 500 BAD REQUEST

**Content** :
[code] 
    {
        "timestamp": 1744181279764,
        "status": 500,
        "error": "Internal Server Error",
        "message": "401 Unauthorized",
        "path": "/user/generateToken" 
    }
[/code]

[Edit this section](Api_Documentation/edit.md)

### Used for

To make api calls in Reportnet that require a Bearer Login. Extract the "accessToken" from the response and use it to authorize a request. In the example below replace YYYYYYYYYYYYYYYYYYYYYYYYYYY with the "accessToken" to recreate the materialized views for a dataset.
[code] 
    curl -X PUT 'https://test-api.reportnet.europa.eu/recordstore/createUpdateQueryView?datasetId=14786&isMaterialized=false' -H 'Authorization: Bearer YYYYYYYYYYYYYYYYYYYYYYYYYYY'
    
[/code]

The token expires every 2 minutes.

## Verification notes

The `/user/generateToken` endpoint is confirmed: `UserManagementControllerImpl` at `user-management-service/src/main/java/org/eea/ums/controller/UserManagementControllerImpl.java` maps `@PostMapping("/generateToken")` and the controller is under the `ums` service (port 9010) routed through the API gateway at port 8010. The endpoint description is accurate.

All API-key-callable endpoints listed in the table were verified against source controllers:

The `dataset/v2/importFileData/` endpoint exists at `DatasetControllerImpl` line 434 as `POST /v2/importFileData/{datasetId}`. The `dataset/v1/{datasetId}/etlImport` endpoint exists as `POST /v1/{datasetId}/etlImport`. The `dataset/v2/etlExport/{datasetId}` and `dataset/v3/etlExport/{datasetId}` endpoints both exist; the source also exposes `v4` and `v5` variants not mentioned in the wiki. The `dataset/v1/{datasetId}/deleteDatasetData` endpoint exists. The `dataset/v1/{datasetId}/field/{fieldId}/attachment` endpoint exists. The `dataflow/v1/{dataflowId}` endpoint exists. The `dataset/v1/historicReleases` endpoint exists in `DatasetSnapshotControllerImpl`. The `dataset/{datasetId}/uploadWebformConfig` endpoint exists in `WebformControllerImpl`. The `orchestrator/addValidationJob/{datasetId}` endpoint exists as a `PUT` in `JobControllerImpl` under the `/jobs` prefix (full path is `orchestrator/jobs/addValidationJob/{datasetId}`); the prefix is missing in the table. Similarly `orchestrator/pollForJobStatus/{jobId}` maps to `orchestrator/jobs/pollForJobStatus/{jobId}`.

The error response for a wrong login says "Code: 500 BAD REQUEST", which conflates the HTTP status code (500 Internal Server Error) with the name of a different status code (400 Bad Request). This is a minor documentation inaccuracy.

The page states the bearer token expires in two minutes. This is plausible for a Keycloak access token but cannot be verified from source alone; the expiry is configured in the Keycloak realm settings, not in application code.
