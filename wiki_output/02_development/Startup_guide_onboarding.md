---
title: "Startup guide onboarding"
---

# Service Startup Dependencies

[Edit this section](Startup_guide_onboarding/edit.md)

## Startup Graph

All services can start independently except dataset and validation that are depending on recordstore.
[code] 
    recordstore
    ├── dataset
    └── validation
    
[/code]

[Edit this section](Startup_guide_onboarding/edit.md)

# Runtime service communication map (zuul-based calls)

This document maps service-to-service communication based on configured Zuul clients in the codebase.  
It reflects **declared HTTP communication paths** , not confirmed runtime execution paths.

A listed dependency means: 

  * the service has a configured Zuul client for the target service
  * the service is capable of calling the target service at runtime



[Edit this section](Startup_guide_onboarding/edit.md)

## Service Communication Matrix (Zuul Clients)

This table shows from which service we have a zuul call to which service

Service  |  zuul client to   
---|---  
api-gateway  |  \-   
collaboration  |  communication   
dataflow   
dataset   
document   
orchestrator   
user-management   
communication  |  \-   
dataflow  |  communication   
dataflow  
dataset   
document   
orchestrator   
rod   
user-management   
validation  
dataset  |  collaboration   
communication   
dataflow   
dataset  
document   
orchestrator   
recordstore   
user-management   
validation   
document  |  collaboration   
communication   
dataflow   
rod  |  \-   
orchestrator  |  dataflow   
dataset   
recordstore   
user-management   
validation   
recordstore  |  dataflow  
dataset  
document  
orchestrator  
recordstore  
user-management  |  communication   
dataflow   
dataset   
validation  |  communication   
dataflow   
dataset   
orchestrator   
recordstore   
user-management   
  
[Edit this section](Startup_guide_onboarding/edit.md)

## Observed Special Cases

[Edit this section](Startup_guide_onboarding/edit.md)

### Self-references

The following services reference themselves via Zuul:

  * dataflow -> dataflow
  * dataset -> dataset
  * recordstore -> recordstore

These may indicate: 
  * internal routing through Zuul
  * legacy client definitions
  * or non-removed historical service references



No conclusion is made yet on whether these are intentional or redundant.

[Edit this section](Startup_guide_onboarding/edit.md)

## Dataflow Zuul Call Observation

Dataflow is calling **IntegrationControllerZuul** even though the implementation exists within the same service:
[code] 
    org/eea/dataflow/service/file/DataflowHelper.java:77
    IntegrationControllerImpl (same service)
    
[/code]

Additional related usage:
[code] 
    org/eea/recordstore/kafka/commands/ExecuteUpdateMaterializedViewCommand.java:37
    
[/code]

This suggests that internal calls may still be routed through Zuul instead of direct internal invocation.

[Edit this section](Startup_guide_onboarding/edit.md)

## Notes about zuul calls

  * This map is derived from Zuul client configuration and code inspection of client usage points.
  * It represents potential communication paths between services.
  * It does not represent business-level functional dependencies.

## Verification notes

The startup dependency claim — that only dataset and validation depend on recordstore — is confirmed by source. `DatasetServiceImpl` imports `RecordStoreControllerZuul` and `ProcessControllerZuul` from the recordstore service. `RulesServiceImpl` in the validation service does the same. No other service has a comparable hard dependency on recordstore at startup.

The dataflow self-reference observation is confirmed: `DataflowHelper.java` at line 77 injects `IntegrationControllerZuul`, which is the Zuul client for `IntegrationControllerImpl` in the same service (`dataflow-service`).

The service communication matrix is not independently verifiable from source code in this review (it would require examining all Feign/Zuul client configurations across every service), but the stated methodology (inspecting Zuul client configuration) is sound. The table format makes the matrix difficult to read because the second column values wrap across rows without clear row boundaries; this is a rendering artefact from the wiki export.
