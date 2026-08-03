---
title: "Manual validation"
---

# Manual validation

  * Validations should run outside working hours.
  * Before running validations give the user to be used admin rights through keycloak (from users tab select the user, go to "Role Mappings" tab and from "Available Roles" select ADMIN and press "Add selected")
  * For linux users in order to run validations, vpn connection should be closed.
  * In feeder validationTest_param.csv for every dataset we want to run the validation for we enter the user's username and password and the datasetId. 
  * From the file load_test_repo.yml where all processes exist, we copy the process with requestName "validationTest", paste it in file load_test.yml and we delete all other processes from load_test.yml file. In usersNumber we enter the total number of datasets we want to run validations for. So in load_test.yml there should exist only the following with the desired usersNumber:  

[code]    gatling_config:
       scenarios:
        #checked
         - requestName: validationTest
           endpoint: /validation/dataset/${datasetId}
           usersNumber: 1
           numberExecutions: 1
           useFeeder: true
           requireAuth: true
           method: put
           pauseTime: 2
           timeOut: 20000
           headers:
             Authorization: Bearer ${token}
    
[/code]

  * From intellij click "Edit configurations" and in the window appearing in the left up corner click the "+" button for adding new configuration. Then select maven and depending on the intellij version used, in the "Run" (newer version) or "Command line" (older version) option enter "gatling:test" and in working directory select test-infrustructure service path. In the "Runner" tab (for older versions) or for newer version from the window settings add the environment variables option and in "Java options", select java 8 and put the following environment variables:  

[code]    LOAD_TEST_PATH -> absolute path for your load_test.yml file.
    URL_BASE -> api url depending on the environment the validations should run. e.g. for dev environment URL_BASE would be https://dev-api.reportnet.europa.eu.
    
[/code]

  * We click apply and ok to close the window.
  * To run the process we just click the run button next to the maven configuration we have created
  * In intellij in folder target -> gatling we can view the results for all simulations run.
  * In metabase table process we can see the validations created for the specific user and date start.
  * For every process using process id, we can find the tasks created in metabase table task.
  * If a validation process has constantly status=IN_QUEUE, we delete the row from process table and run the validation again for that dataset.

## Verification notes

**Endpoint path confirmed but path variable name differs.** The Gatling config uses `/validation/dataset/${datasetId}` with `method: put`. This corresponds to `PUT /validation/dataset/{id}` in `ValidationControllerImpl.java` (line 148). The path is correct; the path variable in the controller is `{id}`, not `{datasetId}`, but this is an implementation detail that does not affect the URL path itself.

**No other source-level discrepancies.** The remainder of the document is a Gatling/IntelliJ operational procedure referencing `process` and `task` tables in metabase. Both table names (`process`, `task`) are confirmed as real persistence entities (`EEAProcess`, `Task` in recordstore and validation-service respectively).
