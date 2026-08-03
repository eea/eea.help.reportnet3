---
title: "Fix stuck processes"
---

# Fix stuck processes

If citus is in recovery mode or there has been a deployement which has affected the ongoing processes do the following:

[Edit this section](Fix_stuck_processes_/edit.md)

## Step 1: Find all stuck processes

Execute the following query:
[code] 
    select * from public.process where status = 'IN_PROGRESS'
    
[/code]

[Edit this section](Fix_stuck_processes_/edit.md)

## Step 2: Retrieve tasks for each process

For each **processId** run the following query
[code] 
    select * from public.task  where process_id = [processId]
    
[/code]

[Edit this section](Fix_stuck_processes_/edit.md)

## Step 3a: Cancel processes without tasks

If for a specific **processId** , no tasks were retieved in step 3, then change the status of the process to CANCELED with the following query:
[code] 
    update public.process set status = 'CANCELED' where process_id  = [processId];
    
[/code]

Also, remove locks that are related to the processes. Follow the process described here: <https://taskman.eionet.europa.eu/projects/reportnet-3/wiki/Get_lock_record_information>.

[Edit this section](Fix_stuck_processes_/edit.md)

### Step 3b: Restart in progress tasks

If for a specific **processId** , tasks with status IN_PROGRESS were retrieved in step 3, then then change the status of each task with a **taskId** to IN_QUEUE with the following query:
[code] 
    update public.task set status = 'IN_QUEUE' where process_id = [processId] and id = [taskId]
    
[/code]

## Verification notes

The table names and column names used in the SQL queries are verified against `postgresql_db.md`.

**`public.process` table.** Confirmed to exist in the Metabase DB (created by migration `V65__create_table_process.sql`). The `status` column exists and uses `ProcessStatusEnum` values including `IN_PROGRESS` and `CANCELED`. The `process_id` column exists as the UUID string join key.

**`public.task` table.** Confirmed to exist in the Metabase DB (created by migration `V66__add_column_priority_and_create_task.sql`). The `status` column and `process_id` column both exist. The join condition `where process_id = [processId] and id = [taskId]` is valid: `task.process_id` matches `process.process_id` (string), and `task.id` is the primary key (bigserial).

**Citus reference.** The document opens with "If citus is in recovery mode". Citus is a PostgreSQL extension for distributed/sharded tables. There is no reference to Citus in the current source code or infrastructure documentation — the dataset schemas use standard PostgreSQL per-dataset schemas managed by the Recordstore Service, not Citus sharding. This opening condition may be a historical artefact from a period when Citus was evaluated or used. The SQL procedures themselves are valid regardless of whether Citus is involved.

**External link.** The link to `https://taskman.eionet.europa.eu/projects/reportnet-3/wiki/Get_lock_record_information` for lock removal is a Taskman internal wiki page and cannot be verified from source code.
