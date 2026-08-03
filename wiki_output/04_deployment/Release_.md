---
title: "Release"
---

# Release

When the user presses the release button, a new validation job with release=true, is created. For every dataset of the provider, a new validation process is created and for every process, validation tasks are created with type VALIDATION_TASK. When all tasks are finished, the validation process is finished. When all validation processes are finished, the validation job is also finished and a new release job is created. If any of the dataset has validation blockers, the release job is failed. For every dataset of the provider a release process is created. If snap files are created, then for every snap file, a release task is created with type RELEASE_TASK. When all tasks are finished, the release process is finished. When all release processes are finished, the release job is also finished.

Before the system starts executing a new release a number of checks are executed. Firstly, we check the number of validation and release jobs and whether a new job can be added. In case of the release, 2 jobs are created, one after the other, firstly the validation and after that the release. So the system must have availability both for validations and release jobs for a release to start executing. Then, we check if there's already a release running in the dataflow. In this case, the job remains in status=QUEUED and will be executed later.

[Edit this section](Release_/edit.md)

### case 1: successful scenario for release job

**steps to reproduce:**   
1\. make sure no other release job for the dataflow and dataprovider has been added and no validation for the datasets has been added  
2 add a release job for the dataflow and dataprovider

**outcome** : the release job gets status queued, so it will be executed by the scheduled task JobForExecutingQueuedJobs

[Edit this section](Release_/edit.md)

### case 2: release job gets status refused because of existing release job

**steps to reproduce:**   
1\. in db_orchestrator database change the status of a release job for a dataflow and dataProvider to IN_PROGRESS  
2\. add a release job for the dataflow and dataprovider

**outcome** : the release job gets status refused

[Edit this section](Release_/edit.md)

### case 3: release job gets status refused because of existing validation job with release true for the dataflow, provider

**steps to reproduce:**   
1\. in db_orchestrator database change the status of a validation job with release true for a dataflow and dataProvider to IN_PROGRESS  
2\. add a release job for the dataflow and dataprovider

**outcome** : the release job gets status refused

[Edit this section](Release_/edit.md)

### case 4: release job gets status refused because of existing validation with release false job for the dataset

**steps to reproduce:**   
1\. in db_orchestrator database change the status of a validation job with release false for a dataset of a dataflow and dataProvider to IN_PROGRESS  
2\. add a release job for the dataflow and dataprovider

**outcome** : the release job gets status refused

[Edit this section](Release_/edit.md)

### case 5: release job gets status failed because of validation blocker errors

**steps to introduce:**  
1\. create a blocker qc rule for the dataset  
2\. add record that violates the qc rule  
3\. add a release job for the dataflow and dataprovider of the dataset

**outcome** : the release job gets status failed

## Verification notes

The description of `VALIDATION_TASK` and `RELEASE_TASK` as task types is confirmed by `TaskType.java` in `common-interfaces/src/main/java/org/eea/interfaces/vo/metabase/TaskType.java`. Both values exist in the enum.

The job statuses `QUEUED`, `IN_PROGRESS`, `REFUSED`, `FAILED`, and `FINISHED` are confirmed in `JobStatusEnum.java` (`common-interfaces/src/main/java/org/eea/interfaces/vo/orchestrator/enums/JobStatusEnum.java`). The wiki's description of the status flow is consistent with this enum.

The wiki describes a "scheduled task `JobForExecutingQueuedJobs`" executing queued jobs. This class exists at `orchestrator-service/src/main/java/org/eea/orchestrator/scheduling/JobForExecutingQueuedJobs.java` and runs every one minute, which is consistent with the described behaviour.

The wiki states that "a new validation job with release=true is created" when the user presses the release button, and that a separate release job follows. In `JobControllerImpl.java` (lines 276–277), the `addReleaseJob` method actually inserts the initial job with type `JobTypeEnum.VALIDATION` (not `RELEASE`), passing `release=true`. The separate `RELEASE` type job is created downstream after validation completes. This two-step creation is consistent with the wiki's description but the distinction between the initial validation-for-release job and the subsequent release job could be clearer.

The phrase "snap files" is used without definition. The recordstore service uses `.snap` files as snapshot data segments (confirmed in `JdbcRecordStoreServiceImpl.java`). This is accurate terminology but unexplained in the document.
