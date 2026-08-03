---
title: "Local setup webforms"
---

### Steps for setting up webforms in a local environment

  * Go to mongo db compass for an evironment which contains webforms and export everything from dataset_schema -> WebformConfig
  * Go to local compass and create inside dataset_schema a collection named WebformConfig. Inside import the file you exported in the previous step.
  * Login to the environment that contains the webform as admin. Go to 'Manage Webforms' and export the json file.
  * Login in your local environment as admin. Then from the left panel click on 'Manage Webforms' and import the json file.
  * Create your dataflow and in the dataset schema click on configure webform and select the webform you want.

## Verification notes

The MongoDB collection name `WebformConfig` inside the `dataset_schema` database is consistent with the source. The `WebformControllerImpl` in `dataset-service/src/main/java/org/eea/dataset/controller/WebformControllerImpl.java` exposes a `POST /{datasetId}/uploadWebformConfig` endpoint, confirming that uploading a webform configuration through the UI is a real, supported operation. The procedural steps on this page (exporting from Compass, importing locally, using the admin UI) cannot be verified against source code directly, but the underlying technical model they describe is consistent with the codebase. No discrepancies found.
