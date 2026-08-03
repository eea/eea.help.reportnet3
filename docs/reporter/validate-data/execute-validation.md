---
title: "Execute validation"
source_url: https://help.reportnet.europa.eu/reportnet-3-1-reporter-howto/validate-data/execute-validation/
---

# Execute validation
## How to validate the data manually,

In the reporting dataset you will find several menu buttons for quality control

![](../../assets/QualityControlDataset.png)

  * **Validate** – Runs validations for the whole dataset
  * **Show validations** – Shows a table of all the validation issues found across the whole dataset after a validation has been run.
  * **QC rules** – shows a list of all the validations which have been created for the dataset.**Dashboards** – Provides a visualisation of the validation feedback.
  * **Manage copies** – Functionality to save copies of the data (snapshots or restore points)
  * **Refresh** – After import, validation and restore copy, you need to refresh the tables

Click on ‘**Validate** ’. Shortly after a notification in the top right will indicate the validation has started and another notification when it has been completed. It is important to press the **Refresh** button to demand your browser refreshing to current table view.

The system has four types of error entities (field level, record level, table level and dataset level)

  * Field level errors have icons next to value in the field. Hover over it to see the error message.
  * The column ‘Validations’ shows for each record which level of errors at field and record level.
  * Table level errors can be seen by clicking on the **Show validation** button. These errors are displayed in a summary table, grouped by a particular error type.
