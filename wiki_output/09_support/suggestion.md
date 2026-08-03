---
title: "Suggestions for helpdesk documentation improvements"
---

# Suggestions for helpdesk documentation improvements

This document records gaps identified during verification of the 09_support wiki pages against the Reportnet3 source code and source-derived service documentation. It is addressed to whoever maintains the helpdesk section.

---

## Gaps in the existing pages

### Role model is out of date

`Reportnet_Helpdesk_Services.md` documents only a subset of the current Keycloak roles. The full set defined in `SecurityRoleEnum` includes `DATA_STEWARD`, `STEWARD_SUPPORT`, `DATA_OBSERVER`, `DATA_REQUESTER`, `REPORTER_PARTITIONED`, and `NATIONAL_COORDINATOR`, none of which appear in the wiki. A helpdesk engineer following the existing role guide when managing Keycloak groups will encounter group names they cannot cross-reference. The role table should be updated to reflect the complete current set and should explain when each role is appropriate to assign.

### System notification mechanism is undocumented

Both `Support_model_and_Functional_escalation.md` and `Reportnet_Helpdesk_Services.md` refer to posting a maintenance note on the Reportnet 3 frontpage, but neither explains how to do it. The mechanism is the `SystemNotification` feature in the Communication Service. An administrator posts to `POST /notification/createSystemNotification` with a message (capped at 300 characters), an `enabled` flag, and a `level` of `SUCCESS`, `INFO`, or `ERROR`. The notification is broadcast to all connected browsers over WebSocket immediately and displayed as a banner. To remove it, the administrator calls `DELETE /notification/deleteSystemNotification/{id}`, which sets `enabled=false` and pushes a `NO_ENABLED_SYSTEM_NOTIFICATIONS` event to all connected clients so the banner disappears without a page refresh. Helpdesk engineers carrying out the maintenance escalation procedure need either access to an admin UI that wraps these endpoints or a documented API call sequence.

### Technical feedback (Collaboration Service) is not mentioned

The Collaboration Service provides a structured in-platform messaging thread between reporters and custodians/stewards. Reporters and custodians can exchange text messages and file attachments within a dataflow, keyed by dataflow ID and data provider. Automated messages from the Orchestrator also appear in these threads. Helpdesk staff who receive reports such as "I cannot see my messages" or "the custodian's reply has not arrived" need to understand this mechanism to diagnose whether the problem is a Keycloak group membership issue, a missing notification, or a backend error. This is entirely absent from the current helpdesk documentation.

### Log aggregation tool may have changed

The Graylog URL in `Reportnet_Helpdesk_Services.md` (`https://logs.eea.europa.eu/streams/5e48016bc2020e0012badef2/`) was current when the wiki was written. The source code shows that services ship logs via Filebeat to a Logstash endpoint rather than directly to Graylog. Whether the current production log stream URL is the same should be confirmed with EEA infrastructure, and if it has changed the wiki must be updated. A stale log URL means a helpdesk engineer investigating an incident has no starting point for log lookup.

---

## What a helpdesk engineer needs that is not currently documented

### Quick-reference: common user-facing errors and their internal causes

The following error patterns appear frequently in support tickets and are diagnosable from existing platform behaviour. A short reference table would save significant investigation time.

| User complaint | Likely cause | Where to investigate |
|---|---|---|
| "I cannot see my dataflow on the landing page" | User not in the Keycloak group `Dataflow-{id}-LEAD_REPORTER` or `Dataflow-{id}-REPORTER_WRITE` | Keycloak admin console: check the user's group memberships |
| "I cannot access my dataset" | User not in the Keycloak group `Dataset-{id}-LEAD_REPORTER` or `Dataset-{id}-REPORTER_WRITE` | Keycloak admin console: check dataset-level groups for that provider |
| "I am not receiving notifications" | User was not connected to the WebSocket when the event fired and the calling service did not separately call the REST persistence endpoint | Check Graylog for `VALIDATION_FINISHED_EVENT` or relevant event; check MongoDB `communication.UserNotification` collection for the userId |
| "My import/validation is stuck" | A job is stuck in `IN_PROGRESS` status in the Orchestrator | See `05_operations/Handle_stuck_jobs.md` and `05_operations/Fix_stuck_processes_.md` |
| "Released data is not visible on the public page" | Post-release publication step failed | See `05_operations/Released_data_not_visible_in_public_page.md` |
| "I cannot log in" | EU Login account not pre-loaded in Keycloak, or group membership missing | Keycloak admin console: verify user exists and holds the correct realm role |
| "The technical feedback thread shows no messages" | Keycloak group membership for the provider's dataset is missing, or messages were created with incorrect `direction` flag | Check Collaboration Service logs and verify Keycloak dataset groups for the provider |

### Links to relevant runbooks in other folders

The operations and data runbooks folders contain procedures that are directly relevant to incidents helpdesk staff will escalate. The following are the most applicable:

- `05_operations/Handle_stuck_jobs.md` — how to identify and resolve jobs that are stuck in a running state
- `05_operations/Fix_stuck_processes_.md` — broader procedure for stuck processing tasks
- `05_operations/Check_And_Fix_Database_Errors.md` — database-level error diagnosis
- `05_operations/Released_data_not_visible_in_public_page.md` — publication failures after release
- `05_operations/Add_provider_to_dataflow.md` — how to add a data provider manually (relevant when a reporter cannot see their country in a dataflow)
- `05_operations/Admin_push__Create_Permissions__button.md` — how to trigger permission reconstruction from the admin UI (useful when Keycloak groups are present but access still fails)
- `05_operations/Reset_MFA_for_Microsoft_and_WikiD.md` — MFA reset procedure for user login issues

### How to post and remove a system notification (maintenance banner)

This procedure should be added either as a new section in `Reportnet_Helpdesk_Services.md` or as a standalone runbook. The steps are:

```
To post a maintenance banner:
POST /notification/createSystemNotification
Body: { "message": "<text, max 300 chars>", "enabled": true, "level": "INFO" }
Requires: ADMIN role

To remove the maintenance banner:
DELETE /notification/deleteSystemNotification/{id}
Requires: ADMIN role
The banner is removed from all connected browsers immediately.
```

If there is an admin UI that wraps these endpoints, the UI path should be documented here instead.

### National coordinator role — explanation for helpdesk

The `NATIONAL_COORDINATOR` role is absent from all current helpdesk documentation but it requires the most complex Keycloak group setup of any role in the platform. A national coordinator is automatically added to the Keycloak groups for every dataset belonging to every data provider for a given country within a dataflow. If a helpdesk engineer manually attempts to set up national coordinator access by adding individual dataset groups, they will likely miss groups and create an inconsistent state. The correct approach is to use the UMS `POST /user/nationalCoordinator` endpoint, not manual group manipulation. This should be documented.

### Notification delivery is not guaranteed for offline users

Helpdesk engineers should be aware that real-time WebSocket notifications and persistent stored notifications are two independent mechanisms in the platform. If a user was not connected when a Kafka event fired, they receive a persistent notification only if the originating service also called `POST /notification/private/createUserNotification` separately. Not all services do this for all event types. When a user reports not receiving a notification for a completed operation, the first diagnostic step is to check the MongoDB `communication.UserNotification` collection for that user, not to assume the operation failed.
