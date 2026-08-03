---
title: "Service Level Agreement"
---

# Service Level Agreement

[Edit this section](Service_Level_Agreement/edit.md)

## Agreement

It has been defined in the **third specific agreement** between EEA and Tracasa/Altia in Work package 6: Transition to production.  
The scope is to maintain part of the systems as soon as they come into production and continue the maintenance of ROD3 until end of the contract:

  * Support ROD3, continue the integration with Reportnet 2.0 and ensure low interruption or downtime in the services provided for Reportnet 2.0.
  * Support the operational version of Reportnet 3.0 when it enters production in July 2020 with low interruption or downtime in the services provided by the system.
  * Support the operational dataflows as soon as they are ready for production
  * Support transition of services to EEA operations staff



The EEA operations staff will monitor the status of both Reportnet 2 and 3 and perform initial investigation and solution. If the incident persists then a ticket is raised with the contractor, who must solve the issue as soon as possible.

[Edit this section](Service_Level_Agreement/edit.md)

## Procedures

Check: [Support_model_and_Functional_escalation](Support_model_and_Functional_escalation.md)

  1. The support shall include diagnosis and solution of the problem (or performance deficiency) passed to the contractor,
  2. All problems sent to the contractors (including support for operational dataflow) must be dealt with depending on its severity, e.g.
     * The user is unable to use Reportnet 3.0 or continue its work (priority immediate): The contractor shall commence the work immediately after notification. The hours for notification shall be from 9:00 to 17:00 Copenhagen time zone.
     * The user is unable to use some of the features of Reportnet 3.0, delaying its work (priority urgent): The contractor shall commence the work as soon as a developer is available.
     * The user is unable to use some of the features, but an alternative solution is available (priority from low to high): The contractor shall plan the work with adequate priority and include it in the next development sprint.

## Verification notes

No source code verification applicable — organisational/process content.

The SLA response-time commitments (immediate start for "priority immediate"; as-soon-as-available for "priority urgent") reference operational response times rather than system-level technical constraints. Nothing in the source code contradicts these commitments, but one performance characteristic is worth noting for context: email delivery via the Communication Service is synchronous over SMTP and blocks the calling thread. If a user-visible failure results in SMTP calls that exceed timeouts, this can compound outage duration. The source documentation records measured SMTP call durations of 130–600 ms per message with no retry mechanism. This is not a violation of the SLA but is relevant background when diagnosing incidents where users report slow or unresponsive behaviour coinciding with notification-heavy operations.

The reference to "ROD3" integration is historically specific to the third specific agreement. Whether ROD3 obligations remain active under the current contract should be confirmed with the programme manager.
