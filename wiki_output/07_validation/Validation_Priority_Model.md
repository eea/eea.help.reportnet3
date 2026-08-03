---
title: "Validation Priority Model"
---

# Validation Priority Model

[Edit this section](Validation_Priority_Model/edit.md)

## Process Pickup Flow :

Scheduler wakes up  
↓  
Check available threads  
↓  
Use HighPriorityTaskReaderStrategy or LowPriorityTaskReaderStrategy   
(HIGH or LOW) Consul variable -- validation -- validation.instance.priority (current: high)  
↓  
Fetch task IDs from the database  
↓  
Group tasks by process  
↓  
Select number of tasks according to free threads number (highest priority*, lowest load*)   
↓  
Initialize Process P  
↓  
Begin task enqueueing

[Edit this section](Validation_Priority_Model/edit.md)

## **Task Execution Flow (Per Process):**

Process P picked (Process Pickup Flow)  
↓  
Enqueue all tasks (dataset, table, record, field)  
↓  
Submit tasks to thread pool  
↓  
Tasks run in parallel  
↓  
Wait until ALL PICKED tasks of P finish  
↓  
Move to next process of the current job (enforced after process is finished and released to achieve sequential job process execution)

[Edit this section](Validation_Priority_Model/edit.md)

### How a Priority is given to a process

Condition  |  Assigned Priority   
---|---  
\-------------------------------------------------  |  \-----------------   
Dataflow is in `DESIGN` status or has no deadline  |  70 (lowest)   
Deadline is more than 90 days away  |  50   
Deadline is between 60–90 days  |  40   
Deadline is between 7–30 days  |  30   
Deadline is within 7 days or has passed  |  20 (highest)   
  
*field priority persists in process table  
Process Load = number of tasks of the process calculated at runtime

[Edit this section](Validation_Priority_Model/edit.md)

### Scenario of how priority affects task processing :
[code] 
    A new process with priority = 20 (highest) enters the system.  
        But all current threads are busy running other processes (lower priorities).  
        High-priority process waits in queue until all processes from another job finish.
[/code]

**Example:**  
Job A, Process 1 — running (priority 70)  
Job A, Process 2 — waiting (priority 70) 

Job B, Process 1 — running (priority 30)

Job C, Process 1 — waiting (priority 30)

Job X, Process X arrives (priority 20)

**What happens?**  
Job X Process X will wait Job A AND Job B as they already have tasks in_progress running until a thread becomes available and Process X tasks will be favored - picked before Job C  
Priority affects picking order, not running order!

## Verification notes

**Strategy classes confirmed.** `HighPriorityTaskReaderStrategy` and `LowPriorityTaskReaderStrategy` are confirmed in `/validation-service/src/main/java/org/eea/validation/util/priority/`. The instance-level switch via the `validation.instance.priority` Consul variable is confirmed in `ValidationScheduler.java`, which checks for `"HIGH"` and falls back to `LowPriorityTaskReaderStrategy` otherwise.

**Priority table has a missing level and incorrect values.** The wiki shows five priority levels. The actual `getPriority()` method in `ValidationHelper.java` (lines 749–781) produces six distinct levels. The full mapping, driven by the configurable `validation.priority.days` property, is:

- No deadline, or dataflow in `DESIGN` status → 70 (correct in wiki)
- Days from deadline exceeds `periodDays[0]` (in either direction) → **60** (missing entirely from wiki)
- Within `periodDays[0]` but beyond `periodDays[1]` → 50 (wiki incorrectly shows 50 for ">90 days" without the 60 level)
- Within `periodDays[1]` but beyond `periodDays[2]` → 40 (correct value, but the day threshold depends on config, not fixed at 60–90 days)
- Within `periodDays[2]` but beyond `periodDays[3]` → 30 (correct value, wiki says "7–30 days" but actual thresholds come from config)
- All remaining cases → 20 (correct)

The wiki's specific day ranges (90, 60, 30, 7) are plausible default values for `validation.priority.days` but are not hardcoded in source. The thresholds are entirely driven by the Consul/config value and may differ between environments. The priority 60 level — for deadlines that are very far in the future or very far in the past — is absent from the wiki table.

**Process table columns confirmed.** `date_start` and `date_finish` column names are confirmed in the `EEAProcess` entity (`EEAProcess.java`).
