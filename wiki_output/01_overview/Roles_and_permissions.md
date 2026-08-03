---
title: "Roles and permissions"
updated: "2021-09-06 12:11"
updated_by: "Christian Xavier Prosperini"
---

# Roles and permissions

This page is a summary of the roles in Reportnet 3.0 and their description. For a detailed mapping roles/permissions, check the architecture document.

[Edit this section](Roles_and_permissions/edit.md)

## Data steward (EEA thematic expert)

The data steward is the thematic expert and overall responsible for a dataflow. All dataflows must have a data steward and only one.  
Data steward can create the dataflow, assign access rights, manage the dataflow and design the schema. They can grant Editor, Read-only and observer roles to other users in the design and reporting phases (see below).  
The data steward also defines and manages legislative instruments, consult and monitor the tasks performed by the data custodian in the dataflow design phase, ensures the quality of the reported data and create the EU dataset.

The Custodian and steward are also responsible for creating the EU dataset and also the post-delivery data processing, typically done in the Common Workspace.   
The data steward is responsible for closing the reporting process.

[Edit this section](Roles_and_permissions/edit.md)

## Data custodian (EEA data management expert)

Data custodian is the data management expert for a dataflow. All dataflows must have a data custodian and only one.  
Data steward can create the dataflow, assign access rights, manage the dataflow and design the schema. They can grant Editor, Read-only and observer roles to other users in the design and reporting phases (see below).

When the schema is finalised, the data custodian (or steward) assign the lead reporters (how these reporters are nominated is different for each dataflow) and then create the data collection.  
The Custodian and steward are also responsible for creating the EU dataset and also the post-delivery data processing, typically done in the Common Workspace.

[Edit this section](Roles_and_permissions/edit.md)

## Design phase roles

[Edit this section](Roles_and_permissions/edit.md)

### Editor

Editors role exist **only** during the **design** phase and are assigned by the data steward or data custodian. Editors are be someone who can also configure tables, fields and QC rules for example an ETC or consultant.

Once the design of the dataflow is finished, the editor role is **removed automaticaly** from all users.

[Edit this section](Roles_and_permissions/edit.md)

### Read-only

Read-only design role exist **only** during the **design** phase and are assigned by the data steward or data custodian. Read-only access will be for those who are invited to follow the design and provide feedback (for example Commission) or they could be invited to test the data model (for example Reporters).

Once the design is finished, the Read Only role is **removed automatically** from all users.

[Edit this section](Roles_and_permissions/edit.md)

## Reporting phase roles - national level

[Edit this section](Roles_and_permissions/edit.md)

### Lead reporter and second lead reporters

There is one lead reporter per country per dataflow assigned when the dataflow is created. It is possible to add a secondary lead reporter as backup - currently through request to helpdesk.

The role is granted by custodian or steward at the end of the design phase. The process of lead reporter nomination is managed within each dataflow.  
The Lead reporters have full rights to import data, submit to the data collection and assign other users. The Lead reporter can assign other users as Reporters inside or outside their organisation who can import and validate data for example regions, other institutions, consultants, etc. The Lead reporter can assign Read-only access to other users inside or outside their organisation.

Both lead reporters can deliver the data (release the data colection).

They can access to the reported data and monitor the status of the submissions on the national level.

[Edit this section](Roles_and_permissions/edit.md)

### National Dataflow Coordinator/National Reporting Coordinator and National Focal Point

The National Dataflow Coordinator/National Reporting Coordinator and National Focal Point will have Read-only rights to the dataset.

National coordinator list is maintained within the platform (there can be multiple coordinators in one country) and has access to all dataflows within the country

These roles can manage for a particular dataflow the Lead Reporter, and assign additional users as Reporters or Read-only roles.

[Edit this section](Roles_and_permissions/edit.md)

### Reporter

Users assigned by the lead reporter to support the reporting of the data for a submission agreement. They can import and edit data and run QC.

Reporters cannot manage access or do the final delivery (release to data collection)

[Edit this section](Roles_and_permissions/edit.md)

### Reporter (partitioned)

Users assigned by the lead reporter to support the reporting of the data for a submission agreement. They can import and edit data in their own working space and run QC in their own working space. They can see the data in other reporters working spaces, but cannot edit it.

Reporters cannot manage access or do the final delivery (release to data collection)

[Edit this section](Roles_and_permissions/edit.md)

### Read-only

Users with Read-only access to the dataflow assigned by the lead reporter or National Dataflow Coordinator.

[Edit this section](Roles_and_permissions/edit.md)

### Custodian support

It's like Observer plus the following permissions: 

  * Test dataset
  * Technical acceptance workflow full access
  * Can update documentation
  * Can manage lead reporters



[Edit this section](Roles_and_permissions/edit.md)

## Reporting phase roles - EU level (can see across all submissions for a dataflow)

[Edit this section](Roles_and_permissions/edit.md)

### Observer

Custodian and steward can also assign other users inside or outside the organisation as Observers. They have read only access to the dataflow across all countries for example Commission, ETC.   
They will only be added after the DC has been created.  
The Observer is very similar to the National Coordinator - they just can see all countries rather than just their own.

They can: 

  * See the data in the data collection, EU dataset and all the countries' datasets. 
  * Export data from any dataset. 
  * They have full access to status dashboards and help
  * They can see the reporters list

They can't: 
  * add/remove any reporters
  * do copy to EU dataset or export to the Common Workspace
  * change the reporting status
  * create data collection



[Edit this section](Roles_and_permissions/edit.md)

### Helpdesk

Assigned users with the responsibility to resolve any technical problems related to the reporting process and support the countries in the reporting process. They can manage any access rights and provide coordination between the data providers and requesters. Helpdesk shall have Read-Only access on all dataset and dataflow, independent of dataflow states.

[Edit this section](Roles_and_permissions/edit.md)

### Public user

Unregistered users that can access to the reported data in charts and on maps.

[Edit this section](Roles_and_permissions/edit.md)

### Registered user

Registered users whom are stakeholders in the reporting process that can access to the reported data in charts and on map and export this information to support the creation of an EU dataset and disseminating results.

[Edit this section](Roles_and_permissions/edit.md)

### System administrator

Users with the responsibility to maintain and support the platform.

## Verification notes

Last wiki update: 2021-09-06. Verified against `SecurityRoleEnum` and `ResourceGroupEnum` in `common-interfaces/src/main/java/org/eea/interfaces/vo/ums/enums/` (source of truth for roles as of June 2026).

**Role naming — "Custodian support" vs `STEWARD_SUPPORT`**
The wiki calls this role "Custodian support". The code defines it as `STEWARD_SUPPORT` in `SecurityRoleEnum`. The two names are inconsistent; the code name takes precedence. All documentation and UI text should be checked for this discrepancy.

**Missing role — `DATA_REQUESTER`**
`SecurityRoleEnum` includes `DATA_REQUESTER`, and `ResourceGroupEnum` defines `DATAFLOW_REQUESTER`, `DATASET_REQUESTER`, and `DATASCHEMA_REQUESTER` groups for it. This role does not appear anywhere in the wiki page. Its purpose and who can assign it are undocumented.

**Missing role — `REPORTER_PARTITIONED` as a distinct enum value**
`REPORTER_PARTITIONED` appears as a separate entry in `SecurityRoleEnum`. The wiki does describe "Reporter (partitioned)" under reporting phase roles, so the concept is documented — but the exact enum name (`REPORTER_PARTITIONED`) is not stated, which matters for anyone looking at access-control annotations in the code.

**Editor split into read/write**
The wiki describes a single "Editor" role for the design phase. The code defines two separate values: `EDITOR_READ` and `EDITOR_WRITE`. The wiki should clarify that editors with write access configure schemas and QC rules, while editors with read access observe.

**"Helpdesk" and "System administrator" both map to `ADMIN`**
The wiki describes two separate roles ("Helpdesk" and "System administrator") with similar descriptions. The code has a single `ADMIN` value. It is unclear whether both are collapsed into `ADMIN` or whether Helpdesk is a separate concept handled outside the `SecurityRoleEnum` (e.g. a Keycloak group). Needs confirmation from the team.

**`ResourceGroupEnum` scope — roles are resource-scoped**
The wiki presents roles as flat system-level concepts. In practice, each role is always scoped to a specific resource type (Dataflow, Dataset, DataCollection, EUDataset, ReferenceDataset, TestDataset, DataSchema). A user can be `DATA_STEWARD` on Dataflow 5 and `DATA_OBSERVER` on Dataflow 12 simultaneously. This is a fundamental architectural point the wiki does not mention.
