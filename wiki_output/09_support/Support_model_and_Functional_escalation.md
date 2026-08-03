---
title: "Support model and Functional escalation"
---

# Support model and Functional escalation

Describe the procedure about bug reporting, starting with the first line of helpdesk and then the second, how the dispatch is done. It can be included the support model into that page, adding the names of the people in charge.

[Edit this section](Support_model_and_Functional_escalation/edit.md)

## Helpdesk Ticket (Bug/Task) Reporting and dispatch

  1. All tickets to be created under the same parent, for 2023: [#251916](/issues/251916 "Task: Work package 4: Operational mode \(Closed\)") (**Taskman status:** NEW) 
     * EEA helpdesk is usually the one creating bug tickets. 
     * If helpdesk is not available, the ticket is created by the one discovering the bug, helpdesk is put as watcher. 
  2. There is a group (reportnet-3-pct-eworxtrasys) in Taskman to assign the tickets (**Taskman status:** NEW; **Assigned:** reportnet-3-pct-eworxtrasys group)
  3. One person of the group take the ticket, review the content, decides on the priority and refine it for developers (**Taskman status:** NEW; **Assigned:** specific person of the group)
  4. Assign to the relevant developer and work on this (**Taskman status:** ACCEPTED IN QUEUE; **Assigned:** specific developer)
  5. Developer works on the ticket (**Taskman status:** IN PROGRESS)
  6. In case the work cannot be concluded: 
    1. If Developer suspends work on the ticket for whatever reason (**Taskman status:** WIP-DEBT: ON HOLD)
    2. If further information is required by the developer then assign to the relevant person (**Taskman status:** WIP-DEBT: NEEDS CLARIFICATIONS; **Assigned:** usually to the specific person who refined it or _sysadmin linux_ for server admin help)
  7. At the end, deploy the code on consultants' test server and assign the ticket to the first group to test it (**Taskman status:** ACCEPTANCE/DEMO; **Assigned:** reportnet-3-pct-eworxtrasys group but should be picked by the person who refined it)
  8. (optional) deploy on EEA test (or sandbox) server and assign to EEA people to test it (**Taskman status:** ACCEPTANCE/DEMO; **Assigned:** Depends on the case - could be Business manager, the steward, topic center, the original reporter)
  9. Deploy in preproduction environment to test deployment (**Taskman status:** TO BE DEPLOYED; **Assigned:** specific person assigned ticket in step 3)
  10. Deploy in production environment (**Taskman status:** CLOSED)

NOTE: 
  * Only the bugs tagged as “immediate” and “urgent” need to be deployed when done; the others are included in the next sprint. It's up to the PM and BM to decide if the next sprint has to be deployed on Prod or can wait for the release.
  * In case of blocker (the bug prevents part of/the whole system from being available), the helpdesk will inform the stakeholders affected.
  * In case of an operational Task (e.g. Record changes in the DB) the effect is immediately applied in Production without deployment (operational hot-fix)



[Edit this section](Support_model_and_Functional_escalation/edit.md)

## Maintenance escalation

In case of issues that prevent the production environment from being accessible to reporters: 

  1. PM need to send an email to EEA Steerco, with Head of Programme in copy, stating what is the cause of the problem, the possible solutions and the timeframe. A meeting with Steerco can be summoned if more actions are needed.
  2. PM need to send an email to Head of Groups and managers dealing with on-going reporting obligations. No technical detail, give the state of the data if database is being restored. Include timeframe.
  3. Put the maintenance note on Reportnet 3 frontpage.
  4. Helpdesk need to notify the data stewards at the EEA, through email or via chat. It's the responsability of the data stewrds to notify the reporters.

De-escalation procedure, once the system is back online: 
  1. PM send an email to HoGs and SteerCo (cc HoP) to confirm that system is back on line. 
  2. Remove the maintenance note on the frontpage. 
  3. Helpdesk notify the data stewards.

## Verification notes

The escalation workflow is organisational process content and cannot be verified directly against source code. The following observations are based on cross-referencing the described systems with the codebase.

**Taskman ticket workflow.** The workflow described (NEW → ACCEPTED IN QUEUE → IN PROGRESS → ACCEPTANCE/DEMO → TO BE DEPLOYED → CLOSED) is a process definition, not something represented in source code. No issues with accuracy can be raised from the source. The reference to parent ticket `#251916` for 2023 is year-specific and will be stale for any subsequent year; this document should be updated annually with the current parent ticket.

**"Maintenance note on the frontpage" (step 3 of escalation).** The Communication Service implements a `SystemNotification` entity with an `enabled` flag and a `level` field (`SUCCESS`, `INFO`, or `ERROR`). Administrators post these via `POST /notification/createSystemNotification`, and the notification is broadcast to all connected browsers over WebSocket immediately. This is the technical mechanism behind the frontpage maintenance banner. The wiki does not explain how this is done technically; a support engineer performing step 3 needs to know to use this API (or the admin UI that wraps it) rather than editing a static page. A cross-reference to the Communication Service documentation would be useful here.

**"reportnet-3-pct-eworxtrasys" group.** This is a Taskman group name, not a Keycloak group. Source code is silent on it. No verification is possible.

**No source code verification applicable for the escalation contact hierarchy** — these are organisational/process details.
