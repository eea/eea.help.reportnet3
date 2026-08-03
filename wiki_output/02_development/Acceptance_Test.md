---
title: "Acceptance Test"
---

# Acceptance Test

Description of how we do User Acceptance Test (UAT) for Reportnet 3 at the EEA. UAT is part of the five types of testing we do on Reportnet3:  
unit test, integration test, system test, UAT and release test; the first 3 are done by Altia/Tracasa, the last 2 by EEA.

[Edit this section](Acceptance_Test/edit.md)

## 1\. Prerequisites of User Acceptance Testing

  * List of features with description must be available as tickets under taskman and marked as closed or Acceptance/testing. 
  * Application Code should be fully developed and deployed on an environment accessible to the Business Group (Altia's servers or EEA Testing site)
  * Unit Testing, Integration Testing & System Testing should be completed with no blockers. Cosmetic error are acceptable.
  * If needed, regression testing should be completed (same as above, with no major defects)
  * Tracasa/Altia shall communicate when the system is ready for UAT



[Edit this section](Acceptance_Test/edit.md)

## 2\. How we do UAT

In our case, UAT are run after each sprints: 

  * The Business Manager check the list of features to test 
  * The BM create dedicated test scenarios and cases to check all features. Those scenarios may involve other staff, or a demo done by the consultants. 
  * Check that the test environment is fit to run the cases. More test data or conditions may be needed.
  * Any test data or conditions must follow EEA standards and rules (especailly regarding privacy and security).
  * Test cases are executed by the require staff member. The bugs must be reported on taskman and fall under the operational mode protocol. Re-test bugs if fixed during the UAT. 
  * If necessary record the results under the appropriate tickets.
  * Confirm business objectives with PM and Scrum POs.



[Edit this section](Acceptance_Test/edit.md)

## 3\. After UAT

  * Code is declare ready for shipping. depending on Busines erquirements, the code can be deployed on production.

## Verification notes

No source code verification applicable — this page describes a human process (UAT methodology, roles, and criteria) with no verifiable technical claims against source code.
