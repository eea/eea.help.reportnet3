---
title: "Orchestrator changes to production"
---

# Orchestrator changes to production

  * Create orchestrator_db to production
  * Alter table tasks in production metabase 
  * Populate new consul variables in preconfigs
  * Add orchestrator microservice helm scripts 
  * Merge Production to orchestrator
  * Communicate all dependencies

## Verification notes

This document describes a one-time migration checklist for introducing the Orchestrator Service into the production environment. It is historical in nature.

The orchestrator service database is confirmed to be a separate database; the service's `application.yml` excludes the default JPA and DataSource autoconfiguration (`spring.autoconfigure.exclude`), meaning it manages its own datasource configuration through external means (Consul KV or environment variables). A `configuration/consulKV.json` file exists in the repository root, confirming that Consul is used for externalised configuration, consistent with the "Populate new consul variables in preconfigs" step.

The "Add orchestrator microservice helm scripts" step references the `rn3-deploy-scripts` repository, which is not present in the local clone. The helm scripts for the orchestrator cannot be verified here.

The Jenkinsfile.eea confirms that `eeacms/orchestrator-service` is a standard Docker Hub image built and published from the `orchestrator-service/` directory, consistent with the service being deployable via the standard helm/Kubernetes pathway.

The "Alter table tasks in production metabase" step is consistent with the existence of `task` and `process` tables referenced in the cancel-release runbook. No Flyway migration files were examined to confirm the specific DDL change.
