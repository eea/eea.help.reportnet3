---
title: "Deployment documentation — gaps and suggested additions"
---

# Deployment documentation — gaps and suggested additions

The following topics are either absent from this folder entirely or covered so briefly that they provide little operational value. Each entry explains what is missing and why it matters.

## CI/CD pipeline documentation

Neither Jenkinsfile is documented. The repository contains two distinct pipelines — `Jenkinsfile` (Altia internal) and `Jenkinsfile.eea` (EEA/Docker Hub) — but no document explains what each does, when each runs, or how they relate to each other. A reader encountering a build failure has no written reference for which pipeline owns which stage.

Topics to cover: the `Preparation → Compile → Install in Nexus → Push to EEA GitHub → Setup sandbox docker images build → Build Docker Images` stage sequence in `Jenkinsfile`; the `Project Build → Report to SonarQube → Setup sandbox docker images build → Docker push` sequence in `Jenkinsfile.eea`; the branch conditions that gate each stage (the `develop1` Nexus publish gate, the `develop`-only Docker build gate, the `sandbox` tag suffix); the Docker Hub registry (`eeacms/`) versus the internal registry (`k8s-swi001:5000/`) distinction; and why both pipelines exist.

## Environment promotion rules

The folder describes which branch maps to which environment but does not document the rules for when a change may move between environments. There is no written policy covering: what review or approval is required before merging from `DevEnv` to `TestEnv`; who may approve a merge to `MasterOneVersion`; what happens when a hotfix is needed on `MasterOneVersion` that is not yet in `TestEnv`; or whether there is any automated gate (test pass rate, SonarQube quality gate) that blocks promotion.

## Rollback procedures beyond image tag change

The rollback section in `Merge_and_deployment_process_for_all_environments.md` covers only the Kubernetes deployment image tag change. Missing topics include: how to roll back a database migration (Flyway); how to roll back a Consul KV configuration change; what the safe ordering is when multiple services need to be rolled back together (e.g. orchestrator and dataset service if a shared API contract changed); and how to verify that a rollback was successful.

## Scheduled job inventory for the Orchestrator

The orchestrator service contains at least 15 scheduling classes (e.g. `JobForExecutingQueuedJobs`, `JobForCancellingValidationsAndReleasesWithoutTasks`, `JobForRestartingReleaseTasks`, `JobForFinalizingReleaseJobsWithFinishedTasks`, `JobForCleanupOfFinishedJobs`). None of these are documented. Operators dealing with stuck jobs, unexpected cancellations, or stale lock records have no written reference for which scheduler is responsible for which recovery action or how frequently each runs.

## Cancel mechanism via API

The `Cancel_release_process.md` document describes a purely manual database intervention. Since that document was written, a `PUT /jobs/cancelJob/{jobId}` endpoint was added to `JobControllerImpl` and a `CANCELED_BY_ADMIN` status was added to `JobStatusEnum`. There is no document that explains the current API-based cancel path, when it should be used instead of direct SQL, and how the `CANCELED_BY_ADMIN` status differs from `CANCELED` in terms of downstream effects.

## `rn3-deploy-scripts` pipeline reference

Three documents (`Deployment_procedure_.md`, `Manualy_uninstall_config_or_preconfig_for_deployment_.md`, `Transfer_branch_to_another_environment_.md`) reference the `rn3-deploy-scripts` repository and its Jenkins job but provide no explanation of what that repository contains, what its Helm releases are named, what parameters its pipeline accepts, or which Kubernetes namespaces it targets per environment. A new developer following `Deployment_procedure_.md` without prior context cannot use it without already knowing this information.

## Maintenance service

The `Jenkinsfile.eea` builds and pushes `eeacms/maintenance-service:1.0` (line 179). This service exists in the `maintenance-service/` directory of the repository. No document in this folder — or anywhere in the wiki output examined — explains what the maintenance service does, when it is activated, or how it affects the deployment procedure (e.g. whether it must be running before or after normal services during a deployment).

## Consul KV configuration changes in deployment

`Orchestrator_changes_to_production.md` lists "Populate new consul variables in preconfigs" as a deployment step but does not explain the process. A `configuration/consulKV.json` file exists in the repository, but there is no document explaining: how new keys are added to Consul; how preconfig and config differ in the deploy-scripts context; what happens if a service starts before its Consul key has been set; or how to verify that all required keys are present after a deployment.

## Environment-specific version tracking

The sprint table in `Merge_and_deployment_process_for_all_environments.md` tracks production deployments manually. There is no document explaining the Transport (`MasterDataLakes`) deployment history, no equivalent table for the DevEnv or TestEnv environments, and no guidance on how version numbers are incremented (the pattern `v3.4`, `v3.4.14`, `v3.4.15` is used but never explained).
