---
title: "Reportnet Helpdesk Services"
---

# Reportnet Helpdesk Services

The purpose of the Reportnet Helpdesk is to resolve user requests and queries in an organised and accurate way to ensure high satisfaction from the users.

[Edit this section](Reportnet_Helpdesk_Services/edit.md)

## What we do

  * Address and resolve technical issues and user concerns by guiding the users.
  * Assign roles to the EU Login accounts according to the agreed procedures.
  * Advice users on how to perform complex operations while using Reportnet. 
  * Report bugs to the developers in accordance with the [Support model and Functional escalation](Support_model_and_Functional_escalation.md).
  * Planning and delivery of training courses/webinars to increase the users’ ability to use the tools.
  * Provide suggestions on how to improve services of Reportnet.



[Edit this section](Reportnet_Helpdesk_Services/edit.md)

### Tools

  * Keycloak: is the IAM (Identity and Access Management) tool used to control what users have access to certain resources
  * Graylog: is the console where all logs are shown so it is possible to retrieve information from EEA Test and Production Environment



[Edit this section](Reportnet_Helpdesk_Services/edit.md)

### Keycloak

[Edit this section](Reportnet_Helpdesk_Services/edit.md)

#### Environment

There are 3 environments for keycloak. Below can be found the admin console for all of the environments: 

  * Test env: <https://rn3auth.eionet.europa.eu/auth/>
  * Staging env: <https://rn3staging-auth.eionet.europa.eu/auth/> \--> this environment is not publicly accessible, it must be accessed via vpn. Only for EEA Test purposes
  * Production: <https://auth.reportnet.europa.eu/auth/>



[Edit this section](Reportnet_Helpdesk_Services/edit.md)

#### Security System and Helpdesk Service acting scenarios

Every user that wants to access to Reportnet will require to have an access in EuLogin. A complete guide can be found here: <https://www.eionet.europa.eu/reportnet/docs/howto_login-reportnet3-0-v1-0.pdf>

[Edit this section](Reportnet_Helpdesk_Services/edit.md)

##### Preloading a Reportnet 3 User on Keycloak.

However, as Helpdeks Service it is possible to be required to create a new user in the system (preload the user). So for this log in as admin in the Admin Console using the endpoints listed above and then follow these steps: 

  1. Click on User on Left Vertical panel
  2. Click on Add User button
  3. Fill the fields with user information
  4. Once it is created click on Credentials tab and set as credentials: ![](reportnet3.0)
  5. Uncheck Temporary checkbox, this password will be used only once
  6. Click on Role Mapping Tab and Select the desired Role.
  7. Click on Add Selected Button.



[Edit this section](Reportnet_Helpdesk_Services/edit.md)

##### Activating/Deactivating Rights for a given User

Thare are two level of rights for an User: Roles and Group.

The Role allows the User to perform generic actions on the System: 

  * DATA_CUSTODIAN: Can list Dataflows in which the User takes part, Create new dataflows, See Dataflow reporting statistics, add contributors to a dataflow, add new Lead Reporters to a dataflow , See all the Datasets in a Dataflow in which the User takes part among others
  * LEAD_REPORTER: Can list Dataflows in which the User takes part



The Groups allow Users to perform actions on a Reportnet Object. A group name has the following pattern: Object-Id-ROLE, for instance: Dataflow-10-DATA_CUSTODIAN.  
If an user is in the group Dataflow-10-DATA_CUSTODIAN, that user will be able to perform DATA_CUSTODIAN actions on the Dataflow with id=10. These actions involves actions such as Creating Schemas, Uploading Documents, Removing the dataflow (if it is in design Status)...

So, if it is necessary to manually give access to a user to some resource it is enough if you add the user to the proper group. The same happens to remove access for an User in a specific Object. As a possible scenario let's say Helpdesk Service receives the following ticket:

I am the User X (LEAD_REPORTER). The User Y (DATA_CUSTODIAN) has created a dataflow and I have been assigned as a LEAD_REPORTER for my Country (Denmark). I have spoken with the DATA_CUSTODIAN and he/she has passed me the following url in which I should be able to find the dataset: <http://reportnet.europa.eu/dataflow/10/dataset/65>, however, I cannot see neither the Dataflow nor the Dataset. Can you please help me with this?

The ticket reporter is the User X which is a LEAD_REPORTER, so it is necessary to see it that reporter is in the proper group for the Dataflow: Dataflow-10-LEAD_REPORTER. It turns out that the user is not in that Group. It is necessary to go to the User profile in Keycloak, and click on tab Groups, search in Available Group (there is a search box) the proper group and Click Join. The User can now list the Dataflow in the landing page as LEAD_REPORTER and can access it just clicking on it. Now it is necessary to do the same with the Dataset group: Dataset-65-LEAD_REPORTER. If the User was not in this group then nothing will be shown upon opening the Dataflow. When the user gets in the right Group the Dataset will be shown and the User will be able to access it as a LEAD_REPORTER.

Depending on the kind of object there will be different kind of groups:  
Dataflow: 

  * DATA_CUSTODIAN: Users in this group will be able to Update/Delete the Dataflow itself adding Documents, Schemas, Lead Reporters and Contributors
  * LEAD_REPORTER: Users in this group will be able to see the Dataflow in the Landing Page.
  * EDITOR_WRITE: Users in this group will be able to create and edit Dataschemas as well the data inside them for the given Dataflow
  * EDITOR_READ: Users in this group only will be able to see the schemas created in the Dataflow, not access them
  * REPORTER_WRITE: Users in this group will be able to see the Dataflow on their landing pages as Reporter with basic write permissions on a single Dataset
  * REPORTER_READ: Users in this group only will be able to see the Dataflow on their landing pages as Reporter basic read write permissions on a single Dataset

Dataset: 
  * DATA_CUSTODIAN: Users in this group will be able to see data in the Dataset but will not have the chance to execute any action, just read mode
  * LEAD_REPORTER: Users in this group will be able to manage information in the Dataset as well as executing validations or releasing the information to the Data Collection or creating Snapshots
  * REPORTER_WRITE: Users in this group will be able to see the Dataset as Reporter with basic write permissions on a single Dataset
  * REPORTER_READ: Users in this group only will be able to see the Dataset as Reporter basic read write permissions on a single Dataset

Dataschema: 
  * DATA_CUSTODIAN: Users in this group will be able to 
  * EDITOR_WRITE: Users in this group will be able to edit Dataschemas
  * EDITOR_READ: Users in this group only will be able to see the schemas created in the Dataflow

Datacollection: 
  * DATA_CUSTODIAN: Users in this group will be able to see data in the Data Collection

EUDataset: 
  * DATA_CUSTODIAN: Users in this group will be able to see data in the Eu Dataset



Though by model it is feasible to add a User with LEAD_REPORTER role to a DATA_CUSTODIAN group (Dataflow-10-DATA_CUSTODIAN) it must not be done for coherence and security.

[Edit this section](Reportnet_Helpdesk_Services/edit.md)

### Graylog

Is a Log Aggregation console where Logs of different systems can be viewed in order to see what is happening. It is accessible through this link: <https://logs.eea.europa.eu/streams/5e48016bc2020e0012badef2/>

Currently there are two data stream for Reportnet 3: one coming from EEA Test Environment and the other one for EEA Production Environment.

## Verification notes

**Keycloak — confirmed in use.** Keycloak is the active identity and access management system. The `user-management-service` source code confirms this: `KeycloakConnectorServiceImpl` calls the Keycloak Admin REST API for all user and group operations. The three environment URLs listed in this document (Test, Staging, Production) are plausible but cannot be verified from source code alone, as they are deployment configuration values rather than code artefacts.

**Role and group model — partially outdated.** The role model described in this document reflects an earlier version of the platform. The current `SecurityRoleEnum` in `common-interfaces` defines the following roles: `DATA_CUSTODIAN`, `DATA_STEWARD`, `STEWARD_SUPPORT`, `DATA_OBSERVER`, `DATA_REQUESTER`, `LEAD_REPORTER`, `REPORTER_READ`, `REPORTER_WRITE`, `EDITOR_READ`, `EDITOR_WRITE`, `REPORTER_PARTITIONED`, `NATIONAL_COORDINATOR`, and `ADMIN`. The wiki omits `DATA_STEWARD`, `STEWARD_SUPPORT`, `DATA_OBSERVER`, `DATA_REQUESTER`, `REPORTER_PARTITIONED`, and `NATIONAL_COORDINATOR`. It also describes `DATA_CUSTODIAN` at the Dataset level as "read mode only", whereas the UMS documentation confirms that `DATA_CUSTODIAN` has full administrative control; the wiki's description of Dataset-level custodian access as "just read mode" is misleading. Helpdesk staff assigning roles via Keycloak may encounter groups that are not listed here.

**Graylog — log aggregation system referenced but not in source code.** The Graylog URL (`https://logs.eea.europa.eu/streams/5e48016bc2020e0012badef2/`) is an external operational URL and cannot be confirmed or denied from the application source. The source code uses Filebeat with Logstash output (see `api-gateway/filebeat.yml`), which is a common upstream feeder for Elasticsearch/OpenSearch or Graylog pipelines. Whether logs still flow to the specific Graylog stream URL is a deployment concern that should be confirmed with EEA infrastructure.

**"Support" references in communication-service.** The communication-service contains no helpdesk-specific logic. The three Java files that matched the search (`WebsocketChannelInterceptor.java`, `WebSocketConfiguration.java`, `EmailConfiguration.java`) reference the word "support" only in code comments about STOMP protocol support. There is no helpdesk email routing, ticket creation, or dedicated support notification template in the communication-service code.

**System notifications for maintenance.** The document does not mention the `SystemNotification` feature in the Communication Service, which is the actual mechanism for broadcasting maintenance messages to all logged-in users. This is a gap for helpdesk staff who need to post or clear a maintenance banner.
