---
title: "Fix export for NULL values"
updated: "2025-06-19 14:36"
updated_by: "Dimitris Petrogiannis"
---

# Fix export for NULL values

When attempting to export data from a dataset, you may encounter the following error in the UI:  

[code]
    Failed exporting data in {providerName}
    eventType=EXPORT_DATASET_FAILED_EVENT
    
[/code]

This may be accompanied by a vague error message such as:  

[code]
    error=Error exporting dataset data
    
[/code]

[Edit this section](Fix_export_for_NULL_values/edit.md)

## **Troubleshooting Steps**

**1) Export Tables Individually**  
Attempt to export each table in the dataset separately. This can help identify if the issue is isolated to a specific table.

**2) Check for Missing Error Notifications**  
If some tables fail to export without displaying an explicit error message, proceed to investigate further.

**3) Inspect for NULL Values**  
In some cases, NULL values in the underlying database may prevent successful export. Verify the schema and data contents of the failing tables to identify any such issues.

**Identify the NULL values in postgres and change them to empty:**  
**1)** Obtain the faulty table schema id from the url  
**2)** In the **datasets** database, locate and open the relevant dataset  
**3)** Within the **table_value** table, find the entry that matches the id_table_schema retrieved in Step 1 and note the corresponding id_table  
**4)** In the **record_value** table, find all records that reference the id_table from Step 3 and for each matching record, collect its id_record  
**5)** In the **field_value** table, query for entries where id_record matches any of the IDs obtained in Step 4  
**6)** Search for fields with NULL values and update them to empty strings by: right click on NULL value -> Edit -> Set to default (Empty string)

example of NULL values in **field_value** table:  
![](Fix_export_for_NULL_values/attachments/image\(1\).png)

## Verification notes

No source code verification applicable — operational runbook.

**Event ownership is in the Dataset Service, not the Validation Service.** `EXPORT_DATASET_FAILED_EVENT` is produced by `FileTreatmentHelper.java` in the dataset-service and handled by `ExportDatasetFailedEvent.java` (also in dataset-service). This runbook has been filed under the validation wiki folder but the underlying failure path belongs to the Dataset Service's export flow.

**`field_value` table column names confirmed.** `FieldValue.java` confirms columns `ID`, `TYPE`, `VALUE`, `ID_FIELD_SCHEMA`, `GEOMETRY`, and a join column `ID_RECORD`. The `VALUE` column is a `String`; a NULL in that column would cause serialisation issues during export depending on the exporter's null handling. The fix of setting NULL to an empty string is a reasonable workaround.
