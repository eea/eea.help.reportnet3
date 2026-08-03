---
title: "Check if dataflow validation is stuck"
---

# Check if dataflow validation is stuck

[Edit this section](Check_if_dataflow_validation_is_stuck/edit.md)

### Prerequisites

We need the dataflow_id and provider_code

[Edit this section](Check_if_dataflow_validation_is_stuck/edit.md)

### Find the dataset_id
[code] 
    SELECT * FROM dataset
    WHERE dataflowid = 8109
    AND data_provider_id IN (SELECT id FROM data_provider WHERE code = '[provider_code]');
    
[/code]

[Edit this section](Check_if_dataflow_validation_is_stuck/edit.md)

### Look for stuck process for this dataset_id

Check if there is an entry in process with status IN_PROGRESS, date_finish null and difference of now from the date_start bigger than 3 hours  

[code]
    SELECT *, AGE(now(), date_start) FROM process
    WHERE dataset_id = dataset_id
    AND status = 'IN_PROGRESS'
    AND date_finish IS NULL
    AND AGE(now(), date_start) > interval '3::hours'
    
[/code]

## Verification notes

**Process table and column names confirmed.** The `process` table, `dataset_id`, `status`, `date_start`, and `date_finish` columns all exist as modelled by `EEAProcess.java` in the recordstore-service.

**Invalid PostgreSQL interval syntax.** The query uses `interval '3::hours'`. This is not valid PostgreSQL syntax. The double colon (`::`) is the PostgreSQL cast operator; inside a string literal it has no special meaning but makes the interval unparseable. The correct form is `interval '3 hours'` or `> INTERVAL '3 hours'`. The query as written will raise a `ERROR: invalid input syntax for type interval` at runtime.

**WHERE clause self-reference.** The condition `WHERE dataset_id = dataset_id` always evaluates to true regardless of the intended filter value. The parameter placeholder should be named differently from the column, for example `WHERE dataset_id = :target_dataset_id`, or supplied as a literal value in a manual query.

**The Validation Service provides a direct API equivalent.** `GET /validation/listInProgressValidationTasks/{timeInMinutes}` (line 632 of `ValidationControllerImpl.java`) returns task IDs that have been in `IN_PROGRESS` status longer than the supplied number of minutes. This is the programmatic equivalent of the manual SQL query and avoids raw database access. Additionally, `PUT /validation/restartTask/{taskId}` (line 614) allows restarting an individual stuck task without deleting the whole process row.
