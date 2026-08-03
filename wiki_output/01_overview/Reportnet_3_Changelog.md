---
title: "Reportnet 3 Changelog"
updated: "2025-09-11 19:02"
updated_by: "KOURETAS Fotios"
---

# Reportnet 3 Changelog

DISCLAIMER   
---  
**From December 2025, items that can be shared publicly will be listed on:<https://help.reportnet.europa.eu/general/whats-new/>**  
  
[Edit this section](Reportnet_3_Changelog/edit.md)

## Sprint 104 - deployed (May 19th 2026)

  * In Validations, multi conditional link validations are now possible through the reference table 
  * In Datasets, retrieval and rendering of large geospatial data has been optimized: geometry values are no longer loaded upfront but fetched on demand,  
preventing browser crashes on datasets with large polygon data.
  * In Validations, the automatic email format check has been fixed to correctly accept email addresses with long domain extensions.
  * In Dataflows, test dataflows are protected from being available public with the introduction of is official attribute.
  * In Webforms, editing is now automatically disabled when the lead reporter who enabled it is removed from a dataflow, preventing editing from becoming  
permanently locked.
  * In Dataflows, the delivery receipt has been updated: the standard acceptance text is now pre-populated and editable, the receipt text and date label have been  
corrected, and the dataflow link has been added below the title.



[Edit this section](Reportnet_3_Changelog/edit.md)

## Sprint 103 - deployed (May 19th 2026)

  * Fixed middle-clicking on Data Collection and EU Dataset icons to correctly open them in a new browser tab.
  * Extended provider-based macro replacement to Field Comparison validation rules, enabling data provider codes to be substituted before query execution.
  * Fixed the right-click tab context menu in Webforms to position correctly regardless of scroll position.
  * In Datasets, the "Delete dataset data" button is visually enhanced to reduce the risk of accidental deletion.
  * In Validations, historical validation results are now stored per snapshot, and a new endpoint allows downloading results for a specific release by snapshot ID.
  * In Validations, QC rules containing unsupported SQL syntax char ";" are now marked as invalid and blocked from execution, with an error message displayed to the user.
  * In Validations icon shown on Dataset table tabs displays the appropriate warning indication, instead of the error icon - for only warnings after validation.
  * In Data Collections, release process reliability has been improved to prevent duplicate or missing tasks.



[Edit this section](Reportnet_3_Changelog/edit.md)

## Sprint 102 - deployed (Mar 31st 2026)

  * Improved the rearranging of tabs functionality in the **Dataset View page** , ensuring stability while rearranging tables.
  * Fixed a bug in **QC rules** where a trailing single-line comment (--) was causing an unnecessary warning.
  * Implemented alphabetical sorting of datasets in the **Provider’s View** .
  * Adjusted Release jobs so that they start with status Queued instead of In Progress.
  * Added database indexes in key areas to improve performance.
  * Added export functionality in **Preparation datasets** .
  * Added validation functionality in **Preparation datasets** .
  * Added an optional preparationDataset parameter in **FME calls** .
  * In **Dataset Design** for Big Data dataflows, disabled certain schema modification actions when a table already contains data.
  * In **public countries View** , Moldova was added to the EEA Cooperating Countries.



[Edit this section](Reportnet_3_Changelog/edit.md)

## Sprint 101 - deployed (Mar 4th 2026)

  * In **Validations** , blank geometries are handled to prevent validation tasks from being canceled.
  * In **Security** , MongoDB has been upgraded for increased security.
  * In **Webforms** , block alignment behaviour has been improved for increased readability.
  * In **Import Data** , memory handling has been improved to prevent pod restarts during large imports.
  * In **Data Collections** , delete preparation set functionality has been implemented.
  * In **Data Collections** , a new endpoint retrieves all preparation dataset names and codes.
  * In **Dataflows** , limits have been enforced on the number of schemas, tables and fields.
  * In **Preparation datasets** , import functionality has been added, including processing and parquet table creation.
  * In **Validations** , execution has been modified so that validations without release jobs can run in parallel.
  * In **Webforms** , searching and sorting have been added to the Configure Webform dialog.



[Edit this section](Reportnet_3_Changelog/edit.md)

## Sprint 100 - deployed (Mar 4th 2026)

  * In **Security** , Java libraries have been upgraded in Reportnet 3 services for increased security.
  * In **Dataflows** , supporting document attachments download improved functionality.
  * In **Business Dataflows** , Sensitive Non Classified (SNC) data are treated as business data and additional safeguards prevent accidental exposure or insecure processing.
  * In **Design and Test datasets** , a custodian can act as a validation provider and set the provider code during validation.
  * In **Import Data** , attachments can be uploaded via the RN3 API without requiring the dataset to be manually unlocked.
  * In **Job Monitoring** , silent releases are visible with a dedicated icon.
  * In **Data Collections** , a lead reporter can create and manage preparation sets from the provider page.
  * In **Data Collections** , preparation set datasets can now be created and viewed through the UI.
  * In **Big Data dataflows** , unnecessary Citus schema creation has been removed improving the create data collection functionality.



[Edit this section](Reportnet_3_Changelog/edit.md)

## Sprint 99 - deployed (Jan 22nd 2026)

  * In **Spatial Data** , the geojson value is not shown in the UI. Instead an INFO button is shown where the user can download the value instead of inspecting it. 
  * In **Import Data** for Citus dataflows, if the imported file only contains headers, a notification is sent to the user.
  * In **Import Data** the UI does not allow adding attachments larger than 2GB for Citus dataflows or 10GB for Big Data dataflows.
  * In **Export Data** , an observer of a dataflow is able to export just like the custodians.
  * In **Business Dataflows** , if the dataflow is big data, it is considered SNC.
  * In **Business Dataflows** , national coordinator permissions are not created.
  * In **QC rules** , if the rule contains a comment at the end, it is marked as invalid.
  * In **Public Dataflows** , the date of the correction requested is shown.
  * In **Job Monitoring** , ETL IMPORT jobs are shown in the job type filter.
  * In **Data Collections** , in the number of records comparison tool, the default country of the filter has been changed to the first one in the list.



[Edit this section](Reportnet_3_Changelog/edit.md)

## Sprint 98 - deployed (Jan 22nd 2026)

  * In the **Front Page** , instead of the supporting documents, a link to the documentation site is shown.
  * In **Editing of Data** , only one user is able to edit tabular data or a webform inside a dataset.
  * In **Documentation** , limitation of editing to one user at a time has been documented.
  * In **Documentation** , historic release date change tool for Admins and Custodians has been documented.
  * In **UI** , dark theme enhancements have been implemented.
  * In **Data collection creation** , fixes have been implemented to reduce complexity and duration.
  * In **Snapshots** , snapshots are now available for Design and Test datasets.
  * In **Job Monitoring** , all jobs types can be canceled.
  * In **Validation** , for Big data expressions and Citus expressions and automated rules, the job calculates up to 1001 errors per QC.
  * In **Validation** , if a geometry is invalid, the reason variable shows why.
  * In **QC rules** , Level Error has been renamed to Severity Level.
  * In **QC rules** , if a big data dataflow has spatial data fields, we have removed unnecessary automated rules that were used in Citus dataflows.
  * In **Public Dataflows Country Page** , technical status and date is shown.



[Edit this section](Reportnet_3_Changelog/edit.md)

## Sprint 97 - deployed (Dec 11th 2025)

  * In **Jobs Monitoring** , users that are both admins and lead reporters can view all jobs due to the admin role.
  * In **Notifications** , updated notification messages to be more user friendly and containing action items for the user.
  * In **Webforms** , checking for duplicate entity ID is now faster.
  * In **Webforms** , changed date time component so that it contains a clear button.
  * In **QC rules** , running a single SQL rule or evaluating it when the rule contains variable R3_COUNTRY_CODE is now working correctly.
  * In **Documentation** , documented cancelled validation tasks and geospatial data.
  * In **Data retrieval** , minimized errors when loading data that were caused due to missing metadata.
  * In **Table Schema deletion** , data of the table are removed as well.
  * In **Import** , if a field is multiline text and it contains more than 10000 characters, a warning notification ios sent to the user and the value is not stored.
  * In **Release** with attachments, old attachments of provider are now removed from the data collection.
  * In **Release** , provided admins with a silent release button in order to release provider's data without any notifications or mails being sent. The release dates are also not updated.
  * In **Historic Releases** , provided admins and custodians of a dataflow with edit buttons for the historic release dates, in order to be able to edit them.



[Edit this section](Reportnet_3_Changelog/edit.md)

## Sprint 96 - deployed (Dec 11th 2025)

  * In **Documentation** , documented export API features, validation API, import API, polling for job status API, how to manage records for big data, dataset schema export process and all user notification messages.
  * In **Etl export** v4 (zip with csv files) and v5 (zip with parquet files) added parameter for data provider codes in order to retrieve data for some providers from the data collection or the EU dataset.
  * In **Imported files** , added a button and window to list imported files in a dataset and a download button for each file.
  * In **Data viewing** , changed vertical alignment of values in table cells to top.
  * In **Release** , added failure notification if editing has been enabled for a dataset of the provider.
  * In **Validation** , in Big data dataflows for automated QCs and SQL expressions limited number of errors to 1001 per QC. If this number is reached, the user is shown the validation code with 1000+ records in Show validations.
  * In **QC rules** , removed the Default severity button for design datasets after the creation of the data collection.
  * In **Dataset schema design** , removed the option for a user to add fields with whitespace inside the name.
  * In **Data collection** , changed message that informs user of invalid or disabled rules. 
  * In **Webforms** , created multiple tabs representing the same tables for Entity type webforms.
  * In **Enabling/Disabling editing** , made changes to ensure that tables are converted successfully and no data loss is possible.



[Edit this section](Reportnet_3_Changelog/edit.md)

## Sprint 95 - deployed (Dec 11th 2025)

  * In **Validation** , for Citus SQL expressions, limited number of errors to 1001 per QC. If this number is reached, the user is shown the validation code with 1000+ records in Show validations.
  * In **Validation** , if a field name contains whitespace, a notification is sent to inform the user of the invalid character.
  * In **Import** , for non big data dataflows, if the imported zip does not contain correctly named csv files, a notification is sent to the user.
  * In **Field updates** for links, if the field's description is updated, the conditional and label attributes of the link are not modified.
  * In **Web links** if a link contains encoded characters, they are not removed and the link is redirecting to the correct URL.
  * In **Data collection** the record comparison tool shows the providers ordered alphabetically.
  * In **Export definition** a notification is sent to the user after the export is completed.
  * In **Webforms** , if a link is changed, the conditional values are cleared so that the user can select the new values.
  * In **Webforms** , a view mode has been introduced, so that the user can view the data and their structure even if editing is not enabled.
  * In **Upgrades** , several libraries have been upgraded to newer versions.
  * In **Export data** , using filtering with spatial data fields, correctly exports the filtered records.



[Edit this section](Reportnet_3_Changelog/edit.md)

## SC6/SR3 - deployed (Sep 23rd 2025)

  * In **Validation** , Table type validations will have the ability to show dynamic values from query instead of <column name> ([#282450](/issues/282450 "Bug: Table type validations showing variable name instead of value \(Closed\)"))
  * In **Validation** , at the beginning of the process will check for non existing tables and will create empty ones before it starts in order to execute all queries without canceling ([#282450](/issues/282450 "Bug: Table type validations showing variable name instead of value \(Closed\)"))
  * In **Historic releases** , added the ability to download the releases in CSV 
  * In **Jobs monitoring** , simplified notifications and wording in messages (eg. Iceberg messages replaced with Dataset in Editing mode, Please disable editing) 
  * In **Public info** , the columns for each country will include First delivery, Last delivery and Delivery status 
  * In **Webforms** , Entities webforms in Datalakes have the ability to define custom keys for the root table (Auto increment or Supplied at data entry/import)
  * In **QC rules** , the ability to define default QC rules severity is added



[Edit this section](Reportnet_3_Changelog/edit.md)

## Sprint 93 - deployed (Sep 23rd 2025)

  * In **Import** , fixed a NegativeArray Exception with Multipart file upload in BigData dataflows /dataset/v2/importFileData/ (mostly used by FME to upload data to Repornet3)
  * In **Validation** , there is a chance processes created for Jobs are not set IN_PROGRESS when DB is under heavy load. The Validation will be cancelled after 3 hours. A new Scheduled task in the Orchestrator finds them and puts them IN_PROGRESS every 10 mins.
  * In **API** , The Api calls below have been updated for use by Lead Reporters

Api call  | Scope   
---|---  
get: /weblink/v1/dataflow/{dataflowId}  |  Retrieves all weblinks by dataflow id   
get: /weblink/dataflow/{dataflowId}  |  Retrieves all weblinks by dataflow id (Legacy)   
get: /datasetmetabase/dataflow/{dataflowId}  |  Retrieves all reporting datasets that belong to a dataflow   
get: /document/v1/{documentId}/dataflow/{dataflowId}  |  Retrieves document   
get: /document/{documentId}/dataflow/{dataflowId}  |  Retrieves document (Legacy)   
  
  * In **Help** , <https://help.reportnet.europa.eu> with become public in September 
  * In **Validation** , changed the priorities based on how close the delivery is to the deadline. The steps are:

Date range  | Priority   
---|---  
Deadline is more than 90 days away  |  60   
Deadline is between 60–90 days away  |  50   
Deadline is between 30–60 days away  |  40   
Deadline is between 7–30 days away  |  30   
Deadline is within 7 days  |  20 (highest)   
Deadline has passed within 7 days  |  20 (highest)   
Deadline has passed between 7–30 days  |  30   
Deadline has passed between 30–60 days  |  40   
Deadline has passed between 60–90 days  |  50   
Deadline has passed more than 90 days away  |  60   
  
  * In **Release** , cancelled releases will have their snapshot records (historic releases) rolled back 
  * In **Import** , imports for reference datasets are now documented in <https://taskman.eionet.europa.eu/projects/reportnet-3/wiki/Import_Reference_Datasets>
  * In **Export** , all versions of ETL exports are now documented in the attached document <https://taskman.eionet.europa.eu/attachments/352685>
  * In **UI - > Tabular Data**, a fix was implemented to encode characters, ensuring that special characters such as “+” and “&” are correctly passed to the backend.



[Edit this section](Reportnet_3_Changelog/edit.md)

## Sprint 92 - deployed (Sep 23rd 2025)

  * In **Design mode** , table schema changes are not allowed while editing data.
  * In **Rod** (Reportnet 2), taking into account only the existing obligation fields for history entries.
  * In **Webforms** , conditional fields inside blocks are now working properly. 
  * In **Big Data** dataflows, field name with spaces are not allowed in design. 
  * In **Spatial Data** fields, field size is limited to 70MB. The notification message is:  

[code]     For {tableName} , and field : {fieldName} , those lines have not been imported due to size limitation of the geoSpatial data field : {lineNumber}
    
[/code]



  * In **Notification** , export messages are change as follows

Old message | New message  
---|---  
External design export init  |  Export dataset data initiated   
QC rules file generated successfully  |  QC rules download completed successfully   
Schemas information file generated successfully  |  Schemas information download completed successfully   
Users list file generated successfully  |  Users list download completed successfully   
Validations file generated successfully  |  Validations download completed successfully   
Export file generated successfully  |  Export dataset data completed successfully   
QC rules file generated successfully  |  QC rules export completed successfully   
Schemas info file generated successfully  |  Schemas information export completed successfully   
Export file generated successfully  |  Export table data completed successfully   
Users list file generated successfully  |  Users list export completed successfully   
External design export file generated successfully  |  External dataset export completed successfully   
External reporting export file generated successfully  |  External reporting dataset export completed successfully   
  
  * In **API** , new statistics endpoint for jobs <https://sandbox-api.reportnet.europa.eu/orchestrator/jobs/statistics>


[code] 
    {"days": [
      {
        "data": {
          "validationJobs": 20,
          "canceledByAdminJobs": 0,
          "totalJobs": 78,
          "deleteJobs": 4,
          "finishedJobs": 56,
          "releaseJobs": 3,
          "refusedJobs": 3,
          "importJobs": 45,
          "queuedJobs": 0,
          "failedJobs": 17,
          "exportJobs": 6,
          "inProgressJobs": 0,
          "canceledJobs": 2
        },
        "day": "2025-9-10" 
      },
      {
        "data": {
          "validationJobs": 16,
          "canceledByAdminJobs": 0,
          "totalJobs": 48,
          "deleteJobs": 6,
          "finishedJobs": 37,
          "releaseJobs": 0,
          "refusedJobs": 0,
          "importJobs": 26,
          "queuedJobs": 0,
          "failedJobs": 4,
          "exportJobs": 0,
          "inProgressJobs": 0,
          "canceledJobs": 7
        },
        "day": "2025-9-9" 
      }
    ]}
    
[/code]

  * In **Import** , .db3 files are allowed 
  * In **Validation** , new column added (Rule Id). Old validations ignore the column for backwards compatibility

## Verification notes

No source code verification applicable — this is a running changelog maintained by the team. The most recent entries (Sprint 104, May 2026) appear current. From December 2025 the team also publishes public-facing release notes at help.reportnet.europa.eu; the two sources may diverge over time and should be cross-checked periodically.
