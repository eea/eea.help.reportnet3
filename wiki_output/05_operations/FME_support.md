---
title: "FME support"
---

# FME support

This page describe the support provided by EEA staff to FME in reportnet 3.0  
FME server: <https://fme.discomap.eea.europa.eu/fmeserver/>

  * Thanh is to be considerd our second helpdesk line for FME technical issues and server maintenance tasks. Server updates is schedule every 6 months on a Tuesday at 12 pm. It can take between 2h to half day. 
  * Every FME workspace and folder comes with a owner, s/he needs to be contacted first.
  * FME structure is divided. We should use one template provided by DIS2 to generate FME Workspace.



For additional information about FME integration, please see notes on FME-Reportnet 2 integration: [Reportnet_2_-_FME_Integration](/projects/reportnet/wiki/Reportnet_2_-_FME_Integration)

## Verification notes

No source code verification applicable — operational runbook; accuracy depends on current infrastructure configuration, not source code.

The FME Server URL `https://fme.discomap.eea.europa.eu/fmeserver/` is consistent with the FME host referenced in source code: `FMECommunicationServiceImpl.java` has a hardcoded `Host: fme.discomap.eea.europa.eu` header and the `integration.fme.host` configuration key, also confirmed in `Operation_guidelines.md` (`config/dataflow/integration.fme.host`). The page is primarily a contact and governance note (who to call for FME issues) rather than a technical reference, so most of its content is not verifiable from source. The link to Reportnet 2 FME integration is a historical reference that is unlikely to be relevant to current operations.
