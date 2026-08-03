---
title: "Version Numbers"
---

# Version Numbers

The development of Reportnet v3 follows the rules: 

  * The platform delivered at the end of the development contract (prior to first obligation) is labeled: 3.0.0.0
  * Every new year of improvement (with a dedicated contract) increase the first digit: 3. **x+1** .0.0 
  * Every time a release must be deployed on production, the third digit increases: 3.0. **x+1** .0 
  * Every hotfixes increase the last digit by 1: 3.0.0. **x+1**
  * Release Candidate (RC) is used to mark a version that is not yet ready for production (not tested or not approved yet)
  * Release Candidate (RC) is increased with any attempt release to TEST/Staging EEA environment (e.g. v3.0.3.0-RC1 requires bug fixing after testing, therefore new version delivered will be v3.0.3.0-RC2, RC3… until version is considered OK to go to PROD). This will imply subsequent versions to be renamed with their RCx digit updated accordingly.

**Notes:**

  * Each microservice has his own versioning as well. The global version number of the Reportnet represents a group of microservices with their own version numbers. The numbers are not matching necessary. 
  * There will exist a page in PROD with showing Application and Microservices version deployed.
  * The early version of Reportnet 3 were labelled as such: DEMO in June 2019, BETA in Septembre 2019, Public Release in July 2020. The version on the 5/02/2021 is considered final and labelled 3.0.0.0
  * If there is any sprint that goes live and is not foreseen below, just subsequent versions will increase third digit v3.0.x.0 RC1
  * Milestone: Reportnet3 in PROD on 8th February 2021 
    * From this point 
      * Hotfix -- deployed in Staging EEA environment for testing before PROD
      * Sprint -- deployed in TEST EEA environment for testing before PROD

**Example:**

  * Sprint 27: v3.0.0.0 RC5.2 
    * any hotfixes required on top: v3.0.0.x RC5.2
  * Sprint 28: v3.0.0.0 RC5.3 -- delivery to prod on 05th of February
  * Sprint 29 - v3.0.0.0 RC5.4 
    * any hotfixes required on top: v3.0.0.x RC5.3

## Verification notes

The version numbering scheme described here (four-segment `3.x.x.x`) was the policy at go-live in 2021. The Changelog page now references sprint numbers (e.g. Sprint 104 in May 2026) without explicit version numbers in that format — it is unclear whether the four-segment convention is still applied consistently. No source code artefact encodes the version policy; it would need to be verified with the team.
