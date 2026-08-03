---
title: "Release and validation"
---

# Release

[Edit this section](Release_and_validation_/edit.md)

## case 1: successful scenario for release job

**steps to reproduce:**   
1\. make sure no other release job for the dataflow and dataprovider has been added and no validation for the datasets has been added  
2 add a release job for the dataflow and dataprovider

**outcome** : the release job gets status queued, so it will be executed by the scheduled task JobForExecutingQueuedJobs

[Edit this section](Release_and_validation_/edit.md)

## case 2: release job gets status refused because of existing release job

**steps to reproduce:**   
1\. in db_orchestrator database change the status of a release job for a dataflow and dataProvider to IN_PROGRESS  
2\. add a release job for the dataflow and dataprovider

**outcome** : the release job gets status refused

[Edit this section](Release_and_validation_/edit.md)

## case 3: release job gets status refused because of existing validation job with release true for the dataflow, provider

**steps to reproduce:**   
1\. in db_orchestrator database change the status of a validation job with release true for a dataflow and dataProvider to IN_PROGRESS  
2\. add a release job for the dataflow and dataprovider

**outcome** : the release job gets status refused

[Edit this section](Release_and_validation_/edit.md)

## case 4: release job gets status refused because of existing validation with release false job for the dataset

**steps to reproduce:**   
1\. in db_orchestrator database change the status of a validation job with release false for a dataset of a dataflow and dataProvider to IN_PROGRESS  
2\. add a release job for the dataflow and dataprovider

**outcome** : the release job gets status refused

[Edit this section](Release_and_validation_/edit.md)

## case 5: release job gets status failed because of validation blocker errors

**steps to introduce:**  
1\. create a blocker qc rule for the dataset  
2\. add record that violates the qc rule  
3\. add a release job for the dataflow and dataprovider of the dataset

**outcome** : the release job gets status failed

## Verification notes

This document is substantially identical to `Release_.md`, covering the same five test scenarios with the same preconditions and outcomes. The statuses `IN_PROGRESS`, `IN_QUEUE`, `QUEUED`, and `REFUSED` are all confirmed in `JobStatusEnum.java`. Note that the enum uses `QUEUED` as the status name, not `IN_QUEUE`; the wiki uses `IN_QUEUE` in the precondition steps to describe the state of process-level records in the metabase, which is a different layer from the job-level `QUEUED` status — the distinction is not explained in this document.

The scheduled task referred to as `JobForExecutingQueuedJobs` is confirmed to exist and runs every one minute (`orchestrator-service/src/main/java/org/eea/orchestrator/scheduling/JobForExecutingQueuedJobs.java`).
