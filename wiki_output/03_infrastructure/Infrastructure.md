---
title: "Infrastructure"
---

# Infrastructure

[Edit this section](Infrastructure/edit.md)

## Architecture

Reportnet 3 final architecture is available on the [Eionet project page](https://projects.eionet.europa.eu/reportnet-3.0/library/03-executing/02-projects/05-development/03-deliverables/02-final-architecture)

[Edit this section](Infrastructure/edit.md)

## Services

The Reportnet 3 infrastructure consists of the following services: 

  * **Consul** : Service discovery and configuration.
  * **Mongo DB** : database for documents and database schema.
  * **PostgreSql** : database for dataflow and dataset.
  * **PgPool** : middleware that works between PostgreSQL servers and a PostgreSQL database client. Works as cache, load-balancer, server replication.
  * **Kafka** : : open-source stream-processing software platform. 
  * **Zookeeper** : centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services.
  * **Keycloak** : Authentication and permissions management.
  * **ElasticSearch** : Search engine 
  * **Redis** : open-source, in-memory data structure store, used as a database, cache and message broker. It supports data structures such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs, geospatial indexes with radius queries and streams
  * **Reportnet’s microservices** : 
    * ApiGateway
    * Dataset
    * Dataflow
    * Recordstore
    * Communication
    * Validation
    * IndexSearch
    * Frontend
    * Inspire
    * Collaboration
    * User Management

## Verification notes

This page is an index page with a short component list. The following observations were identified.

**Services list is incomplete.** The page lists eleven microservices: ApiGateway, Dataset, Dataflow, Recordstore, Communication, Validation, IndexSearch, Frontend, Inspire, Collaboration, and User Management. The source tree at `/Users/janbliki/Documents/GitHub/eea.reportnet3/` contains two additional services not on this list: `orchestrator-service` and `maintenance-service`. The Orchestrator is a central job coordinator and its omission from any infrastructure overview is a meaningful gap.

**Rod Service omitted.** The ROD Service (`rod-service` in source) is not listed, although it is listed in `Environments.md` as a deployed service in every environment.

**Infrastructure components confirmed.** Consul, MongoDB, PostgreSQL, PgPool, Kafka, Zookeeper, Keycloak, Elasticsearch, and Redis are all confirmed as infrastructure components by the source-derived `kubernetes.md`, `consul.md`, `kafka.md`, and `keycloak.md`.

**Zookeeper listed separately.** Zookeeper is listed as a standalone service. This is accurate — it is a separate StatefulSet from Kafka — but the source-derived `kubernetes.md` notes that Zookeeper will be replaced when Kafka upgrades to KRaft. Listing it as a permanent component without that caveat may mislead readers.

**Architecture link is broken.** The link to "Eionet project page" for the final architecture points to an internal EEA SharePoint/Eionet URL that is not accessible outside the EEA network. No public or repository-accessible alternative is provided.

**Redis described incorrectly.** The description calls Redis "open-source, in-memory data structure store, used as a database, cache and message broker" and lists support for streams. While Redis does support all of these generically, in Reportnet3 Redis is used specifically for distributed locking and caching, not as a message broker. The Kafka broker is what Reportnet3 uses for message passing.
