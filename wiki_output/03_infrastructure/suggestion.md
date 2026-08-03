# Suggested topics for the infrastructure folder

The following topics are absent from the current pages in this folder but are either confirmed by source code inspection or identified as necessary for a complete infrastructure reference.

---

## Orchestrator Service deployment and configuration

The Orchestrator Service (`orchestrator-service`) exists in the source tree and is listed in `Environments.md` as a deployed service in every environment, but it does not appear in any deployment runbook in this folder. No Helm chart instructions, Consul KV namespaces, or startup dependency notes exist for it here. A developer setting up a new environment from the pages in this folder would not deploy the Orchestrator at all.

---

## Inspire Harvester deployment and configuration

The `inspire-harvester` directory exists in the source tree and is deployed in all environments, but there are no deployment instructions for it anywhere in this folder.

---

## Current deployment process

`Reportnet_Deployment.md` was last updated in June 2020 and describes a manual, command-by-command Helm deployment. The Jenkins pipeline (`Jenkinsfile` at the repository root) and the `rn3-deploy-scripts` repository at `https://github.com/eea/rn3-deploy-scripts` together represent the current deployment approach, but the relationship between the two — which stages are automated, what triggers a release, how environment-specific values are managed — is not documented anywhere in this folder.

---

## AWS NKP environment architecture

`AWSNKP_Service_Access.md` introduces an AWS NKP (Nutanix Kubernetes Platform) production cluster (`nkp-prod-fra`) but does not describe its topology, which services run there, how it differs from the RN3 Rancher cluster, or how the two co-exist during migration. A developer receiving this environment as a new production platform has no overview page to orient them.

---

## Dremio and S3 production setup

`Dremio_local_setup.md` covers local development only. There is no page describing how the production Dremio instance is deployed (it runs in a separate Kubernetes cluster from the Reportnet3 services per `dremio_s3.md`), how the NetApp S3 buckets are provisioned, what access controls are applied, or how the `nkp-prod-fra` Dremio URL (`dremio-rn-aws.eea.europa.eu:9047`) was set up.

---

## Redis configuration and Sentinel topology

Redis is mentioned in `Infrastructure.md` and listed in deployment maps, but no page in this folder explains how Redis Sentinel is configured, what the master/slave topology looks like in each environment, or how services connect to it. The source-derived `Persistence/redis.md` document covers this at the application level but is not in this folder.

---

## Kafka topic configuration and retention

`Reportnet_Deployment.md` includes the `kafka-configs.sh` commands for setting retention on the four topics, but there is no page explaining what the four topics are, how partitioning is configured in production, or what monitoring exists for consumer lag. The source-derived `Infrastructure/kafka.md` covers this in depth and should be linked or summarised here.

---

## Graylog integration

`Logging_information.md` states that logs go to Graylog, but no page describes how Graylog is integrated in practice (log collection from container stdout/stderr vs a direct GELF appender, which EEA Graylog instance is used, how to query logs, or what the retention policy actually is). There is no Graylog appender in any service's `logback.xml`, so the collection mechanism is entirely undocumented.

---

## Secret and credential management

No page in this folder describes how secrets are managed: which credentials are stored in Kubernetes Secrets vs Consul KV, how they are rotated, who has access, and what the process is when a credential must be changed. The deployment runbook in `Reportnet_Deployment.md` hard-codes MD5 hashes and placeholder `XXXX` values without explaining where the live values come from.

---

## Citus to Dremio migration status and plan

The source-derived `architecture.md` notes that older dataflows remain on Citus while new ones use S3/Dremio, and that the long-term direction is full migration away from Citus. No page in this folder describes which dataflows are currently on Citus, what the migration steps are for moving a live dataflow, or what the criteria are for marking the Citus cluster as decommissioned.

---

## HPA and resource limits

`Automatic_scaling.md` and `Autoscaling_model.md` are placeholders. The source-derived `kubernetes.md` notes explicitly that no resource requests or limits are set on any service pod, which makes Kubernetes autoscaling non-functional. A page documenting the decided resource profiles per service and the resulting HPA configuration — once that work is complete — is needed.
