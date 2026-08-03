---
title: "Cancel release process"
---

# Cancel release process

Based on comment <https://taskman.eionet.europa.eu/issues/152763#note-12> the following should be done to cancel the release process: 

  * If the user is releasing, you'll see all the datasets involved with status in progress or in_queue. If you cancel one dataset validation, the other remain in_queue and the process doesn't continue. So if this happens, after cancelling one dataset releasing you have to delete the next one involved that is in_queue (table process in metabase database).
  * Before canceling or deleting processes, also cancel ongoing tasks.
  * Delete the locks in metabase table "lock". The lock table has entries to avoid the user to repeat calls to an endpoint while there's and operation in progress.
  * In the datasets involved there's a field called "releasing". You'll have to put the value to false in that check (table dataset of metabase database).



[Edit this section](Cancel_release_process/edit.md)

### Prerequisites

We need the dataflow_id and the provider_code

[Edit this section](Cancel_release_process/edit.md)

### Find the dataset_id
[code] 
    SELECT id FROM dataset
    WHERE dataflowid = 8109
    AND data_provider_id IN (SELECT id FROM data_provider WHERE code = '[provider_code]');
    
[/code]

[Edit this section](Cancel_release_process/edit.md)

### Find and cancel ongoing tasks by the above process_ids
[code] 
    SELECT * FROM task
    WHERE process_id IN (SELECT process_id FROM process WHERE dataset_id = [dataset_id]);
    
[/code]
[code] 
    UPDATE task
    SET status = 'CANCELED'
    WHERE process_id IN (SELECT process_id FROM process WHERE dataset_id = [dataset_id]);
    
[/code]

[Edit this section](Cancel_release_process/edit.md)

### Find and cancel the in_progress process

Also take note of username, queued_date, date_start, date_finish  

[code]
    SELECT * FROM process
    WHERE dataset_id = [dataset_id]
    AND status = 'IN_PROGRESS';
    
[/code]
[code] 
    UPDATE process
    SET STATUS = 'CANCELED', released = false;
    
[/code]

[Edit this section](Cancel_release_process/edit.md)

### Find and delete the in_queue processes
[code] 
    SELECT * FROM process
    WHERE dataset_id = [dataset_id]
    AND status = 'IN_QUEUE';
    
[/code]
[code] 
    DELETE FROM process
    WHERE dataset_id = [dataset_id]
    AND status = 'IN_QUEUE';
    
[/code]

[Edit this section](Cancel_release_process/edit.md)

### Update the releasing flag in datasets table
[code] 
    UPDATE dataset
    SET releasing = false
    WHERE id = dataset_id;
    
[/code]

[Edit this section](Cancel_release_process/edit.md)

### Delete locks

Use the username, queued_date, date_start, date_finish from above to delete the entries in lock with the same username and create_date close to the dates.

## Verification notes

The procedure described is a purely manual database intervention against the metabase. It predates the `cancelJob` API endpoint (`PUT /jobs/cancelJob/{jobId}`) that was added to `JobControllerImpl.java` (line 717). The current codebase provides a programmatic cancel path via `jobService.cancelJob(jobId, jobInfo, jobShouldFail)`, which is not mentioned here.

The `process` and `task` tables referenced in the SQL are metabase tables managed by the recordstore/orchestrator layer. The `releasing` boolean column on the `dataset` table is confirmed as a real field — it is referenced in `DatasetSnapshotServiceImpl.java` and in the orchestrator's release logic.

The status values used in the SQL — `IN_PROGRESS`, `IN_QUEUE`, and `CANCELED` — are metabase process-level statuses. These differ from the job-level `JobStatusEnum` values (`IN_PROGRESS`, `QUEUED`, `CANCELED`). Note that the job enum uses `QUEUED` where the process table uses `IN_QUEUE`; both exist and operate at different layers.

The `CANCELED_BY_ADMIN` status in `JobStatusEnum.java` (line 23) is not mentioned in this document. It represents a distinct administrative cancel path that may have been added after this document was written.
