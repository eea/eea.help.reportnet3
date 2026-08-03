---
title: "Project Handbook"
---

# Project Handbook

[Edit this section](Project_Handbook/edit.md)

## Project processes

[Edit this section](Project_Handbook/edit.md)

### Communication management

All Communication is handle on Teams or by emails.

**Trasys/Eworx**  
For all project management and coordination topics, please address emails to 

  * FAZOS Dimitrios <[dimitrios.fazos@trasys.gr](mailto:dimitrios.fazos@trasys.gr)>   
In Cc: 
  * OIKONOMOU Ioannis <[ioannis.oikonomou@trasys.gr](mailto:ioannis.oikonomou@trasys.gr)>
  * KOUROS Christos <[christos.kouros@trasys.gr](mailto:christos.kouros@trasys.gr)>
  * MANIOTIS Vaios <[vaios.maniotis@trasys.gr](mailto:vaios.maniotis@trasys.gr)>



**Escalation procedure**  
<https://taskman.eionet.europa.eu/projects/infrastructure/wiki/Reportnet_3#Escalation-procedure>

[Edit this section](Project_Handbook/edit.md)

### Taskman workflow

The following steps describe the way work items are handled within sprints.   
The main workflow policies are listed below:

  * EEA or Contractors can propose tickets (New). 
  * Work Items can Tasks, Features or Bugs. 
    * Features represent creation of new capabilities.
    * Tasks can be corrections or extension of existing capabilities.
    * Bugs are issues identified during testing or by users and are treated according to their priority and severity as described in [Support_model_and_Functional_escalation](Support_model_and_Functional_escalation.md).
  * If contractors Product Owner propose new tickets, they are always assigned to EEA staff first (backlog for EEA), they are not ready to be considered for the contractors.
  * Upon work initiation on a work item, an analysis is performed and is registered in the comments section. The work item is then assigned to the requestor in status "Needs Clarifications". The requestor from EEA should approve the analysis by providing a relevant comment.
  * Acceptance criteria are also documented in the aforementioned comment of the analysis. EEA can amend/correct the acceptance criteria depending on the business case and requested feature.
  * As far as possible tickets are not assigned to individuals but to a pool of developers (teams) for the specific area of work. 
  * Tickets will be moved from “New” to “Accepted in Queue” by EEA staff or contractors’ Product Owner. Tickets will only be moved into the queue if they need to be started on in the following days/2-3 weeks.
  * Priority of the ticket in the queue are decided by EEA managing staff and is indicated by: 
    * Position (top to bottom) for Sprints, not by metadata (unless otherwise agreed by the entire team, by priority metadata field)
    * Priority (immediate, urgent, high, normal, low) for helpdesk issues
  * Only EEA staff can review tickets in “Acceptance/Demo” and can move them to “To be deployed” or “closed”. Unless otherwise agreed by the steering committee. This is to make sure work is properly reviewed on a demo server before reaching production environment. 
  * EEA should approve the production deployment of a sprint by moving the "Testing Activities" task to “To be deployed” or “closed”. 
  * We should use the keyword LARGE in the title (parent tickets) to structure bigger tasks/epics. Creation of child tickets should be done mainly by contractor when the ticket is in the process to be started.
  * Use the EEA Planned Product ticket as the very top parent for all the tickets. This makes sure we can follow budget consumption within the same contract.
  * Tickets in needs clarifications status must be replied as soon as possible so that developers or EEA staff can continue directly without losing context. If this does not happen in a reasonable time, the contractor or EEA staff must escalate the tickets awaiting feedback to the DIS IT project manager or Product Owner via a direct email and/or via Riot. 
  * Finishing current tickets takes precedence over starting new tickets. So, in practice tickets that are “on hold”, “needs clarifications”, “to be deployed” should be addressed before starting a new one from the queue. 
  * No more than 3 tickets can be in progress for each developer. (WIP limits). This will reduce tickets Lead-Time (less waiting time) and reduce inefficient task switching costs.
  * Issues sent to the contractors (including support for operational dataflow) must be dealt with depending on its severity: 
    * Immediate priority: The user is unable to use Reportnet or continue its work. the contractor shall commence the work immediately after notification. 
    * Urgent priority: The user is unable to use some of the features of Reportnet, delaying its work. The contractor shall commence the work as soon as a developer is available.
    * Tickets with priority “immediate” and “Urgent” are the only type of tickets that allows a developer to task-switch and break the general WIP-limit rule. 
    * From High to low: The user is unable to use some of the features, but an alternative solution is available. The contractor shall plan the work with adequate priority, in agreement to EEA (for ex: include it in the next development sprint).



[Edit this section](Project_Handbook/edit.md)

## Project roles and responsibilities

Check Eionet groups on:  
<https://www.eionet.europa.eu/eionet-account-tools/eionet_account_tools/roles?role_id=reportnet-3>

## Verification notes

No source code verification applicable — this page covers project management processes, communication channels, and escalation procedures. Content is organisational, not technical.
