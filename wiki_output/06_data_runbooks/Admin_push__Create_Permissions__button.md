---
title: "Admin push "Create Permissions" button"
---

The code is defining a URL endpoint ("/validateAllReporters") that is associated with a specific HTTP method, in this case, a PUT request. When a client sends a PUT request to this URL, the code in this method is executed.

Before anything else, the code checks if the user making the request has the "ADMIN" role.

The code defines two possible responses for this API. It specifies that a successful validation will return an HTTP status code 200, and in case of an error during validation, it will return an HTTP status code 400.

The code attempts to validate all reporters and lead reporters in the system. This validation is carried out by invoking the dataflowService.validateAllReporters(userId) method.

The validateAllReporters method performs a series of data validation tasks and communicates the results through notifications when it runs.

1\. Data Retrieval:  
\- It begins by attempting to retrieve two lists of data:  
\- representativeList: This list contains representatives from the representativeRepository that are marked as invalid.  
\- tempUserList: This list contains temporary users from the tempUserRepository.

2\. Dataflow Identification:  
\- It then extracts a set of unique dataflow IDs from the representativeList to identify the specific dataflows that need validation. This is done by iterating through the representativeList and adding the associated dataflow IDs to a dataflowsToCheck set.

3\. Data Validation:  
\- Next, it performs data validation operations for each identified dataflow and for each temporary user:  
\- For each dataflow in dataflowsToCheck, it calls the representativeService.validateLeadReporters method to validate lead reporters for that dataflow.  
\- For each tempUser in the tempUserList, it calls the contributorService.validateReporters method to validate reporters associated with the tempUser's dataflow and data provider.

4\. Notification Generation:  
\- After successfully completing the validation process, it creates a NotificationVO (Notification Value Object) containing the username of the user who triggered the validation. This is done using SecurityContextHolder.getContext().getAuthentication().getName().  
\- It then sends a notification using kafkaSenderUtils to indicate that the validation process has been completed. The event type is EventType.VALIDATE_ALL_REPORTERS_COMPLETED_EVENT. This notification can be used for tracking and reporting purposes.

5\. Logging:  
\- The method logs a message with information about the successful validation, including the user ID of the person who initiated it. This log is recorded for auditing and debugging purposes.

6\. Error Handling:  
\- If an exception of type EEAException is thrown during any part of the validation process, the method catches the exception. It logs an error message to indicate that an error occurred during the validation process.  
\- It also generates an error notification using kafkaSenderUtils with the event type EventType.VALIDATE_ALL_REPORTERS_FAILED_EVENT. This notification communicates that the validation process encountered an error.

In summary, this method performs data validation for representatives and temporary users associated with specific dataflows. It communicates the results of the validation process through notifications and it logs information about the validation process.

## Verification notes

**Endpoint — verified.** The `PUT /dataflow/validateAllReporters` endpoint is confirmed in `DataflowControllerImpl` (base mapping `/dataflow`, method mapping `@PutMapping("/validateAllReporters")`). The description of the ADMIN role requirement, HTTP 200 success, and HTTP 400 error response is consistent with the controller. The Kafka events `VALIDATE_ALL_REPORTERS_COMPLETED_EVENT` and `VALIDATE_ALL_REPORTERS_FAILED_EVENT` are referenced in `dataflow.md`.

**Content note.** This document reads as a code explanation rather than an operational runbook. It accurately describes the `validateAllReporters` method but does not explain when an operator should press the button or how to confirm it succeeded. This is a documentation quality issue, not a factual error.
