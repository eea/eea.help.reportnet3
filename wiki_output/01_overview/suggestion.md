# Suggested additions for 01_overview

The following topics are either absent from this folder or covered too thinly to be useful. Each suggestion identifies the gap and explains why it matters.

---

## Role-to-permission matrix

`Roles_and_permissions.md` describes roles in prose but has no structured table showing which operations each role can perform on which resource types. The code applies role checks through annotations (e.g. `@PreAuthorize`) across dozens of controller methods. A matrix mapping role × resource type × allowed operations would make it possible to answer access-control questions without reading every controller. Source: `SecurityRoleEnum`, `ResourceGroupEnum`, and the `@PreAuthorize` annotations in each service's controller.

## Glossary of core domain terms

New developers encounter several terms — Dataflow, Data Collection, EU Dataset, Reference Dataset, Test Dataset, Submission Agreement, Provider — without a central definition. These terms have precise meanings in the code (each corresponds to a `ResourceTypeEnum` value and a distinct PostgreSQL table structure) but none are defined in the overview. A short glossary page with one paragraph per term, and a pointer to where the term appears in the code, would reduce onboarding time significantly.

## High-level data lifecycle

No page describes the end-to-end lifecycle of a reporting cycle: design phase → reporting phase → release → EU dataset creation → public publication. The Changelog and Roles pages mention phases in passing, but no document maps the full sequence, the state transitions, or which roles are active at each step. This is the single most useful thing a new developer or data steward would want to read first.

## `DATA_REQUESTER` role documentation

The `DATA_REQUESTER` role exists in `SecurityRoleEnum` and has corresponding `ResourceGroupEnum` entries for Dataflow, Dataset, and DataSchema scopes. It is not mentioned anywhere in the wiki. A brief page or section explaining when this role is assigned, who can assign it, and what it permits would close a gap visible in the access-control code.

## Microservice inventory

No overview page lists all microservices, their responsibilities, and their ports. A table with service name / port / one-sentence responsibility would orient a developer who needs to know which service to look at for a given behaviour. The deep-dive docs in `CoreDomain/`, `SupportServices/`, etc. cover individual services in detail, but there is no map of the whole.

## Current architecture diagram

`architecture.md` exists at the root of this repo but is not referenced from the wiki overview folder. The wiki's own architecture page (`03_infrastructure/Architecture.md`) was last updated in 2022 and pre-dates Citus, Dremio/Iceberg, and AWSNKP. The overview folder should link to or include the current Mermaid diagram from `architecture.md` so readers get an accurate system picture.
