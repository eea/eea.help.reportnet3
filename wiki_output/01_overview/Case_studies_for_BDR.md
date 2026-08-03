---
title: "Case studies for BDR"
---

# Use cases for BDR

[Edit this section](Case_studies_for_BDR/edit.md)

## 1) Reporter

Role in BDR: local role on the respective company of `Owner`

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 1: Registration and update of company details and reporters for ODS/F-gases obligations

**Description** : Company representatives register the required company details for their company in the respective [European registry](https://webgate.ec.europa.eu/ods2/ "DG CLIMA"). They update these details each time there is a change in the company's activity or details. In addition, representatives register the persons/accounts which will be able to report under each obligation; the list of reporters is kept updated in time by the company. Following the registration, the company data is automatically harvested in the [BDR European (Cache) Registry](https://bdr.eionet.europa.eu/european_registry/) and used by BDR in the reporting process.

**Trigger** : A company has to report for ODS or F-gases and needs to register or update its details

**Precondition** : Company receives an email from EEA/DG CLIMA, with instructions on how to register their data and reporters

**Normal course** : 

  1. At the beginning of each reporting cycle, company designates a representative to fill in the company data into the respective [European registry](https://webgate.ec.europa.eu/ods2/ "DG CLIMA")
  2. If the representative doesn't have an EU Login account, if (s)he one creates one
  3. Representative logs in the DG CLIMA registry, chooses the right obligation and: 
    1. if the company is not yet registered, creates a new company profile for his/her company, filling in all the fields from the form. The next step is to define the other EU Login accounts that will have rights to report and see reports for that company
    2. if the company is already registered and the company data or list of reporters needs an update, edits the form and fills in the details and list of EU Login users
  4. Details are registered in the DG CLIMA registry they become available for harvesting in the DG CLIMA API for companies
  5. All company representatives must log in the European registry (DG CLIMA) using their EU Login accounts, before being able to see the company's reporting folder in BDR
  6. BDR picks up the feed at regular intervals, registers the new company or updates the record of the existing one, also updating the list of reporters
  7. BDR creates the reporting folder for the company and assigns the roles for the reporters or, if the company already existed, updates the list of reporters



**Alternative course** : n/a

**Acceptance criteria** : 

  1. The details of the new or updated company appears in the [BDR's European Registry](https://bdr.eionet.europa.eu/european_registry/organisation_listing) for the respective obligation
  2. Reporting folder for the company exists in BDR, under the respective country and the tab "Company details" presents the updated data
  3. All users declared as reporters, who previously logged in the European registry (DG CLIMA) see the link to their company on the first page of BDR after login in BDR



**Exception(s)** : n/a

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 2: Provide company details and register reporters for CARS/VANS obligations

**Description** : Company representatives register the required company details for their company in the [BDR Local registry](https://bdr.eionet.europa.eu/registry/). They update these details each time there is a change in the company's activity or details. In addition, representatives register the persons/accounts which will be able to report under each obligation; the list of reporters is kept updated in time by the company.

**Trigger** : A company has to report for CARS or VANS obligations and needs to register or update its details

**Precondition** : Company receives communication from the EEA, with instructions on how to register their data and reporters

**Normal course** : 

  1. At the beginning of each reporting cycle, company designates a representative to fill in or update the company data into the respective [BDR Local Registry](https://bdr.eionet.europa.eu/registry/)
  2. If a new company needs to register, their representative accesses the [specific page for CARS/VANS registration page](https://bdr.eionet.europa.eu/registry/self_register/) and fills in the company details, as well as the data of the first representative 
    1. the company is registered in the database, but no accounts or reporting folder are created at this time
    2. notification emails are sent to the group from the Eionet helpdesk responsible for these obligations, containing the company details
    3. Eionet Helpdesk accesses the new company data from the BDR Registry, reviews the record and, if they decide that the company is valid, validate the account of the representative representative and create the reporting folder 
      1. the representative receives an automated email with login details, send in BCC to the BDR Helpdesk address
    4. if the Eionet Helpdesk considers the record not valid, they can delete the record of the company 
  3. If the company is already registered, all representatives that have reporter accounts for that company see 2 links on the front page of BDR, after logging in: 
    1. link to update the company details page, which allows editing the company data and adding new contact persons 
      1. when added, the new contact persons receive automated emails with login details 
    2. link to the reporting folder

**Alternative course** : 

  1. The Eionet Helpdesk can also register company details for these two obligations, see the corresponding use case below

**Acceptance criteria** : 

  1. The details of the new or updated company appear in the BDR's Local Registry for the respective obligation
  2. Reporting folder for the company exists in BDR, under the respective obligation and the tab "Company details" presents the latest data
  3. All users declared as reporters have links to update their company details and to access the reporting folder on the front page of BDR, after logging in



**Exception(s)** : n/a

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 3: Provide company details and register reporters for HDV obligation

**Description** : Company representatives register the required company details for their company in the [BDR Local registry](https://bdr.eionet.europa.eu/registry/). They update these details each time there is a change in the company's activity or details. In addition, representatives register the persons/accounts which will be able to report under each obligation; the list of reporters is kept updated in time by the company.

**Trigger** : A company has to report for HDV obligation and needs to register or update its details

**Precondition** : Company receives communication from the EEA, with instructions on how to register their data and reporters

**Normal course** : 

  1. At the beginning of each reporting cycle, company designates a representative to fill in or update the company data into the respective [BDR Local Registry](https://bdr.eionet.europa.eu/registry/)
  2. If a new company needs to register, their representative accesses the [specific page for HDV registration page](https://bdr-test.eionet.europa.eu/registry/self_register_hdv/) and fills in the company details, as well as the data of the main contact point 
    1. the company is registered in the database, but no user accounts or reporting folder are created at this time
    2. notification emails are sent to the group from the Eionet helpdesk responsible for these obligations, containing the company details
    3. Eionet Helpdesk accesses the new company data from the BDR Registry, reviews the record and, if they decide that the company is valid validate the account of the representative, designate this account as "account owner" and create the reporting folder 
      1. the representative receives an automated email with login details, with the BDR Helpdesk address in BCC
    4. if the Eionet Helpdesk considers the record not valid, they can delete the record of the company 
  3. If the company is already registered, all representatives that have reporter accounts for that company see 2 links on the front page of BDR, after logging in: 
    1. link to update the company details page, which allows editing the company data, resetting the password, adding new contact persons and setting another account as "account owner" 
      1. when added, the new contact persons receive automated emails with login details 
    2. link to the reporting folder

**Alternative course** : 

  1. The Eionet Helpdesk can also register company details for these two obligations, see the corresponding use case below

**Acceptance criteria** : 

  1. The details of the new or updated company appear in the BDR's Local Registry for the respective obligation
  2. Reporting folder for the company exists in BDR, under the respective obligation and the tab "Company details" presents the latest data
  3. All users declared as reporters have links to update their company details and to access the reporting folder on the front page of BDR, after logging in 
  4. Both the account owner and the Eionet Helpdesk can set an "account owner" for the company



**Exception(s)** : n/a

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 4: Report on F-gases obligation

**Description** : Company submits a valid report for the obligation [Fluorinated gases (F-gases) reporting by undertakings](http://rod.eionet.europa.eu/obligations/713 "Regulation 2014"), which also includes submitting valid reports for one or both of the subsequent verification obligations: [Verification documents - HFC producers and bulk importers](https://bdr.eionet.europa.eu/fgases/at/9683/colwqavxgbi/) and [Verification documents - equipment importers](https://bdr.eionet.europa.eu/fgases/at/9683/colwqavxgei/)

**Trigger** : Country representatives wants to report on [F-gases](http://rod.eionet.europa.eu/obligations/713) and the subsequent verification obligation(s) for their company

**Precondition** : The company was previously registered in the European Registry and its details and list of reporters are up to date

**Normal course** : 

  1. Reporter logs in BDR using his/hers EU Login account and accesses the link to the company's reporting folder from the front page
  2. Reporter creates a new envelope (delivery container), activates the Draft task and adds a new file using the online webform
  3. Reporter fills in the fields of the webform and saves the work. This process can be done in different sittings, by saving the interim work
  4. Upon the completion of the webform and the internal successful validation, reporter submits the delivery to the EEA/DG CLIMA
  5. The envelope is released
  6. The Automatic QA/QC runs and places feedback in the envelope with the results of the tests 
    1. if the result is satisfactory (i.e. the Automatic QA/QC ran successfully and the result does not contain blockers), a receipt confirmation is posted in the envelope and the envelope is completed
    2. if the Automatic QAQC ran successfully, but the test results contain blockers, a negative confirmation of receipt is posted in the envelope and a new envelope is created, with the same file 
      1. EEA Thematic experts may post feedback in the old envelope about the data quality
      2. reporter continues the delivery in the newly created envelope and corrects the errors signaled in the previous envelope, following the instructions posted in the manual feedback, if they exist
    3. if the Automatic QA/QC encounters problems and does not return the correct and complete results, the envelope goes back to Draft and the reporter is informed that they need to submit the delivery again. This sometimes happens when the system is overloaded
  7. The process continues until the finalisation of a delivery with no blockers from the automatic quality assessment and no manual feedback asking the reporters to redeliver
  8. Upon the start of the reporting period for the verification obligations and upon the successful submission of the report on [F-gases](http://rod.eionet.europa.eu/obligations/713), reporter logs in BDR again and accesses the company's reporting folder
  9. Depending on the requirements for that company, reporter delivers a report for one or both verification obligations. For each of the obligation, the following steps are performed: 
    1. Reporter creates an envelope in the respective sub-folder for verification and activates the Draft task
    2. Reporter starts filling in the online webform and uploads the necessary documents
    3. Upon the completion of the webform, reporter saves the work and submits the envelope
    4. Ahe Automatic QA/QC runs and places feedback in the envelope with the results of the tests 
      1. if the result is satisfactory (i.e. the Automatic QA/QC ran successfully and the result does not contain blockers), the envelope is Released, a receipt confirmation is posted in the envelope and the envelope is completed
      2. if the Automatic QAQC ran successfully, but the test results contain blockers, the envelope is directed back to Draft
      3. if the Automatic QA/QC encounters problems and does not return the correct and complete results, an automatic feedback asking the user to redeliver later is posted in the envelope the envelope goes back to Draft 
    5. This second reporting process continues until the finalisation of a delivery with no blockers from the automatic quality assessment



**Alternative course** : n/a

**Acceptance criteria** : 

  1. The reporting folder of the company contains at least one valid report (envelope) for the [F-gases](http://rod.eionet.europa.eu/obligations/713) obligation the chosen reporting year
  2. The latest report for the [F-gases](http://rod.eionet.europa.eu/obligations/713) obligation for the chosen reporting year contains the results of the automatic quality assessment with no blockers and contains no manual feedback asking the reporters to redeliver
  3. One or both reporting sub-folders for the verification obligations contain valid reports (envelopes) for the chosen reporting year; the responsibility to submit reports for one or both of the verification obligations depend on the type of company
  4. The verification report(s) for the chosen reporting year contain(s) the results of the automatic quality assessment with no blockers



**Exception(s)** : n/a

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 5: Report on ODS obligation

**Description** : Company submits a valid report for the obligation [Ozone depleting substances (ODS) reporting by undertakings](http://rod.eionet.europa.eu/obligations/213 "Article 27")

**Trigger** : Country representatives wants to report on ODS

**Precondition** : The company was previously registered in the European Registry and its details and list of reporters are up to date

**Normal course** : 

  1. Reporter logs in BDR using his/hers EU Login account and accesses the link to the company's reporting folder from the front page
  2. Reporter creates a new envelope (delivery container), activates the Draft task and adds a new file using the online webform
  3. Reporter fills in the fields of the webform and saves the work. This process can be done in different sittings, by saving the interim work
  4. Upon the completion of the webform and the internal successful validation, reporter submits the delivery to the EEA/DG CLIMA
  5. The envelope is released
  6. The Automatic QA/QC runs and places feedback in the envelope with the results of the tests 
    1. if the result is satisfactory (i.e. the Automatic QA/QC ran successfully and the result does not contain blockers), a receipt confirmation is posted in the envelope and the envelope is completed
    2. if the Automatic QA/QC ran successfully, but the test results contain blockers, a negative confirmation of receipt is posted in the envelope and a new envelope is created, with the same file 
      1. EEA Thematic experts may post feedback in the old envelope about the data quality
      2. reporter continues the delivery in the newly created envelope and corrects the errors signaled in the previous envelope, following the instructions posted in the manual feedback, if they exist
    3. if the Automatic QA/QC encounters problems and does not return the correct and complete results, the envelope goes back to Draft and the reporter is informed that they need to submit the delivery again. This sometimes happens when the system is overloaded
  7. The process continues until the finalisation of a delivery with no blockers from the automatic quality assessment



**Alternative course** : n/a

**Acceptance criteria** : 

  1. The reporting folder of the company contains at least one valid report (envelope) for the chosen reporting year
  2. The latest report for the chosen reporting year contains the results of the automatic quality assessment with no blockers and contains no manual feedback asking the reporters to redeliver



**Exception(s)** : n/a

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 6: Report on CARS/VANS obligations

**Description** : Company submits a valid report for the obligations [Monitoring and reporting of average CO2 emissions (light commercial vehicles): Member States](http://rod.eionet.europa.eu/obligations/665) or [CO2 emissions from new passenger cars: Member States](http://rod.eionet.europa.eu/obligations/655)

**Trigger** : Country representatives wants to report on CARS or VANS obligations

**Precondition** : The company was previously registered in the BDR Local Registry and its details and list of reporters are up to date

**Normal course** : 

  1. Reporter logs in BDR using his/hers account and accesses the link to the company's reporting folder from the front page
  2. Reporter creates a new envelope (delivery container), activates the Draft task and uploads the delivery
  3. Upon the completion of upload, reporter submits the delivery 
  4. The envelope is released
  5. The Automatic QA/QC runs and places feedback in the envelope with the results of the tests
  6. Since the Automatic QA/QC does not return blockers, a receipt confirmation is posted in the envelope in all situations
  7. Reporter reads the results of the Automatic QA/QC and decide to finish the delivery (complete the envelope) or go back to Drafting and further edit the files 
  8. The process continues until the finalisation of a delivery



**Alternative course** : n/a

**Acceptance criteria** : 

  1. The reporting folder of the company contains at least one valid report (envelope), with a receipt confirmation



**Exception(s)** : n/a

[Edit this section](Case_studies_for_BDR/edit.md)

### Report on HDV obligation

**Description** : Company submits a valid report for the obligation [Reporting of data on new heavy-duty vehicles by manufacturers](http://rod.eionet.europa.eu/obligations/770)

**Trigger** : Country representatives wants to report on HDV obligation

**Precondition** : The company was previously registered in the BDR Local Registry and its details and list of reporters are up to date

**Normal course** : 

  1. Reporter logs in BDR using his/hers account and accesses the link to the company's reporting folder from the front page
  2. Reporter creates a new envelope (delivery container), activates the Draft task and uploads the delivery
  3. Upon the completion of upload, reporter submits the delivery 
  4. The Automatic QA/QC runs and places feedback in the envelope with the results of the tests
  5. If the result is satisfactory (i.e. the Automatic QA/QC ran successfully and the result does not contain blockers), the envelope is released and a receipt confirmation is posted in the envelope; the envelope is then automatically completed
  6. If the Automatic QAQC ran successfully, but the test results contain blockers, a negative confirmation of receipt is posted in the envelope, asking users to make the necessary corrections; the envelope goes back to Draft 
  7. If the Automatic QA/QC encounters problems and does not return the correct and complete results, the envelope goes back to Draft and the reporter is informed that they need to submit the delivery again. This sometimes happens when the system is overloaded
  8. The process continues until the finalisation of a delivery



**Alternative course** : n/a

**Acceptance criteria** : 

  1. The reporting folder of the company contains at least one valid report (envelope), with a receipt confirmation



**Exception(s)** : n/a

[Edit this section](Case_studies_for_BDR/edit.md)

## 2) Auditor

Roles in BDR: local role of on the respective obligation for EU or country of `Auditor`

It is relevant to note that, at the time of writing this document, no Auditors are assigned in BDR.

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 1: Search deliveries

**Description** : User searches the deliveries that have been started or released during a certain period of time, for a certain obligation and for a certain country.

**Trigger** : Auditors on a country (country representative) or for the EU (EU representative) want to search for certain deliveries into BDR

**Precondition** : User has been assigned the necessary role in BDR for the EU Login or LDAP account

**Normal course** : 

  1. User logs in BDR and accesses the [search interface](https://bdr.eionet.europa.eu/ReportekEngine/searchdataflow)
  2. User selects from the available filters and clicks "Search" 
  3. The search results are listed according to the filters 
    1. User can download all results from the released deliveries (envelopes) or just a subset of them, as selected



**Alternative course** : n/a

**Acceptance criteria** : 

  1. User receives results of the deliveries which: 
    1. match the filters
    2. the user has access to each of the results
    3. the Excel export provides of all results provides a zip file with the all released deliveries
    4. only released deliveries can be selected and the Excel export of the selection provides a zip file with the selected deliveries



**Exception(s)** : n/a

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 2: Inspect deliveries

**Description** : User inspects a delivery to which (s)he has access

**Trigger** : Auditors on a country (country representative) or for the EU (EU representative) want to inspect a delivery

**Precondition** : User has been assigned the necessary role in BDR for the EU Login or LDAP account and has obtained the link to the delivery by executing a search

**Normal course** : 

  1. User accesses the delivery by link
  2. User is able to inspect: 
    1. the list of documents submitted
    2. for each document can read the metadata, can download the file and can view the file onlline using the conversions available for that file type
    3. the envelope history
    4. the feedback posted in the envelope



**Alternative course** : n/a

**Acceptance criteria** : 

  1. For a delivery the user has rights to see, user is able to inspect: 
    1. the list of documents submitted
    2. for each document can read the metadata, can download the file and can view the file onlline using the conversions available for that file type
    3. the envelope history
    4. the feedback posted in the envelope



**Exception(s)** : n/a

[Edit this section](Case_studies_for_BDR/edit.md)

## 3) Data steward (EEA thematic expert) and Data custodian (EEA data management expert)

Role in BDR: local role on the respective obligation of `ClientCARS` / `ClientFG` / `ClientHDV` / `ClientODS`

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 1: Search deliveries

Same as Auditor

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 2: Inspect list of companies and reporters

**Description** : User inspects the list of companies registered for an obligation and its list of reporters / account owner (only for HDV)

**Trigger** : User wants to inspect the list of companies or an individual company with an issue or to find the reporting folder for a company

**Precondition** : User has been assigned the necessary role in BDR for the EU Login or LDAP account

**Normal course** : 

  1. For ODS/F-gases companies: 
    1. User logs in and accesses the Company listing of the [European (Cache) Registry](https://bdr.eionet.europa.eu/european_registry/organisation_listing)
    2. User chooses the obligation and counts the companies, browses through them
    3. User enters a search filter (country, part of a company name) and finds a short list of companies and accesses a certain company
    4. User clicks on the company and inspects its details, stocks/licenses/PAU allowances, list of users, link to the reporting folder and links to actions: "disable company" and "sync company" 
  2. For CARS/VANS/HDV: 
    1. User logs in and accesses the Company listing of the [BDR Registry](https://bdr.eionet.europa.eu/european_registry/organisation_listing)
    2. User filters the companies per the companies, browses through them and counts companies for a certain filter
    3. User enters a search filter (country, part of a company name) and finds a short list of companies and accesses a certain company
    4. User clicks on the company and inspects its details, list of users, link to the reporting folder and links to actions: "edit", "reset account", "post comment" and "add new person"



**Alternative course** : n/a

**Acceptance criteria** : 

  1. Companies and their users can be browsed and the actions for each obligation can be successfully performed



[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 3: Inspect deliveries

Same as Auditor

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 4: Provide feedback to deliveries and complete deliveries

**Description** : User is a EEA thematic expert and wants to post feedback to the reporter who submitted a delivery. This usually happens if the delivery lacks in quality and the user wants to communicate specifics about the errors made or inconsistencies to the reporter.

**Trigger** : EEA thematic expert wants to post feedback to the reporter who submitted a delivery

**Precondition** : User has been assigned the necessary role in BDR for the EU Login or LDAP account and the delivery is released by the reporter

**Normal course** : 

  1. User navigates to the delivery (envelope) (s)he wants to post feedback to
  2. User reviews the files and the result of the automatic quality assessment 
  3. User uses the button for adding feedback and fills in the title, description and adds attachments if necessary
  4. Optionally, user can complete the envelope, for the workflows that had created a different reporting envelope in case of quality assessment errors



**Alternative course** : n/a

**Acceptance criteria** : 

  1. Feedback is posted in the envelope, together with the attachments, if provided
  2. The intervention in the envelope history is done and the envelope is completed



[Edit this section](Case_studies_for_BDR/edit.md)

## 4) Eionet Helpdesk

Role in BDR: `Manager`

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 1: Create and update company profiles and reporters

**Description** : Eionet Helpdesk creates a company for the CARS/VANS or HDV obligations, or it updates a company details / list of users, at the request of the company representative

**Trigger** : Country representatives wants to report on CARS or VANS obligations

**Precondition** : A company has to report for one of the CARS / VANS / HDV obligation, needs to register or update its details and asks the Eionet Helpdesk to do it

**Normal course** :   
The process is similar to Provide company details and register reporters for CARS/VANS or Provide company details and register reporters for HDV, with the difference that the Eionet Helpdesk does not submit the

**Alternative course** : 

  1. Company representative provide company details and register reporters

**Acceptance criteria** : 

  1. The details of the new or updated company appear in the BDR's Local Registry for the respective obligation
  2. Reporting folder for the company exists in BDR, under the respective obligation and the tab "Company details" presents the latest data
  3. All users declared as reporters have links to update their company details and to access the reporting folder on the front page of BDR, after logging in
  4. For the HDV obligation, both the account owner and the Eionet Helpdesk can set an "account owner" for the company



**Exception(s)** : n/a

[Edit this section](Case_studies_for_BDR/edit.md)

### Use case 2: Send invitations, reminders and warnings to companies

**Description** : Eionet Helpdesk receives a request from the Data stewards / Data custodian for a certain obligation to send invitations to report, reminders or warnings to a list of companies that are registered to report for that obligation

**Trigger** : Eionet Helpdesk needs to send invitations to report, reminders or warnings to a list of companies that are registered to report for an obligation

**Precondition** : The list of companies that should receive the notification has been compiled for the type of notification that needs to be sent

**Normal course** : 

  1. Eionet Helpdesk user accesses the [BDR Notifications](https://bdr.eionet.europa.eu/notifications/) and sees the list of the reporting cycles defined in the system
  2. If the desired reporting cycle does not exist, the user creates it
  3. User accesses the reporting cycle and adds a new notification. A good practice is to create a test notification first, to send to the test companies for that obligation
  4. Having the possibility to reuse an existing template, user selects a template or starts from an empty one and continues to enter the subject and text
  5. The next step is to select the list of companies/representatives to send the message to. This can be done by uploading a CSV file or by selecting the companies from the list
  6. Messages are sent after the final confirmation and the finalisation of the steps 
    1. Each email is sent in BCC to [helpdesk@eionet.europa.eu](mailto:helpdesk@eionet.europa.eu), which opens and closes an Eionet OTRS ticket, for later followup



**Alternative course** : n/a

**Acceptance criteria** : 

  1. Emails are sent to the all representatives of the selected companies 
  2. Eionet OTRS has a closed ticket for each of the emails sent



**Exception(s)** : n/a

## Verification notes

No source code verification applicable — this page describes BDR (Business Data Repository) use cases from the Reportnet 2 era. BDR is a separate system; the use cases here do not correspond to Reportnet 3 code. The page is historical context, not current system documentation.
