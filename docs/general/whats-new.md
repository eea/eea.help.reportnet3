---
title: "What’s new"
source_url: https://help.reportnet.europa.eu/general/whats-new/
---

# What’s new
The EEA Reportnet team is maintaining this platform on a constant basis. We have monthly sprints (Agile development) that aims in fixing bugs and provide new features. Technology and user demand is constantly changing. Here you get to see some insights of what is changed and the new features we have introduced. We show this to you in reverse order.

##

* * *

## ✅ Fixes & Clarifications (July 2026)

In July, we focused on improving data validation stability, webform behavior, and file export reliability.

  * **Validation** stability improved: In **Validations** , random false positive errors during execution have been eliminated by isolating processing tasks.
  * Missing permission **blockers** : In **Validations** , a failure to record blocking errors due to missing user permissions now properly fails the validation job to prevent invalid data release.
  * Entity dropdowns refresh correctly: In **Webforms** , switching between entities now correctly and immediately updates all dependent dropdown values.
  * Attachment deletion in webforms: In **Webforms** , deleting uploaded attachments inside Tables webforms now works flawlessly for both newly added and already saved files.
  * **GeoJSON** download fix: In Export data, downloading single GeoJSON files now works correctly without triggering a system error.
  * Spinner behavior corrected: In **Data Collections** , stopping a data collection correctly halts the loading spinner instead of leaving it active on the screen.
  * Attachment size limits displayed: In **Dataset Schema** , the maximum file size limit for attachment fields is now preserved and displayed correctly.
  * **SQL** queries in **QC rules** that contain unsupported syntax like ; characters are now marked as erroneous and are rejected.
  * When a release fails, the status of the involved datasets is reset back to **PENDING**.

## 🚀 Features & Enhancements (July 2026)

We delivered updates focusing on API integrations, webform usability, and validation speed.

  * **Preparation datasets** have been deployed but are disabled for all dataflows. We will deploy a hotfix that allows custodians to enable them for specific dataflows.
  * Expandable webform sections: In **Webforms** , designers can now add collapsible sections to hide or show large groups of questions, significantly reducing visual clutter on long forms.
  * **FME** preparation support: In **Import API** , FME integrations can now directly target preparation datasets using a new specific parameter.
  * Optimized validation execution: In **Validations** , critical structural rules now run first and instantly stop the process if blockers are found, speeding up the validation feedback loop.

## ✅ Fixes & Clarifications (June 2026)

During June, we resolved a number of problems affecting how releases and spatial data behaved across the system.

  * Release process reliability: In **Release** , duplicate task creation issues have been resolved, and release jobs now queue properly.
  * Preparation dataset locking: In **Preparation datasets** , validating data no longer incorrectly locks the parent dataset, allowing uninterrupted work.
  * Validation results isolation: In**Preparation datasets** , validation results now display exclusively for the preparation set without affecting the parent view.
  * Invalid geospatial data handling: In **Import data** , invalid geometry values are now gracefully converted to empty values, and a clear warning is added to the job monitor.

## 🚀 Features & Enhancements (June 2026)

We also delivered features to handle spatial rules dynamically.

  * Mutable **spatial rules** : In **QC rules** , automatic validation rules for spatial data now automatically adapt and regenerate whenever table or field names are modified.

## ✅ Fixes & Clarifications (May 2026)

In May, we focused on UI performance and addressing historical data management issues.

  * **Sorting** on large tables: In **Data viewing** , sorting columns in Big Data collections now works correctly for all field types.
  * Faster tab switching: In **Datasets** , load times and switching speeds have been significantly improved for datasets containing a large number of tabs.
  * **Historic release dates editable** : In **Historic Releases** , administrators can now safely edit release dates even if the original job ID is missing.
  * **Attachment** uploads in **Transport** : In **Webforms** , the attachment field issue in the Transport platform has been permanently fixed, removing the need for manual workarounds.

## 🚀 Features & Enhancements (May 2026)

We added several improvements to make data management and monitoring more intuitive for reporters.

  * **Preparation dataset deletion** : In Preparation datasets, reporters can now seamlessly delete specific table data or the entire preparation dataset.
  * Automatic **12-hour editing timeout** : In Editing of Data, the system will now automatically disable editing 12 hours after it is enabled to prevent unintentional locks. A warning message informs the user when editing begins.
  * **Cancelled validation visibility** : In **Job Monitoring** for the Transport platform, release jobs blocked by cancelled validation tasks now feature an info button that displays the exact cancelled validations.

## ✅ Fixes & Clarifications (April 2026)

In April, we focused on improving processes in Validation, Release as well as User Interface fixes.

  * In **Data Collections** , release process reliability has been improved to prevent **duplicate** or **missing** tasks.
  * In **Validations** , **QC rules** containing unsupported SQL syntax char “;” are now marked as invalid and blocked from execution, with an error message displayed to the user.
  * Fixed the right-click tab context menu in **Webforms** to position correctly regardless of scroll position.
  * Fixed middle-clicking on Data Collection and EU Dataset icons to correctly open them in a new browser tab.
  * In **Validations** , the **automatic email format** check has been fixed to correctly accept email addresses with long domain extensions.

## 🚀 Features & Enhancements (April 2026)

We delivered tasks, including enhancements in Validation, Webform editing, geospatial data and User Interface additions.

  * In **Validations** , icon shown on Dataset table tabs displays the appropriate warning indication, instead of the error icon – for only warnings after validation.
  * In **Validations** , historical validation results are now stored per snapshot, and a new endpoint allows downloading results for a specific release by snapshot ID.
  * In **Validations** , multi conditional link validations are now possible through the reference table.
  * In Datasets, the “**Delete dataset data** ” button is visually enhanced to reduce the risk of accidental deletion.
  * Extended provider-based macro replacement to **Field Comparison** validation rules, enabling data provider codes to be substituted before query execution.
  * In **Webforms** , editing is now automatically disabled when the lead reporter who enabled it is removed from a dataflow, preventing editing from becoming
permanently locked.
  * In **Dataflows** , test dataflows are protected from being available public with the introduction of a new “**is Official Reporting** ” attribute.
  * In **Dataflows** , the **delivery receipt** has been updated: the standard acceptance text is now pre-populated and editable, the receipt text and date label have been
corrected, and the dataflow link has been added below the title.
  * In **Datasets** , retrieval and rendering of large **geospatial data** has been optimized: geometry values are no longer loaded upfront but fetched on demand,
preventing browser crashes on datasets with large polygon data.

## ✅ Fixes & Clarifications (March 2026)

In March, we focused on improving system stability and performance.

  * Improved the rearranging of tabs functionality in the **Dataset View page** , ensuring stability of the changes.
  * Fixed a bug in QC rules where a trailing single-line comment (`--`) was causing an unnecessary warning.
  * Adjusted **Release job** s so that they start with status **Queued** instead of **In Progress**.
  * In public countries View, **Moldova** was added to the **Cooperating Countries**.
  * Implemented alphabetical sorting of datasets in the **Provider’s View**.

## 🚀 Features & Enhancements (March 2026)

We also introduced new functionalities in Preparation datasets and Big Data dataflow handling.

  * Added export functionality in **Preparation datasets**.
  * Added validation functionality in **Preparation datasets**.
  * Added an optional preparationDataset parameter in **FME calls**.
  * In **Dataset Design** for Big Data dataflows, disabled certain schema modification actions when a table already contains data.

## ✅ Fixes & Clarifications (February 2026)

In February, we focused on clarifications and fixes across spatial data validation imporvement, imports, validation and SNC data:

  * **Geometry validation** **improvement** : In Validation, blank geometries are handled to prevent validation tasks from being canceled.
  * **Import data improvement** : In Import Data memory handling has been improved to prevent pod restarts during large imports.
  * **Validations running in parallel** : In Validations, execution has been modified so that validations without release jobs can run in parallel.
  * **Enhanced security in dataflows:** In Business Dataflows, Sensitive Non Classified (SNC) data are treated as business data and additional safeguards prevent accidental exposure or insecure processing.
  * **Import without unlocking** : In Import Data, attachments can be uploaded via the RN3 API without requiring the dataset to be manually unlocked.
  * **Dataflows limits:** In Dataflows, limits have been enforced on the number of schemas, tables and fields.
  * **Dataflows creation improvements** : In Big Data dataflows, unnecessary Citus schema creation has been removed improving the create data collection functionality.

## 🚀 Features & Enhancements (February 2026)

We delivered the addition of Preparation Datasets, and improvements regarding User Interface, Validation, Security and Webforms.

  * **Introduction of Preparation Datasets:** In Data Collections, preparation set datasets can now be created and viewed through the User Interface.
  * **Preparation Datasets management by lead reporters:** In Data Collections, a lead reporter can create and manage preparation sets from the provider page.
  * **Retrieval of preparation datasets** : In Data Collections, a new endpoint retrieves all preparation dataset names and codes.
  * **Deletion of preparation datasets:** In Data Collections, delete preparation set functionality has been implemented.
  * **Import in preparation datasets** : In Preparation datasets, import functionality has been added, including processing and parquet table creation.
  * **Webforms styling improvement** : In Webforms, block alignment behaviour has been improved for increased readability.
  * **Webform configuration enhancement** : In Webforms, searching and sorting have been added to the Configure Webform dialog.
  * **Supporting Documents enhancement:** In Dataflows, supporting document attachments download improved functionality.
  * **Silent Releases filter addition:** In Job Monitoring, silent releases are visible with a dedicated icon.
  * **Custodian acting as a Provider for Validation** : In Design and Test datasets, a custodian can act as a validation provider and set the provider code during validation.
  * **MongoDB upgrade:** In Security, MongoDB has been upgraded for increased security.
  * **Java libraries upgrade** : In Security, Java libraries have been upgraded in Reportnet 3 services for increased security.

## ✅ Fixes & Clarifications (January 2026)

In January, we focused on clarifications and fixes across spatial data handling, imports, validation, job monitoring, business dataflows, and public views:

  * **Spatial data value display adjusted** : In Spatial Data, GeoJSON values are no longer displayed directly in the UI. Instead, an INFO button is shown, allowing users to download the value.
  * **Header-only imports notification** : In Import Data for Citus dataflows, if an imported file contains only headers, a notification is sent to the user.
  * **Attachment size limits applied** : In Import Data, adding attachments larger than 2GB for Citus dataflows or 10GB for Big Data dataflows are prevented in the UI.
  * **Export permissions extended** : In Export Data, observers of a dataflow can export data in the same way as custodians.
  * **Business dataflow classification clarified** : In Business Dataflows, Big Data dataflows are considered SNC.
  * **National coordinator permissions clarified** : In Business Dataflows, national coordinator permissions are not created.
  * **QC rule parsing corrected** : In QC rules, custom SQL rules that contain a trailing comment are marked as not valid.
  * **Correction request date shown** : In Public Dataflows, the date of the correction request is displayed.
  * **Job type filter completed** : In Jobs monitoring, ETL IMPORT job added in the job type filter.
  * **Record comparison default updated** : In Data collection, in the number of records comparison tool, the default country filter has been changed to the first country in the list.
  * **Concurrent editing restricted** : In Editing of Data, only one user can edit tabular data or a webform within a dataset at a time.
  * **Geometry validation feedback improved** : In Validation, if a geometry is invalid, the reason is shown to the user.
  * **QC terminology updated** : In QC rules, Level Error has been renamed to Severity Level.
  * **Automated QC rules reduced** : In QC rules, for Big Data dataflows that contain spatial data fields, the unnecessary automated rules used in Citus dataflows have been removed.
  * **Public country information completed** : In Public Dataflows Country Page, technical status and date are now shown.

* * *

## 🚀 Features & Enhancements (January 2026)

We also delivered improvements across documentation, user interface, job monitoring, validation, and dataset management:

  * **Documentation access updated** : In the Front Page, a link to the documentation site is shown instead of the supporting documents.
  * **Editing limitations documented** : In Documentation, the limitation that only one user can edit data at a time has been documented.
  * **Historic release date editing documented** : In Documentation, the tool for Admins and Custodians to edit historic release dates has been documented.
  * **Dark theme enhancements applied** : In UI, improvements to the dark theme have been implemented.
  * **Data collection creation optimized** : In Data collection creation, fixes have been applied to reduce complexity and creation time.
  * **Snapshots extended** : In Snapshots, snapshots are now available for Design and Test datasets.
  * **Job cancellation expanded** : In Job monitoring, all job types can be canceled.
  * **Validation error limits aligned** : In Validation, for Big Data expressions, Citus expressions, and automated rules, the job calculates up to 1001 errors per QC.
  * **Public country status visibility improved** : In Public Dataflows Country Page, technical status information is shown.

* * *

## ✅ Fixes & Clarifications (November 2025)

In November, we focused on improving system reliability, data integrity, and validation correctness by addressing issues in jobs monitoring, QC rules, imports, links, and exports::

  * **Admin job visibility corrected** : In Jobs Monitoring, users that are both admins and lead reporters can view all jobs due to the admin role.
  * **R3_COUNTRY_CODE rule execution fixed** : In QC rules, running a single SQL rule or evaluating it when the rule contains variable R3_COUNTRY_CODE is now working correctly.
  * **Missing metadata load errors reduced** : In Data retrieval, minimized errors when loading data that were caused due to missing metadata.
  * **Table schema deletion cleans data** : In Table Schema deletion, data of the table are removed as well.
  * **Old provider attachments removed on release** : In Release with attachments, old attachments of provider are now removed from the data collection.
  * **Default severity button removed post-collection** : In QC rules, removed the Default severity button for design datasets after the creation of the data collection.
  * **Invalid field names (whitespace) prevented** : In Dataset schema design, removed the option for a user to add fields with whitespace inside the name.
  * **Editing enable/disable conversions stabilized** : In Enabling/Disabling editing, made changes to ensure that tables are converted successfully and no data loss is possible.
  * **Whitespace in field names now flagged** : In Validation, if a field name contains whitespace, a notification is sent to inform the user of the invalid character.
  * **Invalid import ZIP structure notified** : In Import, for non big data dataflows, if the imported zip does not contain correctly named csv files, a notification is sent to the user.
  * **Link field updates preserve behavior** : In Field updates for links, if the field’s description is updated, the conditional and label attributes of the link are not modified.
  * **Encoded URLs kept intact in web links** : In Web links if a link contains encoded characters, they are not removed and the link is redirecting to the correct URL.
  * **Link changes reset conditional values** : In Webforms, if a link is changed, the conditional values are cleared so that the user can select the new values.
  * **Spatial filters export correctly** : In Export data, using filtering with spatial data fields, correctly exports the filtered records.

* * *

## 🚀 Features & Enhancements (November 2025)

We also delivered features on enhancing usability, configurability, and data access across documentation, webforms, exports, and validation workflows::

  * **Notification texts improved** : In Notifications, updated notification messages to be more user friendly and containing action items for the user.
  * **Duplicate entity check performance** : In Webforms, checking for duplicate entity ID is now faster.
  * **Date-time picker clear option** : In Webforms, changed date time component so that it contains a clear button.
  * **Docs – cancelled validations & geospatial**: In Documentation, documented cancelled validation tasks and geospatial data.
  * **Multiline text length safeguard** : In Import, if a field is multiline text and it contains more than 10000 characters, a warning notification is sent to the user and the value is not stored.
  * **Silent release for admins** : In Release, provided admins with a silent release button in order to release provider’s data without any notifications or mails being sent. The release dates are also not updated.
  * **Editable historic release dates** : In Historic Releases, provided admins and custodians of a dataflow with edit buttons for the historic release dates, in order to be able to edit them.
  * **API & notifications documentation extended**: In Documentation, documented export API features, validation API, import API, polling for job status API, how to manage records for big data, dataset schema export process and all user notification messages.
  * **ETL export by provider code** : In Etl export v4 (zip with csv files) and v5 (zip with parquet files) added parameter for data provider codes in order to retrieve data for some providers from the data collection or the EU dataset.
  * **Imported files overview & download**: In Imported files, added a button and window to list imported files in a dataset and a download button for each file.
  * **Table cell alignment improved** : In Data viewing, changed vertical alignment of values in table cells to top.
  * **Release failure notification on active editing** : In Release, added failure notification if editing has been enabled for a dataset of the provider.
  * **Big data QC error cap** : In Validation, in Big data dataflows for automated QCs and SQL expressions limited number of errors to 1001 per QC. If this number is reached, the user is shown the validation code with 1000+ records in Show validations.
  * **Clearer invalid/disabled rules message** : In Data collection, changed message that informs user of invalid or disabled rules.
  * **Entity webforms multi-tab layout** : In Webforms, created multiple tabs representing the same tables for Entity type webforms.
  * **Citus QC error cap** : In Validation, for Citus SQL expressions, limited number of errors to 1001 per QC. If this number is reached, the user is shown the validation code with 1000+ records in Show validations.
  * **Record comparison provider ordering** : In Data collection the record comparison tool shows the providers ordered alphabetically.
  * **Export completion notification** : In Export definition a notification is sent to the user after the export is completed.
  * **Webforms read-only view mode** : In Webforms, a view mode has been introduced, so that the user can view the data and their structure even if editing is not enabled.
  * **Library upgrades** : In Upgrades, several libraries have been upgraded to newer versions.

* * *

## ✅ Fixes & Clarifications (September 2025)

In September, we focused on improving system reliability, validation stability, and user experience across several modules:

  * **Import reliability improved:** Fixed issues that caused import errors (e.g. negative array exceptions) when uploading large or multipart files, ensuring smoother uploads from tools like FME.
  * **Stable validation processing:** Resolved cases where validation jobs were stuck or incorrectly marked as cancelled under heavy database load. A new monitoring task now ensures all validations resume correctly.
  * **Webform consistency:** Conditional fields inside form blocks now behave correctly. Fields with spaces in Big Data dataflows are no longer allowed, preventing schema and mapping errors.
  * **Data editing safeguards:** Table schema changes are now blocked while users are editing data, avoiding accidental data loss or inconsistencies.
  * **Character encoding fixed:** Special characters such as “+” and “&” are now handled correctly when editing or exporting tabular data.
  * **Historic release reliability:** Cancelled releases now correctly roll back their associated historic records, ensuring data integrity.
  * **Spatial data handling improved:** Large geospatial fields (over 70MB) are now automatically excluded with clear notifications, avoiding failed imports.
  * **Messaging clarity improved:** Job notifications and export messages were standardized to use clearer, more consistent wording across modules.

* * *

## 🚀 Features & Enhancements (September 2025)

We also delivered several new capabilities and usability improvements in this release:

  * **Smarter validation logic:**
    * Table-type validations can now display dynamic values directly from queries instead of static column names.
    * The validation process automatically creates missing tables before execution, reducing errors and cancellations.
    * Validation priorities are now dynamically adjusted based on how close a delivery is to its deadline — ensuring urgent datasets are validated first.
  * **Historic releases export:** Users can now download historic releases in CSV format for easier review and reuse.
  * **Jobs monitoring improvements:** Simplified messages and notifications make it easier to understand job status and causes of blocking (e.g. datasets still in editing mode).
  * **Public information view enhanced:** The country overview now includes _First delivery_ , _Last delivery_ , and _Delivery status_ columns for quicker status checks.
  * **Custom webform keys:** Entity webforms in Datalake datasets can now define custom primary keys (auto-incremented or user-supplied), providing more flexibility for data integration.
  * **Default QC rule severity:** Designers can now define a default severity level for QC rules, improving rule consistency across datasets.
  * **API improvements:** Several endpoints were updated for Lead Reporters, and a new statistics endpoint now provides summary data on job activity.
  * **Documentation and help updates:**
    * The official help portal ([help.reportnet.europa.eu](index.md)) is publicly available.
    * Reference dataset imports and ETL export versions are now fully documented in Taskman for transparency and traceability.

* * *

### ✅ Fixes & Clarifications (June 2025)

During June, we resolved a number of problems affecting how data could be viewed, edited, validated, or released across various datasets and countries. These fixes improved overall system reliability and user experience.

  * **Improved Connection Stability** : We solved an SSL connection issue that prevented our services from accessing key data sources (like Dremio). All environments are now fully operational.
  * **Quick Resolution of Service Downtime** : A temporary issue in our database service caused several data loading failures and access problems for multiple countries (e.g. Cyprus, Italy, Bulgaria). These were identified and resolved quickly.
  * **Release & Submission Problems Solved**: Many reporters faced cancelled or stuck data releases. These were caused either by system hiccups or by editing modes being active during release. We helped unlock these situations and guided users to retry successfully.
  * **Validation and Blockers Explained** : Several countries reported issues with validation not showing results or being stuck. In most cases, incorrect configurations or outdated data caused the problems. We helped users identify and fix their queries or retry after short delays.
  * **Disappearing or Locked Data** : Some users found their data missing or inaccessible after edits. We investigated and clarified that these were caused either by overlapping actions (like editing while importing) or due to misunderstandings of the platform’s autosave behavior.
  * **Clarified Data Access Rights** : Some issues around missing or incorrect country access were cleaned up, ensuring each country sees only their relevant datasets.
  * **Validation Time Improvements** : We addressed complaints about slow validations, especially for smaller tables, and introduced improvements to job monitoring and clearer user guidance.

* * *

### 🚀 Features & Enhancements (June 2025)

We also added several improvements to make the system more intuitive and responsive for both reporters and administrators:

  * **Enhanced Error Messages** : We made validation error messages more informative and easier to interpret. If validations are cancelled or something goes wrong, users now receive clearer guidance.
  * **Faster Imports/Exports for Big Files** : For large datasets—especially spatial or multipolygon files—we changed how files are handled to avoid memory issues and improve performance.
  * **Improved Webform Behaviors** : Many small bugs in dropdowns, form refreshes, and editing processes were fixed to improve the flow of entering and saving data.
  * **Automatic Cleanups** : We introduced tasks that clean up old locks and stuck processes, helping keep the platform smooth without manual intervention.
  * **Silent Releases and Recovery Help** : We supported several silent releases when needed and provided reminders and documentation on best practices for backing up and restoring data to avoid accidental overwrites.
  * **Admin Access Simplified** : We fixed issues where admins couldn’t navigate design tabs unless they were custodians, restoring full access as intended.
  * **New Export Options** : A new export version (v5) was launched, allowing the download of full datasets including attachments in a more consistent format.

* * *

### ✅ Fixes & Clarifications (May 2025)

In May, we continued to improve the stability of the platform and fix recurring problems reported by users:

  * **Dropdown and linked field issues were fixed** : Problems where dropdowns showed no values or failed to update when linked to another field were corrected.
  * **Record editing and saving bugs were resolved** : Users who encountered problems saving edited records, especially when using special characters like “&” or quotation marks, can now proceed without errors. Errors caused by overly strict validations or characters in field values (like `%`) were also fixed.
  * **Validation error messages were improved** : Users now see clearer and more helpful messages when validations fail. Some incorrect validations (e.g. on scientific notation or zero values) were corrected.
  * **File upload and dataset structure corrections** : Bugs related to importing and exporting CSV, XML, and JSON files were resolved, especially for shapefiles and dataflows like DWD and MSFD. Archive generation (ZIP files) is now more reliable, producing correctly named and structured outputs.
  * **Clarity in empty or optional values** : The platform now handles optional fields and empty values more gracefully, avoiding false validation errors.

* * *

### 🚀 Features & Enhancements (May 2025)

Several updates were made to enhance functionality and prepare the platform for more complex dataflows:

  * **Advanced field logic was added** : Support for “conditionally required” fields and default values based on linked fields was introduced, helping form designers offer more guided input for users.
  * **Improved geometry validation** : The platform now offers better support for spatial data types, especially in datasets where locations or shapes (geometries) are important.
  * **Better multi-table support** : Users working with datasets that include multiple linked tables (e.g., MSFD, WFD) now experience smoother linking and copying across records.
  * **Support for new dataflows** : Behind the scenes, updates were made to support the rollout of new and revised reporting flows such as WFD2025 v2 and updated MSFD obligations.
  * **Performance improvements for large datasets** : The system now handles larger data uploads and form interactions more efficiently, reducing timeouts and improving overall speed.
  * **Feedback from reporters was incorporated** : Usability fixes and workflow tweaks were applied based on direct feedback from Member States and helpdesk support, particularly around webform layout and validation flow.

* * *

### ✅ Fixes & Clarifications (April 2025)

April focused on resolving form-related issues and improving data validation processes:

  * **Form usability was improved** : Missing dropdown values, blank selection lists, or dropdowns that didn’t update correctly were fixed. Several problems with adding, editing, or deleting records—especially in forms like DWD and WFD—were resolved, ensuring smoother workflows.
  * **Validation feedback was improved** : Misleading or overly technical validation messages were clarified, helping users better understand what needs fixing. Problems where blank or optional fields were incorrectly flagged were corrected.
  * **Field behavior was corrected** : Issues with dependent fields (e.g., fields that appear or change based on a previous answer) were fixed to behave more consistently.
  * **ZIP and file structure fixes** : The export and archive structure of datasets was corrected to produce properly named and bundled ZIP files. Previously reported bugs with XML, CSV, or JSON formatting in exports were resolved.
  * **Copying and mapping between dataflows was stabilized** : Datasets copied from older reporting years or between flows now maintain their internal structure and links correctly.

* * *

### 🚀 Features & Enhancements (April 2025)

Several enhancements were rolled out to improve data handling and prepare for upcoming dataflows:

  * **More flexible webform design** : Designers can now define default values, mark fields as conditionally required, and link dropdowns more effectively—particularly useful in flows like WFD2025v2 and MSFD.
  * **Improved validation control** : Administrators can apply fine-tuned rules for how data is validated, allowing better pre-submission checks and fewer errors during final validation.
  * **Performance improvements** : Large datasets, including those with hundreds of records or multiple tables, now load and save more quickly in webforms.
  * **User feedback implemented** : Enhancements were made based on real feedback from Member States, especially regarding dropdown clarity, geometry handling, and form layout.
  * **Support for upcoming reporting flows** : The platform was updated to support more advanced logic and field configurations needed in new dataflows like WFD2025v2, DWD updates, and others scheduled later in the year.

* * *

### ✅ Fixes & Clarifications (March 2025)

In March, we resolved several recurring issues to improve system stability and usability:

  * **Broken or frozen webforms were fixed** : Users who experienced freezing or loading errors when accessing or editing records in WISE and Water-related forms (WISE6, WFD) can now proceed without interruption.
  * **Validation errors were corrected** : Several cases where correct data triggered false validation errors—like misinterpreting large numeric values or handling empty geometry data—were fixed.
  * **Improved handling of data updates and deletions** : Deleting records or datasets now works as expected, without triggering duplicate jobs or errors. Editing large datasets (over 250 records) was stabilized to avoid timeouts and freezes.
  * **Issues with linked datafields and dropdowns were resolved** : Dependencies between fields now behave correctly, especially in cases where multiple dropdowns or value filters are involved.
  * **Better copy and reuse support for dataflows** : Copying old submissions into new dataflows now preserves relationships between tables and fields, avoiding data mismatches or incomplete imports.
  * **Clarified confusing messages** : Several backend and frontend error messages were rewritten or removed to give users clearer feedback during submission, validation, and form editing.
  * **Dropdown fields now behave correctly** : Problems with dropdowns not showing values, being blank, or showing inconsistent options were fixed. This affected webforms in several reporting flows, including Water and WFD datasets.
  * **Record editing became more stable** : Issues where users couldn’t add or edit records due to missing values or system freezes were resolved. Unresponsive “save” buttons or disappearing fields were fixed, especially in cases with required fields or long linked forms.
  * **Validation messages and warnings were clarified** : Unhelpful messages or incorrectly triggered warnings during data submission were rewritten or removed. Empty mandatory values that previously caused confusion were handled more gracefully.
  * **Copy and reuse of previous submissions** : Copying data from previous years or countries now works better, keeping all necessary links between fields and tables intact.
  * **Bug in ZIP file generation for exports was fixed** : Exported files are now properly named and structured, avoiding confusion when downloading or re-uploading.

* * *

### 🚀 Features & Enhancements (March 2025)

We also rolled out several improvements to streamline workflows and improve the experience:

  * **Better performance on large datasets** : Webforms and validation processes now perform more reliably with high-volume data and complex structures (e.g. marine or water-related datasets).
  * **More flexible validation support** : Scientific notation and empty values are now better supported in numeric fields. Enhanced checks for geometries and encoding in shapefiles and CSVs improve import reliability.
  * **Support for new field types and logic** : Linked fields, default values, and new validation rules were introduced to accommodate more advanced dataflows (e.g., WFD2025, DWD, etc.).
  * **Admin and developer tools were expanded** : Monitoring tools for job queues were improved to identify long-running or stuck processes. New backend features make it easier to preview changes before deploying new dataflows.
  * **Improved file export and archive handling** : Exported ZIP and CSV files are now more consistent and reliable, including improved naming and bundling of multiple files.
  * **Preparation for the next reporting cycle** : The platform was updated to support upcoming datasets and new versions of reporting flows (e.g., WFD2025v2, MSFD updates). Testing and feedback from data providers were incorporated to shape the upcoming interface and logic.
  * **Performance improvements for complex forms** : Webforms with many linked fields now load faster and are more stable, particularly in water-related flows like WFD2025.
  * **New validation options and logic** : Dataflow designers can now apply stricter rules or link validation between fields more easily, allowing more control over what gets submitted. Linked dropdowns and conditionally required fields work better with complex configurations.
  * **Improved handling of optional fields and default values** : Fields that are optional now behave more consistently, and default values appear where they should.
  * **Updates to support newer dataflows** : The platform was enhanced to accommodate new and revised dataflows such as WFD2025 v2 and DWD with new mapping logic, linked dropdowns, and default configurations.
  * **Feedback from reporters was acted on** : Several usability improvements came directly from comments made by Member States during testing or helpdesk contacts.

* * *

### ✅ Fixes & Clarifications (February 2025)

In February, we tackled a number of issues reported by users and system testers:

  * **Missing records or invisible data in webforms** were fixed. In some cases, datasets didn’t show up after being uploaded or copied. This was corrected to ensure records appear immediately and accurately.
  * **Problems when adding or editing records** were resolved. These included dropdown menus not working, data not saving, or extra characters appearing in validation messages. Users can now interact with forms smoothly.
  * **Validation errors were clarified and corrected**. Some datasets were incorrectly marked as invalid (e.g. when using scientific notation or empty values). We updated the validation process to handle these cases properly.
  * **Dataflow behavior was improved for copy and reuse** : When copying datasets from one country or year to another, problems with internal IDs and automatic submissions were fixed to ensure data can be reused easily.
  * **File uploads and schema validations** were repaired. Issues with JSON and XML file checks that prevented users from uploading valid data were addressed.
  * **System notifications and logs were improved** , so administrators could more easily see what went wrong when errors occurred during submissions or updates.

* * *

### 🚀 Features & Enhancements (February 2025)

Several enhancements were made to improve functionality and user experience:

  * **Webforms were made more responsive** : They now handle large files and long records better, with improved dropdown behavior and faster load times.
  * **Support for more file types and validation rules** : New types of encoding and geometry formats were added to support a wider range of user needs.
  * **Job monitoring improvements** : Background processes such as data deletion or form generation now show their status more clearly and are easier for admins to manage.
  * **Clarified system messages** : Many error and validation messages were rewritten or simplified to make it clearer to users what actions they need to take.
  * **Better default settings and help texts** : For example, datasets now default to a neutral state where nothing is selected, helping avoid accidental submissions.
  * **Preparation for bigger changes ahead** : Several background tasks laid the foundation for new dataflow versions, advanced validation rules, and richer data mapping features in upcoming months.

* * *

### ✅ Fixes & Clarifications (January 2025)

Throughout January, we addressed a wide range of issues to ensure the system remained stable and user-friendly:

  * **Stuck or blocked processes were resolved quickly** to avoid delays. This included fixing issues where users couldn’t import data, save records, release datasets, or add representatives. These were mostly caused by internal system locks or timeouts and were removed promptly.
  * **Performance issues were investigated**. For example, a slow and unstable experience with WISE 6 data access was looked into and optimized by reducing unnecessary access permissions.
  * **We corrected misleading error messages**. Some users received confusing feedback during validation or export, which we clarified or fixed behind the scenes.
  * **Unexpected errors in editing or importing data** were solved, including a case where users couldn’t add records in webforms or got stuck when dealing with ZIP/CSV files.
  * **A system glitch involving deletion jobs** that appeared completed but were still running in the background was analyzed and explained to users, avoiding unnecessary workflow changes on their side.
  * **Connectivity and access issues (e.g., VPN, authentication, and geographic latency)** were also examined and resolved where possible.

* * *

### 🚀 Features & Enhancements (January 2025)

In terms of improvements and added value:

  * **Better stability for webforms and data imports** : We improved how webforms behave when users add, view, or edit records, including ensuring dropdown menus and save functions work as expected even with large datasets.
  * **Improved guidance for system users** : Several clarifications were offered to help users understand how data connections work, particularly around reference data or API access.
  * **Monitoring tools were improved** : Backend changes were made to help administrators detect and manage long-running or stuck jobs more effectively, which reduced response time for resolving issues.
  * **Cleaner validation process** : We implemented small adjustments to how the system handles data quality checks, including geometry validations and date checks, ensuring false errors are minimized.

* * *
