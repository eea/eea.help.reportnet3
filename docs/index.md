# Reportnet 3 documentation

Reportnet 3 is the European Environment Agency's platform for environmental data reporting. Countries and organisations submit data against reporting obligations, the platform validates it against quality control rules, and the accepted data is released into data collections for downstream use.

This site holds two kinds of documentation, aimed at different readers.

## User guide

How to use the platform through its web interface, and how to drive it programmatically through the REST API. Written for the people who report data and for the people who design the dataflows they report into.

- [Reporter](01_user-guide/reporter/index.md) — submitting, validating and releasing data
- [Requester](01_user-guide/requester/index.md) — creating dataflows, dataset schemas and quality control rules
- [Rest API](01_user-guide/rest-api/index.md) — import, export, validation and job polling endpoints

This section is migrated from `help.reportnet.europa.eu` and keeps that site's page order.

## Developer and operations documentation

How the platform is built: the microservice architecture, the domain model behind each service, the data stores, and the operational runbooks. Written for developers joining a service, and for anyone who needs a mental model of how the pieces fit together without reading source code.

See `architecture.md` for the system diagram and the per-service deep dives it links to.
