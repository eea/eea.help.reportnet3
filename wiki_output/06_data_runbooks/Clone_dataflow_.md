---
title: "Clone dataflow"
---

# Clone dataflow

  * Go to the dataflow you want to clone and in the left sidebar click "Export schema" 
  * Go to the dataset schema you want to export data and click on "Export dataset data" -> Zip (.csv for each table)" 
  * Go to the environment you want to clone the dataflow and create a new dataflow
  * Click the + button for new schema, select "Import schema(s)" and select the schema you exported in the first step
  * Go to the dataset schema and click on "Import dataset data" -> Zip (.csv for each table) and select the zip file you exported in the second step

## Verification notes

No source code verification applicable — operational runbook describing UI-based steps. The schema export and import functionality described corresponds to `POST /dataflow/exportSchemaInformation/{dataflowId}` and the schema copy mechanism (`POST /dataschema/copy`) on the backend, both of which are confirmed in the Dataset Service and Dataflow Service source code. The data import step uses the standard CSV-per-table zip format consistent with the `FileTreatmentHelper` import path. No discrepancies found.
