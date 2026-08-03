---
title: "Import file through external integration"
---

# Import file through external integration

\- Inside dataset schema click "External integrations"   
\- Click "Create external integration"   
\- Give a name and a description  
\- In repository name insert "ReportNetTesting"   
\- In Workespace name insert "ImportExcel.fmw"   
\- In operation select IMPORT  
\- In file extension insert xlsx  
\- Click create  
\- Click "import dataset data"   
\- In custom file imports, select the integration you created  
\- Select the xlsx file to import  
\- Click upload

## Verification notes

No source code verification applicable — operational runbook describing UI-based steps for configuring and using an FME external integration. The integration mechanism described (creating an integration with a tool name, workspace, operation type `IMPORT`, and file extension) is consistent with the `integration` table schema and the Dataflow Service's integration configuration model. The FME workspace name `ImportExcel.fmw` is environment-specific and must be verified against the FME Server repository available in the target environment.
