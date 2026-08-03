# About

Reportnet 3 is the European Environment Agency's platform for environmental data reporting. Countries and organisations submit data against reporting obligations, the platform validates it against quality control rules, and the accepted data is released into data collections for downstream use.

These pages explain how to use the platform, and how to drive it programmatically.

## Where to start

The documentation is organised around what you are trying to do rather than around the software's internal structure, so the section you want depends on your role in a dataflow.

**[General](general/index.md)** covers the things everyone needs first: getting an EU Login account, linking it to Reportnet, multi-factor authentication, and your user settings.

**[Reporters](reporter/index.md)** is for the people who submit data. It walks through the full cycle — finding your dataflow, importing and editing data, running validations, and releasing to a data collection.

**[Requester](requester/index.md)** is for the people who design what gets reported. It covers creating dataflows and dataset schemas, writing quality control rules including custom SQL validations, and managing reference data and lead reporters.

**[Rest API](rest-api/index.md)** documents the import, export and validation endpoints, how to authenticate with an API key, and how to poll a job for its status. This is the section to read if you are integrating FME or your own scripts.

**[Webforms](webforms.md)** and **[Preparation datasets](preparation-datasets.md)** cover two more specialised parts of the platform.

## About these pages

This documentation was migrated from `help.reportnet.europa.eu` and keeps that site's page order. Every page carries an "Edit this page" link that opens the source file on GitHub, so corrections can be proposed as a pull request.

Developer and operations documentation — the microservice architecture, per-service deep dives, the data model and operational runbooks — lives in the same repository but is not yet part of this site. See the repository README.
