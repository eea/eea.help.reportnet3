---
title: "Security Guideline for controller methods"
---

# Security Guideline for controller methods

The Reportnet 3 app is based on a convention that the methods that are meant only for internal use , should contain in their path the following `/private/` . This way the apigateway secures them and makes them inaccessible from the outside .   
When adding a new method in a microservice controller , there are 2 ways of making this method secure : 

  1. Include the `/private/` in the method path , if the method is for **internal** use only. f.e : 
[code]    /datacollection/private/pendingProviders/{id}
[/code]

  2. Add a `@PreAuthorize` annotation with the desired security level , if the method is for **external** use ,or **both** . f.e 
[code]    @PreAuthorize("isAuthenticated()")
[/code]

## Verification notes

Both conventions described here are confirmed in the source. The `/private/` path segment is used extensively across controllers: examples include `/private/pendingProviders/{id}` in the dataflow service, `DatasetControllerImpl` endpoints such as `/private/updateStatistics/{id}`, `/private/importFileData/{datasetId}`, and `/private/{datasetId}/deleteDatasetData`, and equivalents across `ReferenceDatasetControllerImpl` and `RecordStoreControllerImpl`.

The `@PreAuthorize` pattern is confirmed on external-facing methods throughout the codebase. Actual usage is considerably more complex than `isAuthenticated()` alone: the standard patterns are `secondLevelAuthorize(#id, 'ROLE_1', 'ROLE_2', ...)`, `secondLevelAuthorizeWithApiKey(...)`, `checkApiKey(...)`, and `checkAuthorizationKeyFromConsul(...)`. These custom Spring Security Expression Language functions are defined in `EeaSecurityExpressionRoot` in `common-utitlities/src/main/java/org/eea/security/jwt/expression/EeaSecurityExpressionRoot.java`. The wiki mentions none of these; a developer adding a new endpoint would need to understand when to use each one.

The page omits the `hasAnyRole('ADMIN')` and `hasRole('ADMIN')` patterns that appear on many endpoints as a fallback granting administrative access regardless of resource-level roles. This is a meaningful security consideration that the guideline should document.
