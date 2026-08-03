---
title: "Validation Results per Release Snapshot"
source_url: https://help.reportnet.europa.eu/validation-results-per-release-snapshot/
---

# Validation Results per Release Snapshot
Validation results are now stored for each provider release **snapshot** , allowing users to access the exact validation status that existed when a release was created.

## **What’s new**

Previously, validation results were updated with each new provider release, making only the most recent results available.

With this enhancement, validation results are preserved as part of each release snapshot. This provides full historical visibility into validation outcomes for every release.

## **How it works**

When a provider release is created, the current validation results are stored together with the release snapshot.

As a result, each snapshot contains the validation results exactly as they were at the time of release, enabling accurate historical review and comparison.

Existing promotion processes and query behavior remain unchanged.

## **Accessing validation results**

A new endpoint allows users to download validation results for a specific release snapshot.

### **Endpoint**

`GET /downloadValidation/{snapshotId}`

### **Required parameters**

  * snapshotId
  * datasetId
  * dataflowId
  * providerId

### **Response**

The endpoint returns the validation results associated with the selected release snapshot as a CSV file.

If multiple validation result files exist for the snapshot, they are automatically combined into a single downloadable file.

### **Access**

Access to this endpoint is restricted. Users must have an appropriate dataset role (such as Custodian, Steward, Lead Reporter, or National Coordinator) or use a valid API key with equivalent permissions.
