---
title: "Validation"
---

# Validation

[Edit this section](Validation_/edit.md)

## Check eligibility of job

Try to add a validation job for a specific datasetId.

  * If there is an inserted validation job with isReleased false and status QUEUED or IN_PROGRESS and the same **datasetId** then the new job will have status REFUSED.
  * If there is an inserted validation job with isReleased true or a release job with status QUEUED or IN_PROGRESS for the same pair of **dataflowId and providerId** then the new job will have status REFUSED.



[Edit this section](Validation_/edit.md)

## Check if queued job can be executed

If there is a maximum number validation jobs with isReleased false and status IN_PROGRESS do not execute the job and leave it in status QUEUED.

The maximum number of validation jobs is stored in this property: **config/orchestrator/scheduling.inProgress.import.maximum.jobs**

## Verification notes

**Eligibility check — partially accurate but oversimplified.** The actual eligibility logic in `JobServiceImpl.checkEligibilityOfJob()` is broader than described. A new validation job is refused not only when another validation job is active for the same `datasetId`, but also when any `VALIDATION`, `RELEASE`, `IMPORT`, `ETL_IMPORT`, or `DELETE` job with status `QUEUED` or `IN_PROGRESS` references the same dataset (via `datasetId` or the `parameters.datasetId` list). The wiki only mentions validation and release jobs. The second bullet — refusing when a release job exists for the same `dataflowId` and `providerId` — is also a simplification: the actual check calls `isDatasetInActiveReleaseOrValidationJob()`, which inspects the `parameters` map of existing jobs, not just the `dataflowId`/`providerId` pair directly.

**Wrong property key for the maximum-jobs cap.** The wiki states the maximum number of in-progress validation jobs is controlled by `scheduling.inProgress.import.maximum.jobs`. The correct property is `scheduling.inProgress.validation.maximum.jobs`, as declared at line 72 of `JobServiceImpl.java`. The import variant (`scheduling.inProgress.import.maximum.jobs`, line 69) governs import jobs, not validation jobs. These are separate properties with separate values.
