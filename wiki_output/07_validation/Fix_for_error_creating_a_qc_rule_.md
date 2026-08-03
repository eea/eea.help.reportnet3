---
title: "Fix for error creating a qc rule"
---

# Fix for error creating a qc rule

While creating a qc rule, reporters got an error similar to   

[code]
     
    ERROR: relation "dataset_46122.legacy_seasonalperiod" does not exist.
    
[/code]

After inspecting the materialized views for this dataset, one could see that there was no view for legacy_seasonalperiod. So updating the materialized views using the following api solved the problem.

PUT [https://api.reportnet.europa.eu/recordstore/createUpdateQueryView?datasetId=46122&isMaterialized=false](https://api.reportnet.europa.eu/recordstore/createUpdateQueryView?datasetId=46122&isMaterialized=false) with Bearer token

## Verification notes

**Endpoint path confirmed.** `PUT /recordstore/createUpdateQueryView` is confirmed in `RecordStoreControllerImpl.java` at line 677. The endpoint accepts `datasetId` and `isMaterialized` as request parameters, exactly as used in the wiki example.

**Root cause attribution is plausible.** The error `relation "dataset_46122.legacy_seasonalperiod" does not exist` indicates that a SQL rule references a table view that has not been created (or was dropped). The fix — calling `createUpdateQueryView` — triggers `recordStoreService.createUpdateQueryView(datasetId, isMaterialized)`, which recreates the dataset's query views. The `isMaterialized=false` parameter creates a regular (non-materialised) view; using `true` would create a materialised view instead.
