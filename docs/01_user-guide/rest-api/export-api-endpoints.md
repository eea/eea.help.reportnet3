---
title: "Export API Endpoints"
source_url: https://help.reportnet.europa.eu/export-api-endpoints/
---

# Export API Endpoints
# **ETL Export Versions**

Version| Path| Format| Type| Description| Platform| Status
---|---|---|---|---|---|---
`/v1`| `/v1/{datasetId}/etlExport`| JSON| Synchronous| Streams dataset content directly. Not suitable for large datasets.| Big Data/Citus|
`/v2`| `/v2/etlExport/{datasetId}`| JSON| Synchronous| Internal improvement of v1.| Big Data/Citus| Replaced by v3
`/v3`| `/v3/etlExport/{datasetId}`| JSON| Asynchronous| Introduced job-based export.| Big Data/Citus|
`/v4`| `/v4/etlExport/{datasetId}`| ZIP (CSV)| Asynchronous| Exports an entire dataset asynchronously as a ZIP archive containing one CSV file per table.
Supports large datasets and includes an option to export attachments.| Big Data| Recommended **– DLT2 harvesting**
`/v5`| `/v5/etlExport/{datasetId}`| ZIP (Parquet)| Asynchronous| Exports dataset in Parquet format.Analytics-focused.| Big Data| Optional

## **Example**
```
GET /v4/etlExport/{datasetId}
```

### **Parameters**

Name| Type| Required| Description
---|---|---|---
`datasetId`| Long| Yes| ID of the dataset to export.
`dataflowId`| Long| Yes| ID of the associated dataflow.
`providerId`| Long| Optional| ID of the data provider.
`tableSchemaId`| String| Optional| Restrict export to a specific table schema.
`includeAttachments`| Boolean| Optional| Include attachments in the exported ZIP (default: false).

### **Response**
```
{
      "pollingUrl": "/orchestrator/jobs/pollForJobStatus/{jobId}?datasetId={datasetId}&dataflowId={dataflowId}",
      "status": "Preparing file"
    }
```

#### **Description**

  * When `mimeType=csv` or `zip(with csv files)`, the export streams data directly as a file download – recommended for large datasets.
  * When using `xlsx`, validation or formatting may be applied.

The export runs in the background.
Clients (like DLT2) should:

  1. Call the endpoint.
  2. Poll the `pollingUrl` until job status becomes `FINISHED`. For more info [Poll for job status](poll-for-job-status.md)
  3. Download the resulting ZIP from the orchestrator’s job results.

### **Output**

  * ZIP archive containing one CSV per dataset table.
  * Attachments (if requested) are included in separate folders.

## **Limitations and Notes**

  1. **Synchronous vs Asynchronous:**
     * `/v4` and `/v5` are asynchronous and suitable for automated harvesting.
     * `/v1` and `/`v2 are synchronous, best for on-demand downloads.
  2. **Authorization:**
     * Access depends on the user’s dataset role (`CUSTODIAN`, `STEWARD`, `OBSERVER`, etc.) or API key –header ‘Authorization: ApiKey xxxxx-xxxx-xxxxx’.
  3. **Performance:**
     * `/v1`–`/v3` may fail or time out on large datasets. Use `/v4` for all harvesting operations.
  4. **Attachments:**
     * Only `/v4` and `/v5` support attachment export.
  5. **Formats:**
     * `/v4` → CSV (archived in ZIP)
     * `/v5` → Parquet

### **Final Recommendation for DLT2**

Use:
```
GET /v4/etlExport/{datasetId}?dataflowId={dataflowId}
```

  * Handles all dataset sizes.
  * Asynchronous job-based process.
  * Returns ZIP with CSVs (attachments optional).
  * Backward compatible and actively supported.

# **Dataset – Available Export Endpoints Overview as used in Reportnet 3 UI**

Endpoint| Type| Format| Description| Recommended Use
---|---|---|---|---
/`{datasetId}/exportDatasetFile`?mimetype=| Asynchronous| CSV, XLSX, ZIP| Exports a dataset directly for download.| Manual or quick dataset export with Bearer Token
/`{datasetId}/exportDatasetFile`DL?mimetype=| Asynchronous| ZIP (CSV)| Exports a zip with Csv for each table| Manual or quick dataseTablet export with Bearer Token

## **Requests**

### **1.`GET **`{datasetId}`** /exportDatasetFile`**

Exports the **entire dataset** directly.
Used mainly for user-initiated downloads via the RN3 interface.

#### Example
```
GET /exportDatasetFile/1001?mimeType=csv
```

#### Parameters

Name| Type| Required| Description
---|---|---|---
`datasetId`| Long| Yes| Dataset identifier.
`mimeType`| String| Yes| Output format (`csv`, `xlsx`, `zip`, etc.).

### **2.** **`GET**`{datasetId}`** /exportDatasetFileDL`**

Exports the **entire dataset** directly (synchronous call).
Used mainly for user-initiated datalake downloads via the RN3 interface.

#### Description

  * `zip(with csv files)`, the export streams data directly as a file download – recommended for large datasets.

#### Example
```
GET /exportDatasetFileDL/1001?mimeType=zip+csv
```

#### Parameters

Name| Type| Required| Description
---|---|---|---
`datasetId`| Long| Yes| Dataset identifier.
`mimeType`| String| Yes| Output format ZIP of CSV only

# **Table – Available Export Endpoints Overview as used in Reportnet 3 UI**

Endpoint| Type| Format| Description| Recommended Use
---|---|---|---|---
/exportFile| Asynchronous| CSV, XLSX| Exports a single table from a dataset.| Table-level manual export with Bearer Token
`/exportFileDL`| Asynchronous| CSV| Exports a single table from a dataset.| Table-level manual export with Bearer Token

## **Requests**

### **1**. **`POST /exportFile`**

Exports data for a **single table** within a dataset.

#### **Parameters**

Name| Type| Required| Description
---|---|---|---
`datasetId`| Long| Yes| Dataset identifier.
`tableSchemaId`| String| Yes| Identifier of the specific table schema.
`mimeType`| String| Yes| Output format (`csv`, `xlsx`).
Request Body| `ExportFilterVO`| Optional| Filters for rows, columns, or specific conditions.

#### **Description**

  * Returns the selected table as a downloadable file in the requested format.
  * Useful for manual exports or debugging single tables.
  * The export can be filtered using the `ExportFilterVO` body.

#### **Example**
```
POST /exportFileDL?datasetId=1001&tableSchemaId=5cf0e9b3b793310e9ceca190&mimeType=csv
```

#### **Request Body – optional**
```
{
      "filterField": "country",
      "filterValue": "DK"
    }
```

### **2.`POST /exportFileDL`**

Exports data for a **single table** within a dataset.

#### **Parameters**

Name| Type| Required| Description
---|---|---|---
`datasetId`| Long| Yes| Dataset identifier.
`tableSchemaId`| String| Yes| Identifier of the specific table schema.
`mimeType`| String| Yes| Output format (`csv`, `xlsx`).
Request Body| `ExportFilterVO`| Optional| Filters for rows, columns, or specific conditions.

#### **Description**

  * Returns the selected table as a downloadable file in the requested format.
  * Useful for manual exports or debugging single tables.
  * The export can be filtered using the `ExportFilterVO` body.

#### **Example**
```
POST /exportFileDL?datasetId=1001&tableSchemaId=5cf0e9b3b793310e9ceca190&mimeType=csv
```

**Request body – optional:**
```
{
      "filterField": "country",
      "filterValue": "DK"
    }
```
