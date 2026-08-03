# REST API overview

Reportnet3 exposes its functionality through a collection of Spring Boot microservice REST endpoints, all unified behind a single API Gateway based on Netflix Zuul. Every inbound HTTP request from a browser, external system, or FME Server reaches the gateway first; the gateway validates the JWT token and then proxies the request to the appropriate microservice using Consul-based service discovery. The gateway does not aggregate or transform responses — it forwards them unchanged with the original path intact.

The endpoints fall into two categories. **Public endpoints** are reachable through the gateway and are the intended integration surface for the frontend and external API consumers. **Private endpoints** are paths that contain the segment `/private/` anywhere in the URL; the gateway is configured to ignore these patterns (`zuul.ignoredPatterns = /**/private/**`), so they are blocked at the gateway and can only be called by other microservices within the cluster via Feign clients. A handful of additional controllers — those belonging to the Orchestrator — are not routed through the gateway at all and are strictly internal.

The API does not follow a single overarching REST versioning strategy. Some endpoints have explicit version prefixes (`/v1/`, `/v2/`, `/v3/`) added as features evolved, while many others have no version prefix. Where versioned and unversioned variants of the same endpoint coexist, the versioned form is generally the newer behaviour.

---

## Authentication

Clients authenticate by obtaining a JWT from Keycloak, either via the standard OAuth2 code flow or through the token generation endpoints that the User Management Service exposes directly. All gateway-proxied requests must carry the token as a `Bearer` header. The gateway validates it before forwarding. API key authentication is also available for programmatic integrations: a reporter or dataflow custodian can generate an API key tied to a specific dataflow, then call `POST /user/authenticateByApiKey/{apiKey}` to exchange it for a short-lived JWT.

The three routes to a token:

| Method | Path | Use case |
|--------|------|----------|
| POST | `/user/generateToken` | Username and password (Keycloak direct grant) |
| POST | `/user/generateTokenByCode` | OAuth2 authorisation code |
| POST | `/user/authenticateByApiKey/{apiKey}` | API key issued per dataflow |
| POST | `/user/refreshToken` | Refresh an existing token |

---

## Gateway routing

The table below maps each URL prefix to the microservice that handles it. All routes have `stripPrefix = false`, meaning the prefix is kept when the gateway forwards the request.

| URL prefix | Microservice |
|-----------|-------------|
| `/dataflow/**` | Dataflow Service |
| `/contributor/**` | Dataflow Service |
| `/representative/**` | Dataflow Service |
| `/weblink/**` | Dataflow Service |
| `/integration/**` | Dataflow Service |
| `/fme/**` | Dataflow Service |
| `/dataset/**` | Dataset Service |
| `/datasetmetabase/**` | Dataset Service |
| `/dataschema/**` | Dataset Service |
| `/snapshot/**` | Dataset Service |
| `/datacollection/**` | Dataset Service |
| `/euDataset/**` | Dataset Service |
| `/referenceDataset/**` | Dataset Service |
| `/pam/**` | Dataset Service |
| `/webform/**` | Dataset Service |
| `/testDataset/**` | Dataset Service |
| `/validation/**` | Validation Service |
| `/rules/**` | Validation Service |
| `/recordstore/**` | Recordstore Service |
| `/process/**` | Recordstore Service |
| `/collaboration/**` | Collaboration Service |
| `/communication/**` | Communication Service |
| `/notification/**` | Communication Service |
| `/document/**` | Document Container Service |
| `/user/**` | User Management Service |
| `/resource/**` | User Management Service |
| `/obligation/**` | ROD Service |
| `/obligation_client/**` | ROD Service |
| `/obligation_country/**` | ROD Service |
| `/obligation_issue/**` | ROD Service |
| `/indexSearch/**` | Index Search Service |
| `/inspireHarvester/**` | Inspire Harvester |

Orchestrator endpoints (`/jobs/**`, `/jobHistory/**`, `/jobProcess/**`, `/redis/**`) are **not** registered in the gateway routing. They exist solely for service-to-service calls.

---

## Public API

This section describes the endpoints reachable through the gateway, excluding any path containing `/private/`. They are organised by the domain they operate on.

---

### User management (`/user`, `/resource`)

The User Management Service wraps Keycloak. It handles token issuance, user lookups, role assignments, and API key management. It does not store user profiles itself — Keycloak is the system of record. The `/resource` prefix exposes Keycloak resource group management used when dataflows and datasets are created or deleted.

**User operations**

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/user/generateToken` | Obtain a JWT via username and password |
| POST | `/user/generateTokenByCode` | Obtain a JWT via OAuth2 authorisation code |
| POST | `/user/refreshToken` | Refresh a JWT |
| POST | `/user/logout` | Invalidate a refresh token |
| POST | `/user/authenticateByApiKey/{apiKey}` | Exchange an API key for a JWT |
| POST | `/user/authenticateByEmail` | Authenticate by email (internal use) |
| GET | `/user/checkAccess` | Check whether the current user has a given scope on a resource |
| GET | `/user/resources` | List all resources the current user can access |
| GET | `/user/resources_by_type` | Filter resources by type |
| GET | `/user/resources_by_role` | Filter resources by security role |
| GET | `/user/resources_by_type_role` | Filter resources by type and role |
| PUT | `/user/add_user_to_resource` | Grant the current user access to a resource group |
| PUT | `/user/add_contributor_to_resource` | Grant a specific user access to a resource group |
| PUT | `/user/add_contributors_to_resources` | Bulk-grant access |
| PUT | `/user/add_user_to_resources` | Bulk-grant the current user access |
| PUT | `/user/updateAttributes` | Update Keycloak user attributes |
| GET | `/user/getAttributes` | Retrieve Keycloak user attributes |
| GET | `/user/getUserByEmail` | Look up a user by email address |
| GET | `/user/getUserByUserId` | Look up the current user's profile |
| GET | `/user/getUsersByGroup/{group}` | List all users in a Keycloak group |
| DELETE | `/user/remove_contributor_from_resource` | Revoke a user's access to a resource |
| DELETE | `/user/remove_contributors_from_resources` | Bulk-revoke access |
| DELETE | `/user/remove_user_from_resources` | Bulk-revoke the current user's access |
| POST | `/user/createUsers` | Bulk-create users via CSV file upload |
| POST | `/user/createApiKey` | Generate an API key for a dataflow |
| GET | `/user/getApiKey` | Retrieve an existing API key |
| GET | `/user/getUserRolesByDataflow/{dataflowId}/dataProviderId/{dataProviderId}` | List a user's roles for a specific dataflow and provider |
| GET | `/user/userRoles/dataflow/{dataflowId}` | List all user roles for a dataflow |
| POST | `/user/exportUsersByCountry/dataflow/{dataflowId}` | Trigger export of reporter list to file |
| GET | `/user/downloadUsersByCountry/{dataflowId}` | Download the exported reporter list |
| POST | `/user/nationalCoordinator` | Register a national coordinator |
| GET | `/user/nationalCoordinator` | List all national coordinators |
| GET | `/user/nationalCoordinator/{countryCode}` | List coordinators for a country (Consul-key guarded) |
| DELETE | `/user/nationalCoordinator` | Remove a national coordinator |

**Resource management**

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/resource/create` | Create a single Keycloak resource |
| POST | `/resource/createList` | Bulk-create resources |
| GET | `/resource/details` | Retrieve resource details by id and group |
| GET | `/resource/getResourceInfoVOByResource` | List all groups for a resource |
| DELETE | `/resource/delete` | Delete a list of resources |
| DELETE | `/resource/delete_by_name` | Delete resources by name |
| DELETE | `/resource/delete_by_dataset_id` | Delete all resources associated with a set of dataset ids |

---

### Dataflows (`/dataflow`)

A dataflow is the top-level container for a reporting exercise. It links an obligation from the ROD database to a schema, a set of reporters, and lifecycle rules. The Dataflow Service is the authority on dataflow metadata, status, and access configuration.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/dataflow/getDataflows` | Paginated list of reporting dataflows with filters |
| POST | `/dataflow/referenceDataflows` | Paginated list of reference dataflows |
| POST | `/dataflow/businessDataflows` | Paginated list of business dataflows |
| POST | `/dataflow/citizenDataflows` | Paginated list of citizen-science dataflows |
| POST | `/dataflow/getPublicDataflows` | Paginated public dataflow listing (no auth required) |
| POST | `/dataflow/getPublicDataflowsByObligation` | Paginated public listing grouped by obligation |
| GET | `/dataflow/getPublicDataflow/{dataflowId}` | Public summary of a single dataflow |
| GET | `/dataflow/getPrivateDataflow/{dataflowId}` | Internal detail view of a single dataflow |
| GET | `/dataflow/cloneableDataflows` | Dataflows the current user may clone |
| GET | `/dataflow/countByType` | Count of dataflows grouped by type |
| GET | `/dataflow/getUserRolesAllDataflows` | Current user's role across all dataflows |
| GET | `/dataflow/v1/{dataflowId}` | Retrieve a dataflow by id (v1) |
| GET | `/dataflow/{dataflowId}` | Retrieve a dataflow by id |
| GET | `/dataflow/v1/{dataflowId}/getmetabase` | Retrieve dataflow metabase information (v1) |
| GET | `/dataflow/{dataflowId}/getmetabase` | Retrieve dataflow metabase information |
| GET | `/dataflow/{dataflowId}/datasetsSummary` | Summary of all datasets in a dataflow |
| GET | `/dataflow/status/{status}` | List dataflows by status |
| GET | `/dataflow/completed` | Paginated list of completed dataflows |
| POST | `/dataflow/` | Create a new dataflow |
| PUT | `/dataflow/` | Update dataflow metadata |
| DELETE | `/dataflow/{dataflowId}` | Hard-delete a dataflow |
| PUT | `/dataflow/{dataflowId}/soft-delete` | Mark a dataflow as deleted without removing data |
| PUT | `/dataflow/{dataflowId}/reverse-soft-delete` | Undo a soft delete |
| PUT | `/dataflow/{dataflowId}/updateStatus` | Change the dataflow status and optional deadline |
| PUT | `/dataflow/{dataflowId}/updateAutomaticDelete` | Toggle automatic deletion setting |
| PUT | `/dataflow/updateDataProviderGroupIdById/{dataflowId}` | Change the data provider group assigned to a dataflow |
| PUT | `/dataflow/validateAllReporters` | Trigger validation of all reporter accounts |
| POST | `/dataflow/exportSchemaInformation/{dataflowId}` | Export dataflow schema information to file |
| GET | `/dataflow/downloadSchemaInformation/{dataflowId}` | Download previously exported schema information |
| GET | `/dataflow/downloadPublicSchemaInformation/{dataflowId}` | Download public schema information without auth |
| POST | `/dataflow/country/{countryCode}` | List dataflows accessible to a specific country |

---

### Contributors and representatives (`/contributor`, `/representative`)

Within a dataflow, reporters are represented by data providers. Contributors are the individual user accounts that have write access to a provider's reporting dataset. The Representative controller manages the data provider groups, provider records, and the lead reporters who formally submit data.

**Contributors**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/contributor/requester/dataflow/{dataflowId}` | List requester contributors for a dataflow |
| GET | `/contributor/reporter/dataflow/{dataflowId}/provider/{dataproviderId}` | List reporter contributors for a provider |
| PUT | `/contributor/requester/dataflow/{dataflowId}` | Add or update a requester contributor |
| PUT | `/contributor/reporter/dataflow/{dataflowId}/provider/{dataProviderId}` | Add or update a reporter contributor |
| PUT | `/contributor/validateReporters/dataflow/{dataflowId}/provider/{dataProviderId}` | Re-validate reporter access for a provider |
| DELETE | `/contributor/requester/dataflow/{dataflowId}` | Remove a requester contributor |
| DELETE | `/contributor/reporter/dataflow/{dataflowId}/provider/{dataProviderId}` | Remove a reporter contributor |

**Representatives and data providers**

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/representative/{dataflowId}` | Add a representative (data provider) to a dataflow |
| PUT | `/representative/update` | Update a representative |
| DELETE | `/representative/{dataflowRepresentativeId}/dataflow/{dataflowId}` | Remove a representative from a dataflow |
| DELETE | `/representative/dataflow/{dataflowId}` | Remove all representatives from a dataflow |
| GET | `/representative/v1/dataflow/{dataflowId}` | List representatives for a dataflow (v1) |
| GET | `/representative/dataflow/{dataflowId}` | List representatives for a dataflow |
| GET | `/representative/dataProvider` | Paginated list of data providers |
| GET | `/representative/dataProviderGroups` | List all data provider groups |
| GET | `/representative/dataProvider/{groupId}` | List providers in a group |
| GET | `/representative/dataProvider/id/{id}` | Retrieve a single data provider |
| GET | `/representative/dataProvider/countryGroups` | Country-level provider groups |
| GET | `/representative/dataProvider/companyGroups` | Company-level provider groups |
| GET | `/representative/dataProvider/organizationGroups` | Organisation-level provider groups |
| POST | `/representative/provider/create` | Create a new data provider |
| PUT | `/representative/provider/update` | Update a data provider |
| GET | `/representative/export/{dataflowId}` | Export the representative list to file |
| GET | `/representative/exportTemplateReportersFile/{groupId}` | Download import template for a provider group |
| POST | `/representative/import/{dataflowId}/group/{groupId}` | Import representatives from file |
| POST | `/representative/importAndReplace/{dataflowId}/group/{groupId}` | Import and replace existing representatives |
| PUT | `/representative/update/restrictFromPublic/dataflow/{dataflowId}/dataProvider/{dataProviderId}` | Toggle public visibility for a provider |
| POST | `/representative/{representativeId}/leadReporter/dataflow/{dataflowId}` | Add a lead reporter |
| PUT | `/representative/leadReporter/update/dataflow/{dataflowId}` | Update a lead reporter |
| DELETE | `/representative/leadReporter/{leadReporterId}/dataflow/{dataflowId}` | Remove a lead reporter |
| PUT | `/representative/validateLeadReporters/dataflow/{dataflowId}` | Validate lead reporter access |
| GET | `/representative/fmeUsers` | List FME user accounts available for integration |

---

### Web links and documents (`/weblink`, `/dataflowDocument`)

Dataflows may carry supporting materials: web links point to external URLs relevant to the reporting obligation, and documents are files uploaded directly into the platform. Both belong to a specific dataflow, and both can be marked as public to appear on the public-facing dataflow page.

Note: `/dataflowDocument/**` is not routed through the API Gateway — document metadata operations are internal. File upload and download for dataflow-level documents go through `/document/**`.

**Web links**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/weblink/v1/dataflow/{dataflowId}` | List web links for a dataflow (v1) |
| GET | `/weblink/dataflow/{dataflowId}` | List web links for a dataflow |
| POST | `/weblink/v1/dataflow/{dataflowId}` | Add a web link to a dataflow (v1) |
| POST | `/weblink/dataflow/{dataflowId}` | Add a web link to a dataflow |
| PUT | `/weblink/v1/dataflow/{dataflowId}` | Update a web link (v1) |
| PUT | `/weblink/dataflow/{dataflowId}` | Update a web link |
| DELETE | `/weblink/{idLink}/dataflow/{dataflowId}` | Remove a web link |

**Documents**

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/document/v1/upload/{dataflowId}` | Upload a file to a dataflow (v1) |
| POST | `/document/upload/{dataflowId}` | Upload a file to a dataflow |
| GET | `/document/v1/{documentId}/dataflow/{dataflowId}` | Download a document (v1) |
| GET | `/document/{documentId}/dataflow/{dataflowId}` | Download a document |
| PUT | `/document/v1/update/{idDocument}/dataflow/{dataflowId}` | Replace or update a document (v1) |
| PUT | `/document/update/{idDocument}/dataflow/{dataflowId}` | Replace or update a document |
| DELETE | `/document/v1/{documentId}/dataflow/{dataflowId}` | Delete a document (v1) |
| DELETE | `/document/{documentId}/dataflow/{dataflowId}` | Delete a document |
| GET | `/document/v1/dataflow/{dataflowId}` | List all documents in a dataflow (v1) |
| GET | `/document/dataflow/{dataflowId}` | List all documents in a dataflow |
| GET | `/document/public/{documentId}` | Download a public document without authentication |

---

### Integrations and FME (`/integration`, `/fme`)

Integrations connect a dataset schema to an external process — most commonly an FME Server workspace that transforms or validates data. The Integration controller manages these configuration records. The FME controller is the callback surface that FME Server calls after completing an import or export job.

**Integration configuration**

| Method | Path | Purpose |
|--------|------|---------|
| PUT | `/integration/listIntegrations` | List integrations matching a filter |
| PUT | `/integration/listExtensionsOperations` | List file-extension operations for a schema |
| POST | `/integration/create` | Create a new integration |
| PUT | `/integration/update` | Update an integration |
| DELETE | `/integration/{integrationId}/dataflow/{dataflowId}` | Delete an integration |
| POST | `/integration/v1/executeEUDatasetExport` | Trigger EU dataset export via integration (v1) |
| POST | `/integration/executeEUDatasetExport` | Trigger EU dataset export via integration |
| GET | `/integration/findExportEUDatasetIntegration` | Find the EU dataset export integration for a schema |
| POST | `/integration/{integrationId}/runIntegration/dataset/{datasetId}` | Execute an integration against a dataset |

**FME callbacks**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/fme/findRepositories` | List FME repositories accessible for a dataset |
| GET | `/fme/findItems` | List workspaces in an FME repository |
| POST | `/fme/operationFinished` | FME Server callback when an operation completes |
| GET | `/fme/downloadExportFile` | Download an FME-produced export file |

---

### Dataset data (`/dataset`)

The Dataset controller is the largest in the system. It owns the actual record-level data — rows, fields, attachments, and import/export operations. It also manages the editing lifecycle (enabling and disabling manual editing) and handles both the standard relational storage path and the big-data lake path (Parquet/Iceberg on S3 via Dremio, indicated by `DL` suffixes).

**Reading data**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/dataset/TableValueDataset/{id}` | Retrieve paginated table data from relational store |
| GET | `/dataset/TableValueDatasetDL/{id}` | Retrieve paginated table data from data lake |
| GET | `/dataset/{datasetId}/field/{fieldId}/attachment` | Download a file attachment for a field |
| GET | `/dataset/v1/{datasetId}/field/{fieldId}/attachment` | Download a file attachment (v1) |
| GET | `/dataset/{id}/datasetSchemaId/{datasetSchemaId}/fieldSchemaId/{fieldSchemaId}/getFieldsValuesReferenced` | Retrieve values from a referenced field for autocomplete |
| GET | `/dataset/{datasetId}/viewUpdated` | Check whether the data lake view is current |
| GET | `/dataset/{id}/editingStatus` | Retrieve the current editing status of a dataset |
| GET | `/dataset/hasEnabledEditingDatasets` | Check whether any datasets in a dataflow have editing enabled |
| GET | `/dataset/tablesUpdated` | Check whether any tables have been updated since last export |
| GET | `/dataset/list-imported-files` | List files in the import staging directory |
| GET | `/dataset/download-imported-file` | Download a file from the import staging directory |
| GET | `/dataset/getIcebergTables` | List Iceberg tables for a dataflow |
| GET | `/dataset/isIcebergTableCreated/{datasetId}/{tableSchemaId}` | Check whether an Iceberg table exists |
| GET | `/dataset/getAvailableForManualEditingTables/{datasetId}` | List tables eligible for manual editing |
| GET | `/dataset/getImportRelatedStatistics/{datasetId}` | Retrieve import statistics |
| GET | `/dataset/getReleasedDatasetDataInfo` | Retrieve data info from a released collection dataset |
| GET | `/dataset/v1/{datasetId}/record/{recordId}/geometry` | Retrieve geometry data for a record field |

**Writing data**

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/dataset/{datasetId}/table/{tableSchemaId}/record` | Insert records into a table |
| PUT | `/dataset/{id}/updateRecord` | Update existing records |
| DELETE | `/dataset/{id}/record/{recordId}` | Delete a record |
| PUT | `/dataset/{id}/updateField` | Update a single field value |
| PUT | `/dataset/{id}/updateWebformFields` | Update multiple field values for a webform row |
| PUT | `/dataset/{datasetId}/field/{fieldId}/attachment` | Upload or replace a field attachment |
| PUT | `/dataset/v1/{datasetId}/field/{fieldId}/attachment` | Upload or replace a field attachment (v1) |
| DELETE | `/dataset/{datasetId}/field/{fieldId}/attachment` | Delete a field attachment |
| DELETE | `/dataset/v1/{datasetId}/field/{fieldId}/attachment` | Delete a field attachment (v1) |
| POST | `/dataset/{datasetId}/insertRecordsMultiTable` | Insert records across multiple tables in one call |
| POST | `/dataset/{datasetId}/duplicateFieldValueExists` | Check whether a field value would violate uniqueness |

**Import**

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/dataset/v2/importFileData/{datasetId}` | Import a file into a dataset (v2, returns job id) |
| POST | `/dataset/v1/{datasetId}/importFileData` | Import a file (v1) |
| POST | `/dataset/{datasetId}/importFileData` | Import a file |
| POST | `/dataset/v1/{datasetId}/etlImport` | ETL import of structured data (v1) |
| POST | `/dataset/{datasetId}/etlImport` | ETL import of structured data |
| POST | `/dataset/{datasetId}/etlImportDL` | ETL import from a data lake file path |
| GET | `/dataset/{datasetId}/generateImportPresignedUrl` | Generate an S3 pre-signed URL for direct upload |
| POST | `/dataset/restorePrefilledTables/{datasetId}` | Restore pre-filled table data to its original state |
| POST | `/dataset/{datasetId}/createEmptyTablesV3` | Initialise empty table partitions in the data lake |
| POST | `/dataset/convertParquetToIcebergTables/{datasetId}` | Convert Parquet data lake tables to Iceberg format |
| POST | `/dataset/convertIcebergToParquetTables/{datasetId}` | Convert Iceberg tables back to Parquet |
| POST | `/dataset/createPublicFiles` | Publish dataset files for public access |

**Export**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/dataset/exportFile` | Export a dataset or table to a file format |
| GET | `/dataset/exportFileDL` | Export from the data lake |
| GET | `/dataset/exportFileThroughIntegration` | Export using an FME integration |
| GET | `/dataset/{datasetId}/exportDatasetFile` | Export an entire dataset to a file |
| GET | `/dataset/v1/{datasetId}/etlExport` | ETL export of dataset records (v1) |
| GET | `/dataset/v2/etlExport/{datasetId}` | ETL export (v2) |
| GET | `/dataset/v3/etlExport/{datasetId}` | ETL export returning a map structure (v3) |
| GET | `/dataset/v4/etlExport/{datasetId}` | ETL export with attachment support (v4) |
| GET | `/dataset/v5/etlExport/{datasetId}` | ETL export with attachment support, updated filters (v5) |
| GET | `/dataset/{datasetId}/etlExport` | ETL export |
| GET | `/dataset/{datasetId}/downloadFile` | Download a previously exported file |
| GET | `/dataset/{datasetId}/downloadFileDL` | Download a data lake export file |
| GET | `/dataset/exportPublicFile/dataflow/{dataflowId}/dataProvider/{dataProviderId}` | Download a public export for a specific provider |
| GET | `/dataset/exportPublicFile/dataflow/{dataflowId}` | Download a public export for a dataflow |

**Editing lifecycle**

| Method | Path | Purpose |
|--------|------|---------|
| PUT | `/dataset/{id}/enableEditing` | Enable manual editing for a dataset (optionally scoped to specific tables) |
| PUT | `/dataset/{id}/disableEditing` | Disable manual editing |
| PUT | `/dataset/{id}/updateGeometry` | Refresh geometry data after an import |
| PUT | `/dataset/v2/{datasetId}/updateGeometry` | Refresh geometry data (v2) |

**Delete**

| Method | Path | Purpose |
|--------|------|---------|
| DELETE | `/dataset/v1/{datasetId}/deleteDatasetData` | Delete all data from a dataset (v1) |
| DELETE | `/dataset/{datasetId}/deleteImportData` | Delete import data |
| DELETE | `/dataset/v1/{datasetId}/deleteTableData/{tableSchemaId}` | Delete data from a single table (v1) |
| DELETE | `/dataset/{datasetId}/deleteImportTable/{tableSchemaId}` | Delete data from a single table |
| DELETE | `/dataset/deleteLocksToImportProcess/{datasetId}` | Release import locks |
| DELETE | `/dataset/clearDatasetTableLocksByDataflow` | Release all table editing locks for a dataflow |
| DELETE | `/dataset/clearDatasetTableLocksByUser` | Release all table editing locks for a user |

**PAM (Policies and Measures)**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/pam/{datasetId}/getListSinglePaM/{groupPaMId}` | Retrieve individual PAM entries within a group |

---

### Dataset metadata (`/datasetmetabase`)

The Metabase controller provides the catalogue view of datasets — what datasets exist, what their names and types are, and how they relate to dataflows and data providers. It does not serve actual data records; it serves the structural information about where those records live.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/datasetmetabase/{datasetId}` | Retrieve metadata for a single dataset |
| GET | `/datasetmetabase/datasetName/{datasetId}` | Retrieve only the name of a dataset |
| GET | `/datasetmetabase/dataflow/{dataflowId}` | List reporting datasets for a dataflow |
| GET | `/datasetmetabase/{datasetId}/loadStatistics` | Load error statistics for a dataset |
| GET | `/datasetmetabase/globalStatistics/dataflow/{dataflowId}/dataSchema/{dataschemaId}` | Aggregate statistics across all reporters for a schema |
| PUT | `/datasetmetabase/updateDatasetName` | Rename a dataset |
| PUT | `/datasetmetabase/updateDatasetStatus` | Update the lifecycle status of a dataset |

---

### Dataset schema (`/dataschema`)

The schema controller manages the structural definition of datasets — what tables they contain, what fields those tables have, and what data types and constraints apply. Schema changes propagate to the validation rule engine and to any uniqueness constraints. Every reporting, collection, and reference dataset is built from a design schema that custodians define before data collection begins.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/dataschema/createEmptyDatasetSchema` | Create a new empty schema linked to a dataflow |
| GET | `/dataschema/v1/datasetId/{datasetId}` | Retrieve the full schema for a dataset (v1) |
| GET | `/dataschema/datasetId/{datasetId}` | Retrieve the full schema for a dataset |
| GET | `/dataschema/{datasetId}/noRules` | Retrieve the schema without validation rules |
| PUT | `/dataschema/{datasetId}/datasetSchema` | Update top-level schema properties |
| DELETE | `/dataschema/dataset/{datasetId}` | Delete a dataset schema |
| POST | `/dataschema/{datasetId}/tableSchema` | Add a table to a schema |
| PUT | `/dataschema/{datasetId}/tableSchema` | Update a table definition |
| DELETE | `/dataschema/{datasetId}/tableSchema/{tableSchemaId}` | Remove a table from a schema |
| PUT | `/dataschema/{datasetId}/tableSchema/order` | Reorder tables |
| POST | `/dataschema/{datasetId}/fieldSchema` | Add a field to a table |
| PUT | `/dataschema/{datasetId}/fieldSchema` | Update a field definition |
| DELETE | `/dataschema/{datasetId}/fieldSchema/{fieldSchemaId}` | Remove a field |
| PUT | `/dataschema/{datasetId}/fieldSchema/order` | Reorder fields within a table |
| GET | `/dataschema/{schemaId}/validate` | Validate a schema (checks completeness and consistency) |
| GET | `/dataschema/validate/dataflow/{dataflowId}` | Validate all schemas in a dataflow |
| GET | `/dataschema/getSchemas/dataflow/{idDataflow}` | Retrieve all schemas for a dataflow |
| POST | `/dataschema/createUniqueConstraint` | Define a uniqueness constraint on one or more fields |
| PUT | `/dataschema/updateUniqueConstraint` | Update a uniqueness constraint |
| DELETE | `/dataschema/deleteUniqueConstraint/{uniqueConstraintId}/dataflow/{dataflowId}` | Remove a uniqueness constraint |
| GET | `/dataschema/{schemaId}/getUniqueConstraints/dataflow/{dataflowId}` | List uniqueness constraints for a schema |
| GET | `/dataschema/{schemaId}/getPublicUniqueConstraints/dataflow/{dataflowId}` | List uniqueness constraints (public view) |
| POST | `/dataschema/copy` | Copy a schema from one dataflow to another |
| GET | `/dataschema/export` | Export schema definitions to a file |
| POST | `/dataschema/import` | Import schema definitions from a file |
| GET | `/dataschema/v1/getSimpleSchema/dataset/{datasetId}` | Retrieve a simplified schema (v1) |
| GET | `/dataschema/getSimpleSchema/dataset/{datasetId}` | Retrieve a simplified schema |
| GET | `/dataschema/v1/getTableSchemasIds/{datasetId}` | List table schema ids and names (v1) |
| GET | `/dataschema/getTableSchemasIds/{datasetId}` | List table schema ids and names |
| GET | `/dataschema/v1/{datasetSchemaId}/exportFieldSchemas` | Export field definitions for a table (v1) |
| GET | `/dataschema/{datasetSchemaId}/exportFieldSchemas` | Export field definitions for a table |
| POST | `/dataschema/v1/{datasetSchemaId}/importFieldSchemas` | Import field definitions (v1) |
| POST | `/dataschema/{datasetSchemaId}/importFieldSchemas` | Import field definitions |
| GET | `/dataschema/v1/dataset/{datasetId}/exportFieldSchemas` | Export field definitions by dataset id (v1) |
| GET | `/dataschema/dataset/{datasetId}/exportFieldSchemas` | Export field definitions by dataset id |
| PUT | `/dataschema/updateManuallyEditable/{datasetId}` | Toggle whether the dataset is manually editable |

---

### Webforms (`/webform`)

Webforms are preconfigured reporting templates that provide a structured, form-based entry interface instead of the generic table view. A webform maps one or more dataset tables to a named template, optionally with a versioned JSON configuration that the frontend uses to render the form. Custodians configure which webform applies to a dataset; the configuration itself is stored as a JSON blob.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/webform/listAll` | List all available webform templates |
| POST | `/webform/webformConfig` | Create a webform configuration |
| PUT | `/webform/webformConfig` | Update a webform configuration |
| GET | `/webform/webformConfig/{id}` | Retrieve a webform configuration by id |
| DELETE | `/webform/webformConfig/{id}` | Delete a webform configuration |
| POST | `/webform/{datasetId}/webformConfig` | Apply a webform configuration to a dataset |
| GET | `/webform/{datasetId}/getWebformConfigSchema` | Retrieve the applied webform schema for a dataset |
| GET | `/webform/{datasetId}/restoreWebformConfigSchema` | Restore the webform schema to a named version |

---

### Data collections (`/datacollection`)

A data collection is a read-only aggregation of all reporters' validated data for a dataflow. Custodians create a collection when they are ready to freeze the reporting schema and open the dataflow for data submission. The creation process provisions one reporting dataset per representative and sets up the underlying PostgreSQL schemas via the Recordstore Service.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/datacollection/create` | Create a data collection for a dataflow |
| PUT | `/datacollection/update/{dataflowId}` | Update data collection configuration |

---

### Snapshots and releases (`/snapshot`)

A snapshot is a point-in-time copy of a dataset. For design datasets, snapshots let custodians save and restore schema configurations. For reporting datasets, a release is a special snapshot that moves validated data into the official data collection. The release process validates data, copies records, generates a receipt PDF, and publishes the data according to the dataflow's public visibility settings.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/snapshot/dataset/{idDataset}/listSnapshots` | List all snapshots for a reporting dataset |
| POST | `/snapshot/dataset/{idDataset}/create` | Create a new snapshot |
| DELETE | `/snapshot/v1/{idSnapshot}/dataset/{idDataset}/delete` | Delete a snapshot (v1) |
| DELETE | `/snapshot/{idSnapshot}/dataset/{idDataset}/delete` | Delete a snapshot |
| POST | `/snapshot/{idSnapshot}/dataset/{idDataset}/restore` | Restore a dataset from a snapshot |
| GET | `/snapshot/dataschema/{idDesignDataset}/listSnapshots` | List schema snapshots for a design dataset |
| POST | `/snapshot/dataschema/{idDatasetSchema}/dataset/{idDesignDataset}/create` | Create a schema snapshot |
| POST | `/snapshot/{idSnapshot}/dataschema/{idDesignDataset}/restore` | Restore a schema from a schema snapshot |
| DELETE | `/snapshot/{idSnapshot}/dataschema/{idDesignDataset}/delete` | Delete a schema snapshot |
| POST | `/snapshot/dataflow/{dataflowId}/dataProvider/{dataProviderId}/release` | Release a provider's data into the data collection |
| GET | `/snapshot/receiptPDF/dataflow/{dataflowId}/dataProvider/{dataProviderId}` | Download the release receipt PDF |
| GET | `/snapshot/v1/historicReleases` | List historical release records (v1) |
| GET | `/snapshot/historicReleases` | List historical release records |
| GET | `/snapshot/historicReleasesRepresentative` | List releases for a specific representative |
| POST | `/snapshot/exportHistoricReleases/{datasetId}` | Export release history to file |
| GET | `/snapshot/downloadHistoricReleases/{datasetId}` | Download exported release history |

---

### EU dataset (`/euDataset`)

The EU Dataset is the single consolidated view of data across all member state reporters for a dataflow. Populating it copies the released data from each data collection into one EU-level dataset, making it available for analysis and downstream publication.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/euDataset/v1/populateData/dataflow/{dataflowId}` | Populate the EU dataset from released data (v1, queued as job) |
| POST | `/euDataset/populateData/dataflow/{dataflowId}` | Populate the EU dataset |

---

### Reference datasets (`/referenceDataset`)

Reference datasets hold lookup data — codelists, country lists, and other controlled vocabularies — that other datasets reference for validation. They belong to a dataflow but are managed separately because they may be shared across multiple dataflows and may be marked as updatable to allow in-place corrections.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/referenceDataset/referenced/dataflow/{id}` | List dataflows that use reference datasets from a given dataflow |
| PUT | `/referenceDataset/{datasetId}` | Update reference dataset settings (updatable flag) |

---

### Validation (`/validation`, `/rules`)

The Validation Service executes quality rules against dataset records and stores the resulting errors. Triggering validation is an asynchronous operation — the request queues a job via the Orchestrator and returns immediately. Results are retrieved by querying the validation error tables after the job completes.

The Rules controller manages the quality rule definitions themselves. Rules can be automatic (generated from field type, mandatory, or uniqueness constraints) or manual (SQL expressions or integrity checks written by custodians). The controller also exposes SQL validation tooling that lets custodians test expressions before activating them.

**Validation execution and results**

| Method | Path | Purpose |
|--------|------|---------|
| PUT | `/validation/dataset/{id}` | Trigger validation of a dataset |
| GET | `/validation/listValidations/{id}` | List validation errors for a dataset (paginated) |
| GET | `/validation/listGroupValidations/{id}` | List grouped validation errors (paginated) |
| GET | `/validation/listGroupValidationsDL/{id}` | List grouped errors from data lake dataset |
| POST | `/validation/export/{datasetId}` | Export validation errors to file |
| GET | `/validation/downloadFile/{datasetId}` | Download a validation error export file |
| PUT | `/validation/restartTask/{taskId}` | Restart a stalled validation task |
| GET | `/validation/listInProgressValidationTasks/{timeInMinutes}` | List validation tasks running longer than a threshold |
| DELETE | `/validation/deleteLocksToReleaseProcess/{datasetId}` | Release locks held by a validation-during-release process |

**Quality rules**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/rules/{datasetSchemaId}/dataflow/{dataflowId}` | Retrieve all rules for a schema |
| PUT | `/rules/createNewRule` | Create a new quality rule |
| PUT | `/rules/updateRule` | Update a quality rule |
| PUT | `/rules/updateAutomaticRule/{datasetId}` | Update an automatically generated rule |
| PUT | `/rules/updateAutomaticQCsDefaultLevelError` | Change the default error level for automatic rules |
| DELETE | `/rules/deleteRule` | Delete a rule by id |
| POST | `/rules/validateAllRules` | Validate all rules in a schema |
| POST | `/rules/validateSqlRule` | Validate a SQL rule expression against a dataset |
| POST | `/rules/validateSqlRules` | Validate all SQL rules in a schema |
| POST | `/rules/runSqlRule` | Execute a SQL rule and return matching rows |
| POST | `/rules/evaluateSqlRule` | Estimate what percentage of records a SQL rule would affect |
| POST | `/rules/exportQC/{datasetId}` | Export quality control rules to file |
| GET | `/rules/downloadQC/{datasetId}` | Download an exported QC rules file |
| GET | `/rules/historicInfo` | Retrieve historical execution stats for a rule |
| GET | `/rules/historicDatasetRules` | Retrieve rule history across a dataset |

---

### Recordstore and processes (`/recordstore`, `/process`)

The Recordstore Service manages the low-level PostgreSQL schemas where dataset records are stored, as well as the snapshot file operations. The Process controller provides a monitoring view over long-running operations — releases, imports, and validations — that the Orchestrator tracks. The `/process/**` prefix is routed through the gateway, making process status visible to the frontend for job polling.

**Process monitoring**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/process/` | List processes with filters (status, dataflow, user) |
| POST | `/process/{processId}/priority/{priority}` | Change the priority of a queued process |

**Recordstore snapshot operations**

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/recordstore/dataset/{datasetId}/snapshot/create` | Create a snapshot of a dataset's records |
| POST | `/recordstore/dataset/{datasetId}/snapshot/restore` | Restore records from a snapshot |
| POST | `/recordstore/dataset/{datasetId}/snapshot/delete` | Delete a snapshot |
| GET | `/recordstore/findReleaseTasksInProgress/{timeInMinutes}` | List release tasks running longer than a threshold |
| GET | `/recordstore/findReleaseTaskByTaskId/{taskId}` | Retrieve a release task by id |
| POST | `/recordstore/restoreSpecificFileSnapshotData` | Restore a range of snapshot file chunks |
| GET | `/recordstore/recoverCheck` | Verify record integrity by field id range |
| GET | `/recordstore/getLatestReleaseSnapshots` | List the most recent release snapshot files |
| GET | `/recordstore/downloadSnapshot/{datasetId}` | Download a snapshot file |

---

### Collaboration (`/collaboration`)

The Collaboration Service provides a threaded messaging system between reporters and reviewers within a dataflow. Each thread is scoped to a dataflow and a data provider. Messages can include file attachments. The service also sends email notifications when new messages arrive.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/collaboration/createMessage/dataflow/{dataflowId}` | Post a new message in a thread |
| POST | `/collaboration/createMessage/dataflow/{dataflowId}/attachment` | Post a message with a file attachment |
| PUT | `/collaboration/updateMessageReadStatus/dataflow/{dataflowId}` | Mark messages as read or unread |
| DELETE | `/collaboration/deleteMessage/dataflow/{dataflowId}` | Delete a message |
| GET | `/collaboration/findMessages/dataflow/{dataflowId}` | Retrieve a paginated message thread |
| GET | `/collaboration/findMessages/dataflow/{dataflowId}/getMessageAttachment` | Download a message attachment |

---

### Notifications (`/notification`)

The Communication Service distributes real-time notifications to the browser via WebSocket, but it also exposes a REST interface for creating and managing notifications. User notifications are ephemeral alerts about events (import completed, validation failed). System notifications are platform-wide banners that appear to all users until deleted.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/notification/createUserNotification` | Create a user-scoped notification |
| POST | `/notification/createSystemNotification` | Create a system-wide notification |
| PUT | `/notification/updateSystemNotification` | Update a system notification |
| DELETE | `/notification/deleteSystemNotification/{systemNotificationId}` | Delete a system notification |
| GET | `/notification/findUserNotifications` | Retrieve the current user's notification list |
| GET | `/notification/findSystemNotifications` | List all active system notifications |
| GET | `/notification/checkAnySystemNotificationEnabled` | Check whether any system notification is currently active |

---

### ROD obligations (`/obligation`, `/obligation_client`, `/obligation_country`, `/obligation_issue`)

The ROD Service synchronises with the EEA's Reporting Obligations Database. It does not manage the obligations itself — those are mastered in ROD and pulled by this service periodically. The REST endpoints allow the frontend and other services to query the local cache of obligations, clients, countries, and environmental issues without calling ROD directly.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/obligation/findOpened` | Find open obligations, optionally filtered by client, spatial scope, issue, or deadline range |
| GET | `/obligation/{id}` | Retrieve a single obligation by ROD id |
| GET | `/obligation_client/` | List all reporting clients (organisations) |
| GET | `/obligation_country/` | List all reporting countries |
| GET | `/obligation_issue/` | List all environmental issue categories |

---

### Release receipts (`/release-receipts`)

Release receipts are records that acknowledge a provider's data release. They are distinct from the snapshot mechanism: a receipt is the business confirmation that a release occurred, carrying additional metadata for audit purposes. This controller is not routed through the API gateway and is used only via internal Feign calls.

---

## Private and internal-only endpoints

Every endpoint whose URL contains `/private/` is blocked by the gateway. These endpoints exist so that microservices can call each other without going through the public API surface. They handle tasks such as provisioning Keycloak resources when a dataset is created, reading internal metadata that should not be exposed to callers, cascading deletes across services, and managing distributed locks.

The orchestrator's controllers — `/jobs/**`, `/jobHistory/**`, `/jobProcess/**`, and `/redis/**` — are not registered in the gateway routing at all. They are called exclusively by the Orchestrator itself and by other backend services that need to track job state.

The following table summarises which prefixes are internal-only.

| Prefix | Owner service | Reason for exclusion |
|--------|--------------|----------------------|
| `/**/private/**` | All services | Blocked by gateway `ignoredPatterns` |
| `/jobs/**` | Orchestrator | Not registered in gateway routing |
| `/jobHistory/**` | Orchestrator | Not registered in gateway routing |
| `/jobProcess/**` | Orchestrator | Not registered in gateway routing |
| `/redis/**` | Orchestrator | Not registered in gateway routing |
| `/lock/**` | Common utilities | Not registered in gateway routing |
| `/dataflowDocument/**` | Dataflow Service | Not registered in gateway routing |
| `/release-receipts/**` | Dataset Service | Not registered in gateway routing |
| `/testDataset/**` | Dataset Service | Routed but only has private sub-paths |

Notable private endpoint groups, for reference when tracing inter-service calls:

- `/dataflow/private/v1/{dataflowId}/isBigDataflow` — tells other services whether a dataflow's data exceeds the threshold for data lake handling.
- `/datasetmetabase/private/create` — called by the Dataflow Service after it creates a new representative, to provision the corresponding reporting dataset metadata.
- `/dataschema/private/{id}` — allows other services to read schema definitions without going through the public endpoint.
- `/resource/private/delete` — called internally when dataflows or datasets are deleted, to clean up Keycloak resource groups.
- `/rules/private/createAutomaticRule` — called by the Dataset Schema Service whenever a field type or mandatory constraint changes, to keep validation rules in sync with the schema.
- `/validation/private/executeValidation/{datasetId}` — the actual validation execution call, invoked by the Orchestrator after it has set up the process context.
- `/recordstore/private/dataset/create/{datasetName}` — provisions the PostgreSQL schema for a new dataset, called by the Dataset Service.
- `/jobs/private/updateJobStatus/{id}/{status}` — called by the Dataset and Validation services to report job progress back to the Orchestrator.

---

## API versioning

Where multiple versions of an endpoint exist, they appear side by side in the URL space (`/v1/`, `/v2/`, etc.) and the unversioned form is typically the oldest behaviour that is kept for backwards compatibility. The most significant version progressions are:

- **ETL export** (`/dataset/etlExport`): v1 through v5, each adding new filter parameters or changing the response structure from a streaming body to a map of results with attachment support.
- **Import file data** (`/dataset/importFileData`): v1 returns void; v2 returns a job id, allowing the caller to poll status.
- **Snapshot delete** (`/snapshot/{id}/dataset/{id}/delete`): v1 is identical in behaviour to the unversioned form; the split exists to support legacy client integrations.
- **Schema export** (`/dataschema/exportFieldSchemas`): v1 scopes the export to a schema id with an optional table filter; the dataset-scoped variant is a later addition.

---

## Missing public endpoints

This section documents service-layer capabilities that exist in code but have no public REST endpoint. They are grouped by how significant the gap is — whether it blocks legitimate external use cases or simply leaves admin operations inaccessible.

### Operational recovery — scheduler logic not triggerable manually

The Orchestrator runs a set of maintenance schedulers that handle stuck or orphaned jobs. None of these can be triggered manually, which means recovery from failures always requires waiting for the next automatic run. The most significant gaps are:

**`GET /jobs/executeQueuedJobs`** (currently absent) — the `JobForExecutingQueuedJobs` scheduler runs every minute and advances queued jobs. After a service restart or a crash mid-execution, jobs can remain in `QUEUED` state until the scheduler fires. An admin endpoint would allow immediate recovery without waiting.

**`POST /jobs/cancelOrphanedJobs`** (currently absent) — `JobForCancellingJobsWithoutProcess` runs every 30 minutes and cancels any `IN_PROGRESS` job that has no associated process record. This situation arises when process creation fails partway through. Without a manual trigger, stuck jobs block the concurrency slot for up to 30 minutes.

**`POST /jobs/cleanupFinishedJobs`** (currently absent) — `JobForCleanupOfFinishedJobs` runs once a day at midnight and removes terminal-state jobs older than one day. There is no way to trigger this ahead of schedule, for example during a database housekeeping window.

**`POST /jobs/pollFmeStatus`** (currently absent) — `JobForFmeStatusPolling` checks FME Server every 10 minutes for the status of active import jobs. If FME completes a job but its callback to Reportnet3 fails, the import job sits in `IN_PROGRESS` until the scheduler fires. A targeted poll for a specific FME job id would allow immediate resolution.

### Validation — batch recovery and single-rule retrieval

**`PUT /validation/restartDelayedTasks`** (currently absent) — `PUT /validation/restartTask/{taskId}` exists to restart a single stuck task, but there is no endpoint to restart all tasks that exceed the configured timeout threshold in one call. `JobForRestartingDelayedValidationTasks` does this automatically every five minutes, but during an incident an administrator has to restart tasks one by one.

**`GET /rules/{datasetSchemaId}/rule/{ruleId}`** (currently absent) — `RulesService` has a `findRule(datasetSchemaId, ruleId)` method used internally when other services need to look up a specific rule. The public endpoint `GET /rules/{datasetSchemaId}/dataflow/{dataflowId}` returns the entire rules schema. Fetching a single rule requires loading the full schema and filtering client-side.

**`GET /rules/{datasetSchemaId}/integrityConstraint/{integrityId}`** (currently absent) — integrity constraints between schemas are managed internally but have no public lookup endpoint. A caller that creates an integrity rule and later needs to inspect it must retrieve the full rules schema.

### Representatives — release status and visibility checks

**`GET /representative/{dataflowId}/provider/{dataProviderId}/releaseStatus`** (currently absent) — `RepresentativeService.checkDataHaveBeenRelease(dataflowId, dataProviderId)` checks whether a provider has released data for a dataflow. The frontend uses this to show or hide release-related UI elements, but the check is currently made via a chain of internal calls rather than a dedicated endpoint. Exposing it directly would also allow external reporting tools to check release status.

**`GET /representative/{dataflowId}/provider/{dataProviderId}/restrictFromPublic`** (currently absent) — `RepresentativeService.checkRestrictFromPublic(dataflowId, dataProviderId)` checks whether a provider's data is excluded from the public view. The `PUT` endpoint to set this flag exists; the read endpoint to retrieve the current flag value does not.

### Dataset — missing lookup endpoints

**`GET /datasetmetabase/byProviders`** (currently absent) — `DatasetMetabaseService.getDatasetsByProviderIds(List<Long>)` accepts a list of provider ids and returns all datasets for those providers across any dataflow. There is no public equivalent; callers must query per-provider.

**`GET /dataschema/{datasetSchemaId}/isReference`** (currently absent) — `DatasetSchemaService.isReferenceSchema(datasetSchemaId)` tells callers whether a schema belongs to a reference dataset. This distinction drives behaviour in both the frontend and validation logic but has no dedicated public endpoint.

**`GET /dataset/{datasetId}/providerMapping`** (currently absent) — the Dataset Service can resolve a dataset id to its data provider id, but this mapping is only accessible internally via `DatasetService.getDataProviderIdById`. External callers that work with dataset ids (ETL integrations, external reporting tools) cannot resolve the corresponding provider without a separate Metabase call that may not expose this detail.

### Admin and monitoring — no observability surface

The platform has no admin REST surface for monitoring dataset statistics (record counts, field counts, error counts per rule) outside of the validation error list endpoints. `ValidationService` methods for `countRecordsDataset`, `countFieldsDataset`, and `getNumberOfRecordsInTable` exist but are called only internally. Adding even simple count endpoints under a guarded admin prefix would support operational dashboards without requiring direct database access.

---

## API consistency problems and improvement recommendations

The API has accumulated inconsistencies as new endpoints were added independently across services. This section documents the concrete problems found across the controller interfaces, grouped by category, and recommends how each should be standardised going forward.

### HTTP verb misuse

**GET with a request body.** Two export endpoints use GET but accept a request body containing filter criteria:

```
GET /dataset/exportFile        — body: ExportFilterVO
GET /dataset/exportFileDL      — body: ExportFilterVO
```

HTTP GET requests must not carry a body; many proxies, CDNs, and HTTP clients strip or reject it. These should be changed to POST. Since export is a side-effecting operation (it generates a file), POST is semantically correct regardless.

**PUT and POST used for read-only queries.** Several endpoints use mutating verbs but perform only reads:

```
PUT  /integration/listIntegrations           — returns a list (read)
PUT  /integration/listExtensionsOperations   — returns a list (read)
PUT  /rules/existsRuleRequired               — returns a boolean (read)
POST /dataflow/getDataflows                  — returns a paginated list (read)
POST /dataflow/referenceDataflows            — returns a paginated list (read)
POST /dataflow/businessDataflows             — returns a paginated list (read)
POST /dataflow/citizenDataflows              — returns a paginated list (read)
POST /dataflow/getPublicDataflows            — returns a paginated list (read)
POST /dataflow/getPublicDataflowsByObligation — returns a paginated list (read)
```

The dataflow listing endpoints use POST because they accept a filter map in the request body. The idiomatic approach for filtered queries is either to encode the filters as query parameters (for simple cases) or to keep POST but rename the paths to avoid the misleading `get` prefix — for example, `POST /dataflow/search` or `POST /dataflow/query`. The integration listing endpoints should be GET with the filter as a query parameter, since `IntegrationVO` used as a filter only carries a handful of fields.

**GET causing side effects.** One notable case:

```
GET /collaboration/private/notifyNewMessages — sends email and in-app notifications
```

Sending notifications is a side effect. This should be POST. The current path is internal-only, but the principle matters for maintainability: GET must be safe (idempotent, no state change).

**Rules service using PUT for existence checks and deletes:**

```
PUT /rules/existsRuleRequired      — checks if a rule exists (should be GET)
PUT /rules/deleteRuleRequired      — deletes a rule (should be DELETE)
```

These should use the verbs that match their semantics.

---

### Path variable naming

Path variable names are inconsistent across the API for the same conceptual identifier. The table below shows the variants in use:

| Concept | Variants found |
|---------|---------------|
| Dataset id | `{id}`, `{datasetId}`, `{idDataset}`, `{idDesignDataset}` |
| Snapshot id | `{idSnapshot}` (snapshot controller), `{snapshotId}` (snapshot controller) |
| Dataflow id | `{dataflowId}`, `{idDataflow}` |
| Schema id | `{datasetSchemaId}`, `{schemaId}`, `{idDatasetSchema}`, `{idDataSetSchema}` |
| Document id | `{documentId}`, `{idDocument}` |
| Weblink id | `{idLink}` |
| Representative id | `{dataflowRepresentativeId}`, `{representativeId}` |

The recommendation is to adopt `{resourceTypeId}` as the single form — for example, `{datasetId}`, `{dataflowId}`, `{snapshotId}`, `{schemaId}`, `{documentId}` — and apply it consistently across all controllers. The `{id}` placeholder in particular (`/dataset/TableValueDataset/{id}`) is ambiguous when read outside its context.

---

### Parameter location inconsistency

The same logical parameter appears in the path in some endpoints and as a query parameter in others, even for the same type of operation:

| Parameter | As path variable | As query parameter |
|-----------|------------------|--------------------|
| `dataflowId` | `/integration/{integrationId}/dataflow/{dataflowId}` | `/integration/v1/executeEUDatasetExport?dataflowId=` |
| `datasetId` | `/dataset/{datasetId}/table/{tableSchemaId}/record` | `/integration/private/executeIntegration?datasetId=` |
| `tableSchemaId` | `/dataset/{datasetId}/table/{tableSchemaId}/record` | `/dataset/{id}/updateRecord?tableSchemaId=` |
| `integrationId` | `/integration/{integrationId}/dataflow/{dataflowId}` | `/integration/private/findExportIntegration?integrationId=` |
| `datasetSchemaId` | `/rules/{datasetSchemaId}/dataflow/{dataflowId}` | `/rules/private/findSqlSentencesByDatasetSchemaId?datasetSchemaId=` |

The convention should be: if an id identifies the primary resource being operated on, put it in the path. If it is a secondary filter or qualifier, it can be a query parameter. By this rule, `tableSchemaId` should be in the path when it scopes the operation (as in the record insert endpoint), and only a query parameter when it is truly optional (as in export endpoints where it filters to one table).

---

### Pagination inconsistency

Two different pagination models are used across the API:

```
pageNum / pageSize  — used by: /dataflow/completed, /dataflow/getDataflows,
                               /representative/dataProvider, /jobs/, /process/,
                               /validation/listValidations/{id}

limit / offset      — used by: /dataset/v1/{datasetId}/etlExport,
                               /dataset/v2/etlExport/{datasetId},
                               /dataset/v3/etlExport/{datasetId}
```

`pageNum/pageSize` and `limit/offset` are not interchangeable: `pageNum=2, pageSize=20` returns rows 21–40, but the equivalent in `limit/offset` is `limit=20, offset=40`. The ETL export endpoints adopt `limit/offset` because they were designed for cursor-style consumption by external ETL tools, which is a reasonable use case. However, the inconsistency should be documented explicitly at each endpoint rather than assumed by callers. New paginated endpoints should use `pageNum/pageSize` unless there is a specific streaming or cursor-based access requirement.

Sort parameters also vary:
- `asc` (boolean) — most list endpoints
- `sortedColumn` — jobs and process endpoints
- `fields` — validation list endpoints (a comma-separated sort-and-field-selection string)
- `orderHeader` — dataflow search endpoints

The dataflow search sort parameter `orderHeader` should be renamed to `sortedColumn` to match the pattern used elsewhere.

---

### Response type inconsistency for file downloads

Five different patterns are used to return files from endpoints:

| Pattern | Endpoints using it |
|---------|-------------------|
| `ResponseEntity<byte[]>` | `/dataset/{datasetId}/field/{fieldId}/attachment`, `/dataschema/export`, schema field export endpoints, collaboration attachment |
| `ResponseEntity<InputStreamResource>` | `/dataset/exportPublicFile/...` |
| `ResponseEntity<StreamingResponseBody>` | `/snapshot/receiptPDF/...`, `/dataset/v1/{datasetId}/etlExport` |
| `Resource` | `/document/{documentId}/dataflow/{dataflowId}`, `/document/public/{documentId}` |
| `byte[]` (plain) | `/document/private/.../snapshot`, `/document/private/.../collaborationattachment` |
| `void` + `HttpServletResponse` injection | `/dataset/{datasetId}/downloadFile`, `/user/downloadUsersByCountry`, `/snapshot/downloadHistoricReleases` |

The `ResponseEntity<StreamingResponseBody>` pattern is the correct approach for large files: it does not buffer the entire response body in memory and allows the container to stream data to the client. The `void + HttpServletResponse` injection pattern works but is non-standard and harder to test. The plain `byte[]` return type loads the entire file into heap memory, which is a problem for large attachments.

The recommendation is to standardise on `ResponseEntity<StreamingResponseBody>` for all file download endpoints, including schema exports, document downloads, and attachments. The `ResponseEntity<byte[]>` pattern should only remain where the caller genuinely needs the full content in memory (for example, when re-encoding or signing the bytes before returning them).

---

### DELETE returning a body

Two delete endpoints return a `Map<String, Object>` instead of void:

```
DELETE /dataset/v1/{datasetId}/deleteDatasetData     — returns Map<String, Object>
DELETE /dataset/v1/{datasetId}/deleteTableData/{tableSchemaId}  — returns Map<String, Object>
```

Their non-versioned counterparts (`DELETE /dataset/{datasetId}/deleteImportData`, `DELETE /dataset/{datasetId}/deleteImportTable/{tableSchemaId}`) return void. The v1 variants appear to return a job id or status map to support async tracking. If async tracking is the intent, the better pattern is to return `202 Accepted` with a `Location` header pointing to the job resource, or simply return the job id in the response body as `{ "jobId": 123 }` with a defined type rather than a raw map.

---

### Boolean parameter naming

Boolean query parameters follow no consistent naming convention:

| Parameter | Endpoints using it |
|-----------|-------------------|
| `isBigDataflow` | `/dataset/private/updateStatistics/{id}` |
| `showPublicInfo` | `/dataflow/private/updatePublicStatus` |
| `restrictFromPublic` | `/snapshot/dataflow/.../release`, `/representative/update/restrictFromPublic/...` |
| `isPublic` | `/document/upload/{dataflowId}` |
| `manuallyEditable` | `/dataschema/updateManuallyEditable/{datasetId}` |
| `deletePrefilledTables` | `/dataset/v1/{datasetId}/deleteDatasetData` |

The recommendation is to drop `is`/`has` prefixes and use plain adjectives or verb phrases consistently: `public`, `restrictedFromPublic`, `manuallyEditable`, `bigDataflow`, `deletePrefilledTables`. This matches the style already used by the majority of parameters.

---

### Missing annotation on path variable

`GET /user/userRoles/dataflow/{dataflowId}` — the `dataflowId` path variable in the interface method declaration is missing its `@PathVariable` annotation. Spring will still bind it by name convention in this case, but the annotation is required for Feign clients to resolve the variable correctly. This should be corrected in `UserManagementController.java`.
