---
title: "Validate & Run SQL as Provider"
source_url: https://help.reportnet.europa.eu/validate-run-sql-as-provider/
---

# Validate & Run SQL as Provider
### Validate with Provider

As a requester a “**Validate with Provider** ” option has been added and is available for both Design Datasets and Test Datasets when clicking the **Validate** button.

![](../assets/image-823520ac.png)

The dropdown contains all representatives of the dataflow .

![](../assets/image-1-e72185d5.png)

When Validate with Provider is selected, the validation process starts with the provider code included in the request.
In the provider’s datasets, only the simple Validation will be available.

### Run SQL as Provider

A “**Run SQL as Provider** ” feature has been introduced for QC rules that include SQL sentences.
This option can be found in QC rules that contain an SQL expression in Tables, Fields and Rows.

![](../assets/image-2-1024x511.png)

The dropdown contains all representatives of the dataflow .

With this call, the provider code is sent along with the SQL expression.
