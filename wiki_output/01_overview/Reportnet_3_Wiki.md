---
title: "Reportnet 3 Wiki"
---

# Welcome to Reportnet 3

Reportnet is Eionet's infrastructure for supporting and improving data and information flows. Reportnet 3 is project is to "Modernise eReporting including through a more advanced Reportnet and by making best use of the existing infrastructure."

[Edit this section](Reportnet_3_Wiki/edit.md)

## General Information

The purpose of this page is to collect documentation related to the process of tasks and issues for Reportnet 3.  
The "issues" log contains all the items related to Reportnet 3.0: 

  * Features
  * Bugs
  * tasks
  * Decisions
  * Risks



The project contain also sub-projects each with it's own dedicated page. Check the Overview page for the links to the page.

~~All the rest of the documentation is available on the project page on Eionet:<https://projects.eionet.europa.eu/reportnet-3.0/>~~

**To edit the wiki pages or create a ticket you must log in with your Eionet account.**

[Edit this section](Reportnet_3_Wiki/edit.md)

### Deployment and development

  * [Kubernetes deployment files](Kubernetes_deployment_files.md)
  * [Reportnet Deployment](Reportnet_Deployment.md)
  * [Development and Production tools](Development_and_Production_tools.md)
  * [EU login documentation](EU_login_documentation.md)
  * [Performance and stress tests](Performance_tests.md)
  * [Feature process orchestration](Feature_process_orchestration.md)
  * [Orchestrator changes to production](Orchestrator_changes_to_production.md)
  * [Reportnet 3 Changelog](Reportnet_3_Changelog.md)
  * [AWSNKP Service Access](AWSNKP_Service_Access.md)
  * [Service Monitoring](Service_Monitoring.md)
  * [Remote Service Connection](Remote_Service_Connection.md)



[Edit this section](Reportnet_3_Wiki/edit.md)

### Operational model

This section contains the description of the system specific to EEA: test, staging, prod. Together with the backup/restore plan and operation guidelines, how to maintain the system, where the commands are.

  * [Architecture](Architecture.md)
  * [BackupRestore plan](BackupRestore_plan.md)
  * [BackupRestore HotSwitch proposed](BackupRestore_HotSwitch_proposed_.md)
  * [Environments (Production, Sandbox, Test, Hotfixes, Dev)](Environments.md)
  * [Infrastructure](Infrastructure.md)
  * [Operation guidelines](Operation_guidelines.md)
  * [Automatic scaling](Automatic_scaling.md)
  * [FME support](FME_support.md)
  * [Autoscaling model for k8s](Autoscaling_model.md)
  * [ROD](ROD.md)
  * [Dremio local setup](Dremio_local_setup.md)
  * [Iceberg demo](Iceberg_demo.md)
  * [ Api Documentation](Api_Documentation.md)
  * [ Validation Priority Model](Validation_Priority_Model.md)
  * [ Change schema in Datalakes](Change_schema_in_Datalakes_.md)
  * [ Replicated Postgres troubleshooting](Replicated_Postgres_troubleshooting.md)



[Edit this section](Reportnet_3_Wiki/edit.md)

### Processes

  * [Support model and functional escalation](Support_model_and_Functional_escalation.md)
  * [Reportnet helpdesk services](Reportnet_Helpdesk_Services.md)
  * [Service Level Agreement](Service_Level_Agreement.md)
  * [Version Numbers](Version_Numbers.md)
  * [Acceptance Test](Acceptance_Test.md)
  * [Logging information](Logging_information.md)
  * [Security Guideline for controller methods](Security_Guideline_for_controller_methods.md)
  * [List of FME processes](FME_processes.md)
  * [ As an Admin push "Create Permissions" button](As_an_Admin_push_"Create_Permissions"_button.md)
  * [Merge and deployment process for all environments](Merge_and_deployment_process_for_all_environments.md)
  * [Ticket templates](Ticket_templates.md)
  * [JUnit and Mockito Testing](JUnit_Mockito_testing.md)



[Edit this section](Reportnet_3_Wiki/edit.md)

### More materials

  * [Project Handbook](Project_Handbook.md)
  * [Roles and permissions](Roles_and_permissions_.md)
  * [Shared documents](Shared_documents.md)
  * [Ideas and context to consider for Reportnet 3 from Reportnet 2](Ideas_and_context_to_consider_for_Reportnet_3_from_Reportnet_2.md)
  * [Case studies for BDR - Reportnet 2](Case_studies_for_BDR.md)



[Edit this section](Reportnet_3_Wiki/edit.md)

### Frequently used processes

  * [Deletion of old dataflows in the database](Deletion_of_old_dataflows_in_the_database.md)
  * [ Deletion of hidden (invalid) records in dataset](Deletion_of_hidden_records_in_dataset_.md)
  * [Manual validations](Manual_validation.md)
  * [Import file through external integration](Import_file_through_external_integration.md)
  * [Cancel the release process](Cancel_release_process.md)
  * [Delete provider dataset from dataflow](Delete_provider_data_from_dataflow.md)
  * [Delete bad records from dataset](Delete_bad_records_from_dataset.md)
  * [Fix cannot add records for attachment field](Fix_cannot_add_records_for_attachment_field.md)
  * [Check if dataflow validation is stuck](Check_if_dataflow_validation_is_stuck.md)
  * [ Get validation/copy/release locks](Get_lock_record_information.md)
  * [ Suggested git flow process](Suggested_git_flow_process_.md)
  * [ Postgres recovery in kubernetes](Postgres_recovery_in_kubernetes.md)
  * [ Create new database in postgres](Create_new_database_in_postgres.md)
  * [ Manual deletion of data](Manual_deletion_of_data_.md)
  * [ Add provider to dataflow](Add_provider_to_dataflow.md)
  * [ Citus local setup](Citus_local_setup.md)
  * [ Copy data collections to eu dataset problems](Copy_data_collections_to_eu_dataset_problems_.md)
  * [ Transfer branch to another environment](Transfer_branch_to_another_environment_.md)
  * [ Manually uninstall config or preconfig for deployment](Manualy_uninstall_config_or_preconfig_for_deployment_.md)
  * [ Process sequence](Process_sequence.md)
  * [ Clone dataflow](Clone_dataflow_.md)
  * [ Release-Validate manually](Release_manually_.md)
  * [ Add missing public data files in dataflow](Add_missing_public_files_in_dataflow.md)
  * [ Fix for error creating a qc rule and update materialized view](Fix_for_error_creating_a_qc_rule_.md)
  * [ Deployment procedure ](Deployment_procedure_.md)
  * [ Fix stuck processes ](Fix_stuck_processes_.md)
  * [ Access containers with kubectl ](Access_containers_with_kubectl_.md)
  * [ Local setup](Local_setup_.md)
  * [ Set up webforms in a local environment](Local_setup_webforms_.md)
  * [ Locate mongo record duplicates ](Locate_mongo_record_duplicates.md)
  * [ Released data not visible in public page](Released_data_not_visible_in_public_page.md)
  * [ Check And Fix Database Errors](Check_And_Fix_Database_Errors.md)
  * [ Decode consul file](Decode_consul_file.md)
  * [ Handle stuck jobs](Handle_stuck_jobs.md)
  * [ Materialized views update fails because there are duplicate records in citus](Materialized_views_update_fails_duplicate_records.md)
  * [ Fix Export for NULL values](Fix_export_for_NULL_values.md)
  * [ Reset MFA for Microsoft and WikiD](Reset_MFA_for_Microsoft_and_WikiD.md)



[Edit this section](Reportnet_3_Wiki/edit.md)

### Citus

  * [Citus findings coordinator workers](Citus_findings_coordinator_workers.md)
  * [Reportnet3 citus setup](Reportnet3_citus_setup.md)
  * [Create new dataset from code](Create_new_dataset_from_code.md)
  * [Add worker node](Add_worker_node.md)
  * [Remove worker node](Remove_worker_node.md)



[Edit this section](Reportnet_3_Wiki/edit.md)

#### Test cases for orchestrator jobs

  * [ Release](Release_.md)
  * [ Validation](Validation_.md)



[Edit this section](Reportnet_3_Wiki/edit.md)

### Custodian Documentation

  * [Validation API Endpoints](Validation_api_endpoints.md)
  * [Import for Reference datasets API Endpoints](Import_Reference_Datasets.md)



[Edit this section](Reportnet_3_Wiki/edit.md)

### Developer notes

  * [Local setup & onboarding material](Local_setup_and_onboarding_material.md)

## Verification notes

No source code verification applicable — this is the wiki index page. It catalogues sub-pages; the sub-pages themselves are verified individually in their respective folders.
