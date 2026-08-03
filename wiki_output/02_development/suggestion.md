---
title: "Suggested additions to the 02_development folder"
---

# Suggested additions to the 02_development folder

The following topics are absent from this folder but represent information a developer joining the project would need early. Each section explains the gap and why it matters.

## A consolidated local service port reference

No single page lists all the microservices, their local port numbers, and what each one does. A developer starting the system locally must open thirteen `application.yml` files to discover that the API gateway runs on 8010, the dataflow service on 8020, the dataset service on 8030, the validation service on 8015, the orchestrator on 8091, the recordstore on 8090, the user management service on 9010, the communication service on 9020, the indexsearch service on 9030, the document service on 9040, the rod service on 9050, and the collaboration service on 9060. This information should live in one place alongside the local-setup instructions. Without it, a developer debugging a connection failure cannot tell at a glance which service a given port belongs to.

## How Keycloak integrates with EU Login in practice

The `EU_login_documentation.md` page is from 2019 and describes a CAS integration that no longer exists. No page in this folder explains how authentication actually works for a developer running the system locally. The `Infrastructure/keycloak.md` document covers the production flow well, but a developer needs to know: what the `REACT_APP_EULOGIN` flag controls in `frontend-service/public/env.js`, why it is set to `false` for local development, what happens when it is `true` (the browser is sent through EU Login's OIDC flow before Keycloak), and how to obtain a test token using the `/user/generateToken` endpoint when running locally without EU Login. This is the single most confusing part of the local setup, and it is currently undocumented.

## A guide to the custom `@PreAuthorize` expressions

The `Security_Guideline_for_controller_methods.md` page correctly identifies the two security patterns (`/private/` path and `@PreAuthorize`) but does not explain the custom Spring Security Expression Language functions that appear on nearly every secured endpoint: `secondLevelAuthorize`, `secondLevelAuthorizeWithApiKey`, `checkApiKey`, and `checkAuthorizationKeyFromConsul`. These are defined in `EeaSecurityExpressionRoot` at `common-utitlities/src/main/java/org/eea/security/jwt/expression/EeaSecurityExpressionRoot.java`. A developer adding a new endpoint needs to know what each expression does, how resource IDs are resolved from method parameters, and when to use `checkApiKey` versus `secondLevelAuthorize`. Without this, a developer either copies a nearby annotation without understanding it or leaves an endpoint unsecured.

## A complete local-environment troubleshooting guide

Both local setup pages describe the happy path for standing up all infrastructure components, but neither explains what to do when things go wrong in common ways. The Consul key-value import, Keycloak realm import, PostgreSQL extension setup, and Redis host resolution all have known failure modes (the `Local_setup_.md` page itself hints at the Keycloak group issue in an important note at the bottom). A troubleshooting section — covering at minimum: how to verify that the Consul import succeeded, how to confirm the Keycloak realm is correctly configured, how to diagnose a service that fails to register with the service discovery, and what "groups" to remove from a freshly-created Keycloak user — would save hours for new developers.

## An integration testing guide

The `JUnit_Mockito_testing.md` page covers unit tests in depth. There is no document explaining how integration tests are structured, what the `test-infrastructure` module (present in the root `pom.xml`) provides, and which tests run against a real database or message broker. Developers contributing to services with Kafka-driven workflows or multi-service interactions have no guidance on how to test those paths. Given that the codebase uses Kafka extensively for orchestration and that several failure modes only appear at integration boundaries, the absence of this document is a meaningful gap.

## A guide to Consul key-value configuration

The local setup pages mention importing `consulKV.json` but do not explain the structure of Consul's key-value tree or how configuration is consumed at runtime. Developers who need to add a new configuration key, override a value for local testing, or understand which service reads which key currently have no reference. A document mapping the key-path conventions (`config/application/`, `config/ums/`, and per-service paths) to the Spring Cloud Config bootstrap mechanism, and listing the most important keys (such as all `eea.keycloak.*` entries and `spring.redis.host`) would be directly useful when debugging startup failures or customising a local environment.
