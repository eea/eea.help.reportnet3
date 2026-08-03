# ROD Service

ROD stands for the Reporting Obligations Database. It is an external EEA system, publicly accessible at `rod.eionet.europa.eu`, that is the authoritative source for environmental reporting obligations across European member states. A reporting obligation is a legal requirement — derived from an EU directive, regulation, or international agreement — for countries to submit data on a specific topic to a specific organisation by a specific deadline.

Reportnet 3 does not own or replicate obligation data. Instead it reads obligations on demand from ROD's public REST API and holds only an `obligationId` integer inside each dataflow record. The ROD Service is the dedicated microservice that sits between the external ROD API and the rest of the Reportnet platform: it fetches data from ROD, assembles it into the shapes the platform needs, caches it, and exposes it to the Dataflow Service via Feign.

The ROD Service deliberately does not persist any obligation data. All obligation information is live data from ROD, refreshed on each cache miss.

## Flow overview

```mermaid
flowchart TD
    DF[Dataflow Service]
    ROD[ROD Service :9050]
    CACHE[(In-process cache\nJVM lifetime)]
    RODAPI[External ROD API\nrod.eionet.europa.eu]

    DF -->|Feign via Consul: rod\nGET /obligation/findOpened\nGET /obligation/{id}\nGET /obligation_client/\nGET /obligation_country/\nGET /obligation_issue/| ROD
    ROD -->|@Cacheable — check cache first| CACHE
    CACHE -->|cache miss| ROD
    ROD -->|GET /rest/obligation/findOpened\nGET /rest/obligation/{id}\nGET /rest/client/findAll\nGET /rest/country/findAll\nGET /rest/issue/findAll| RODAPI
    ROD -->|ObligationVO| DF
```

---

## Purpose in Reportnet

Each reporting dataflow in Reportnet is tied to exactly one ROD obligation. When a dataflow is created, the user selects an obligation from a filtered list drawn from ROD. The `obligationId` is stored in the `DATAFLOW` table in PostgreSQL. From that point on, the Dataflow Service fetches the full obligation detail from the ROD Service every time it needs to present obligation metadata to the client.

The obligation supplies the context that explains why a dataflow exists: who is legally required to report, what topic they are reporting on, when the report is due, and which legal instrument created the requirement. This context is surfaced in the dataflow list, in per-dataflow detail pages, in the country-level reporting view, and in the PDF submission receipt that reporters download after releasing their data.

---

## Architecture

The ROD Service runs on port `9050`, registers with Consul under the name `rod`, and is accessed by the rest of the platform via the API Gateway or directly via Feign using the Consul-registered name.

```
Browser / Dataflow Service
        │
        │  Feign (via Consul: "rod")
        ▼
  ROD Service :9050
        │
        │  Feign HTTP (via ${rod.url})
        ▼
  ROD External API
  rod3.devel6cph.eea.europa.eu  (dev default)
  rod.eionet.europa.eu          (production)
```

The external ROD URL is configured via the `ROD_URL` environment variable, defaulting to `rod3.devel6cph.eea.europa.eu`. It is read from Consul KV at `config/rod/rod.url`. Spring's `@EnableCaching` is active; all four outbound Feign calls are annotated with `@Cacheable` so that repeated requests within the cache lifetime hit local memory, not ROD.

---

## Outbound calls to ROD

The ROD Service makes HTTP GET requests to four paths under ROD's REST API. The base URL is `${rod.url}`.

| Path | Cache key | Parameters | Purpose |
|---|---|---|---|
| `GET /rest/obligation/findOpened` | `rod_obligation_cache` | `clientId`, `issueId`, `spatialId`, `dateFrom`, `dateTo` (all optional) | Returns all currently active (not terminated) obligations, optionally filtered |
| `GET /rest/obligation/{id}` | `rod_single_obligation_cache` | `id` (path) | Returns a single obligation by its numeric ID |
| `GET /rest/client/findAll` | `rod_client_cache` | none | Returns all client organisations registered in ROD |
| `GET /rest/country/findAll` | `rod_country_cache` | none | Returns all countries/spatial units registered in ROD |
| `GET /rest/issue/findAll` | `rod_issue_cache` | none | Returns all environmental issues registered in ROD |

There is no cache eviction configuration in the service; cache entries expire according to the default Spring Cache in-process behaviour (JVM lifetime). In practice the caches are effectively warm for the lifetime of the service instance.

---

## Data returned by ROD

### Obligation (raw)

The `Obligation` domain class represents one obligation document as returned by ROD's `/rest/obligation/findOpened` and `/rest/obligation/{id}` endpoints. The fields come from several joined tables inside ROD's own database, as noted in the comments.

| Field | Type | Source table in ROD | Notes |
|---|---|---|---|
| `obligationId` | Integer | Core obligation | The ROD obligation identifier. Stored in Reportnet's `DATAFLOW.OBLIGATION_ID` column. |
| `oblTitle` | String | Core obligation | Human-readable obligation title. |
| `description` | String | Core obligation | Free-text description of the obligation. |
| `terminate` | String | Core obligation | Whether the obligation has been terminated. |
| `eeaPrimary` | Integer | Core obligation | Flag indicating this is an EEA primary obligation. |
| `eeaCore` | Integer | Core obligation | Flag for EEA core obligations. |
| `flagged` | Integer | Core obligation | Generic flag field. |
| `overlapUrl` | String | Core obligation | URL to overlapping obligations. |
| `comment` | String | Core obligation | Editorial comment. |
| `parameters` | String | Core obligation | Additional parameters. |
| `hasDelivery` | String | Core obligation | Whether the obligation expects a delivery. |
| `authority` | String | Core obligation | The legal authority of the obligation. |
| `lastUpdate` | String | Core obligation | Date of last change to the obligation in ROD. |
| `lastHarvested` | Date | Core obligation | Date of last harvest by ROD's crawler. |
| `validSince` | Date | Core obligation | Date from which the obligation is valid. |
| `validTo` | Date | Core obligation | Date to which the obligation is valid (null = ongoing). |
| `coordinator` | String | Core obligation | Name of the coordinating contact. |
| `coordinatorUrl` | String | Core obligation | URL for the coordinator. |
| `coordinatorRole` | String | Core obligation | Role name of the coordinator. |
| `coordinatorRoleSuf` | String | Core obligation | Role suffix. |
| `nationalContact` | String | Core obligation | National contact name. |
| `nationalContactUrl` | String | Core obligation | National contact URL. |
| `responsibleRole` | String | Core obligation | Name of the responsible role. |
| `responsibleRoleSuf` | String | Core obligation | Responsible role suffix. |
| `nextDeadline` | Date | Core obligation | Next reporting deadline. |
| `nextDeadline2` | Date | Core obligation | Secondary deadline. |
| `nextReporting` | String | Core obligation | Free-text next reporting description. |
| `firstReporting` | Date | Core obligation | Date of first required report. |
| `continousReporting` | String | Core obligation | Whether reporting is continuous. |
| `dateComments` | String | Core obligation | Comments on date interpretation. |
| `reportFreq` | String | Core obligation | Reporting frequency label (e.g. "Annual"). |
| `reportFreqMonths` | String | Core obligation | Numeric frequency in months. |
| `reportFreqDetail` | String | Core obligation | Detailed description of the reporting frequency. |
| `formatName` | String | Core obligation | Name of the required reporting format. |
| `reportFormatUrl` | String | Core obligation | URL to the format specification. |
| `reportingFormat` | String | Core obligation | Identifier or code of the format. |
| `locationPtr` | String | Core obligation | Where deliveries should be sent. |
| `locationInfo` | String | Core obligation | Free-text location notes. |
| `dataUsedFor` | String | Core obligation | How the data will be used. |
| `dataUsedForUrl` | String | Core obligation | URL to usage information. |
| `coordRoleId` | String | `T_ROLE` | ID of the coordinating role. |
| `coordRoleUrl` | String | `T_ROLE` | URL of the coordinating role. |
| `coordRoleName` | String | `T_ROLE` | Name of the coordinating role. |
| `respRoleId` | String | `T_ROLE` | ID of the responsible role. |
| `respRoleName` | String | `T_ROLE` | Name of the responsible role. |
| `clientLnkFKClientId` | String | `T_CLIENT_LNK` | Foreign key linking obligation to a client. |
| `clientLnkFKObjectId` | String | `T_CLIENT_LNK` | Object ID in the client link. |
| `clientLnkStatus` | String | `T_CLIENT_LNK` | Status of the client link. |
| `clientLnkType` | String | `T_CLIENT_LNK` | Type of the client link. |
| `clientId` | String | `T_CLIENT` | Numeric client ID as a string, used to join against the client list. |
| `clientName` | String | `T_CLIENT` | Name of the client organisation. |
| `sourceId` | String | `T_SOURCE` | ID of the legal instrument (source). |
| `sourceTitle` | String | `T_SOURCE` | Full title of the legal instrument. |
| `sourceAlias` | String | `T_SOURCE` | Short alias for the legal instrument. |
| `spatialId` | String | `T_SPATIAL` | Comma-separated list of country/spatial IDs bound to this obligation. |
| `voluntary` | String | `T_RASPATIAL_LNK` | Whether participation is voluntary. |
| `issueId` | String | `T_ISSUE` | Comma-separated list of environmental issue IDs. |
| `selectedClients` | List\<String\> | Search helper | Clients selected in a search context. |
| `selectedFormalCountries` | List\<String\> | Search helper | Formal country selections. |
| `selectedVoluntaryCountries` | List\<String\> | Search helper | Voluntary country selections. |
| `selectedIssues` | List\<String\> | Search helper | Issue selections. |
| `deadlineId` | String | Search helper | Deadline filter identifier. |
| `delObligations` | String | Search helper | Related delegated obligations. |
| `relObligationId` | Integer | `T_OBLIGATION_RELATION` | Related obligation ID. |
| `oblRelationId` | String | `T_OBLIGATION_RELATION` | Relation ID. |
| `oblRelationTitle` | String | `T_OBLIGATION_RELATION` | Related obligation title. |
| `nextDeadlineFrom` | String | Advanced search | Start of deadline range filter. |
| `nextDeadlineTo` | String | Advanced search | End of deadline range filter. |
| `deliveryCountryId` | String | Delivery | Country ID for delivery filtering. |
| `deliveryCountryName` | String | Delivery | Country name for delivery filtering. |
| `anmode` | String | — | Analysis mode indicator. |

### Client (raw)

Returned by `GET /rest/client/findAll`. Represents an EEA client organisation that commissions reporting obligations.

| Field | Type | Notes |
|---|---|---|
| `clientId` | Integer | Numeric ID used to match against `Obligation.clientId`. |
| `name` | String | Full name of the organisation. |
| `acronym` | String | Acronym (e.g. "EEA"). |
| `shortName` | String | Short form of the name. |
| `address` | String | Street address. |
| `url` | String | Organisation website. |
| `email` | String | Contact email. |
| `postalCode` | String | Postal code. |
| `city` | String | City. |
| `description` | String | Free-text description. |
| `country` | String | Country name. |

### Country (raw)

Returned by `GET /rest/country/findAll`. Represents a geographic/spatial unit (EU member state, candidate country, or other spatial entity) that can be bound to an obligation.

| Field | Type | Notes |
|---|---|---|
| `spatialId` | Integer | Numeric ID matched against the comma-separated `Obligation.spatialId`. |
| `name` | String | Country or region name. |
| `type` | String | Spatial unit type (e.g. country, EU member state, group). |
| `twoLetter` | String | ISO two-letter country code where applicable. |
| `memberCountry` | String | Whether this is an EU member state. |

### Issue (raw)

Returned by `GET /rest/issue/findAll`. Represents an environmental topic area.

| Field | Type | Notes |
|---|---|---|
| `issueId` | Integer | Numeric ID matched against the comma-separated `Obligation.issueId`. |
| `issueName` | String | Name of the environmental issue (e.g. "Air", "Water", "Nature"). |

---

## Mapping to Reportnet VOs

The ROD Service does not pass all fields through. After fetching raw data from ROD it assembles a trimmed `ObligationVO` that carries only the fields Reportnet actually uses.

### ObligationVO — fields surfaced to the platform

| Field | Type | Source in raw Obligation | Notes |
|---|---|---|---|
| `obligationId` | Integer | `obligationId` | The primary key used everywhere inside Reportnet. |
| `oblTitle` | String | `oblTitle` | Displayed in the dataflow list and dataflow detail pages. |
| `description` | String | `description` | Shown in the dataflow detail view. |
| `validSince` | Date | `validSince` | Obligation validity start. |
| `validTo` | Date | `validTo` | Obligation validity end. |
| `comment` | String | `comment` | Editorial comment on the obligation. |
| `nextDeadline` | Date | `nextDeadline` | The deadline used when displaying upcoming deadlines. Also used as the filter when browsing obligations by deadline range. |
| `reportFreq` | String | `reportFreq` | Reporting frequency label. |
| `reportFreqDetail` | String | `reportFreqDetail` | Detailed frequency description. |
| `legalInstrument` | LegalInstrumentVO | assembled | Contains `sourceId`, `sourceTitle`, `sourceAlias` from the raw obligation, plus a `legalInstrumentLink` URL built at query time. |
| `client` | ClientVO | looked up by `clientId` | Full client record matched from the `/rest/client/findAll` list. |
| `countries` | List\<CountryVO\> | looked up by `spatialId` | All country records matched from `/rest/country/findAll` using the comma-separated `spatialId` list. Only populated for single-obligation lookups (`findObligationById`); not populated in the list view. |
| `issues` | List\<IssueVO\> | looked up by `issueId` | Environmental issue records matched from `/rest/issue/findAll`. Only populated for single-obligation lookups; not populated in the list view. |
| `obligationLink` | String | built | Set by the Dataflow Service (not by the ROD Service) as `${rod.url}/obligations/{obligationId}`. |

### Fields in the raw Obligation not surfaced in ObligationVO

The following fields are fetched from ROD but discarded during mapping: `eeaPrimary`, `eeaCore`, `flagged`, `overlapUrl`, `coordinator`, `coordinatorUrl`, `coordinatorRole`, `coordinatorRoleSuf`, `nationalContact`, `nationalContactUrl`, `responsibleRole`, `responsibleRoleSuf`, `terminate`, `reportFreqMonths`, `nextDeadline2`, `nextReporting`, `firstReporting`, `continousReporting`, `dateComments`, `formatName`, `reportFormatUrl`, `reportingFormat`, `locationPtr`, `locationInfo`, `dataUsedFor`, `dataUsedForUrl`, `authority`, `parameters`, `hasDelivery`, `lastUpdate`, `lastHarvested`, `coordRoleId`, `coordRoleUrl`, `coordRoleName`, `respRoleId`, `respRoleName`, `clientLnkFKClientId`, `clientLnkFKObjectId`, `clientLnkStatus`, `clientLnkType`, `clientName`, `selectedClients`, `selectedFormalCountries`, `selectedVoluntaryCountries`, `selectedIssues`, `voluntary`, `deadlineId`, `delObligations`, `relObligationId`, `oblRelationId`, `oblRelationTitle`, `nextDeadlineFrom`, `nextDeadlineTo`, `deliveryCountryId`, `deliveryCountryName`, `anmode`.

---

## How the Dataflow Service uses obligation data

### Dataflow list

When the Dataflow Service serves any of its paginated dataflow list endpoints it first calls `GET /obligation/findOpened` on the ROD Service (via Feign) with no filter parameters, retrieving all open obligations. It serialises the list to JSON and passes it as a parameter to a PostgreSQL native SQL query using `json_array_elements`. Inside that query a CTE called `obligationtable` unpacks the JSON and joins each obligation to its matching dataflow via `DATAFLOW.OBLIGATION_ID = obligation.obligationId`. This lets PostgreSQL filter, sort, and paginate dataflows by obligation attributes entirely inside a single SQL statement.

The obligation fields read out of the JSON inside these SQL queries are: `obligationId`, `oblTitle`, `description`, `validSince`, `validTo`, `comment`, `nextDeadline`, `legalInstrument.sourceTitle` (nested JSON extraction), `client`, `countries`, `issues`, `reportFreq`, `reportFreqDetail`.

After the SQL returns, the Dataflow Service loops over the results and sets the full `ObligationVO` onto each `DataFlowVO` by matching on `obligationId`. This two-step approach means the obligation metadata is never stored in PostgreSQL — it is always live from ROD.

### Country-level view

The `getDataflowsByCountry` method follows the same SQL injection pattern but additionally calls `dataflowVO.getObligation().setObligationLink(rodUrl + "/obligations/" + obligationId)` and `dataflowVO.getObligation().getLegalInstrument().setLegalInstrumentLink(rodUrl + "/instruments/" + sourceId)` to build external hyperlinks into the ROD website for each dataflow. These links let users navigate from the Reportnet dataflow view directly to the authoritative obligation and legal instrument pages on the ROD site.

### Public dataflows by obligation

The `getPublicDataflowsByObligation` method groups dataflows under their obligations rather than listing dataflows independently. It fetches all open obligations, sorts them by title, and for each obligation finds the matching public dataflows. The result is a `PaginatedObligationVO` in which each obligation entry carries its list of associated dataflows.

### Release receipt PDF

When a data reporter downloads a submission confirmation after releasing a dataset, the `DatasetSnapshotService` fetches the full `DataFlowVO` and uses `dataflow.getObligation().getObligationId()` and `dataflow.getObligation().getOblTitle()` to populate the receipt. The obligation title is printed on the PDF. A hard-coded URL `https://rod.eionet.europa.eu/obligations/{obligationId}` is also printed, pointing to the public ROD page for the obligation. This URL is hard-coded in the PDF generator rather than using the configurable `rod.url` property.

---

## Endpoints exposed by the ROD Service

These endpoints are available to other services within the platform. They are all marked `@ApiIgnore` so they are not advertised in the public Swagger UI.

| Method | Path | Returns | Notes |
|---|---|---|---|
| `GET` | `/obligation/findOpened` | `ObligationListVO` | Filterable list of open obligations. Filter params: `clientId`, `spatialId`, `issueId`, `deadlineDateFrom`, `deadlineDateTo` (epoch millis). Client and issue lists are not fetched in this path (performance optimisation) — only the obligation list and client lookup are performed. |
| `GET` | `/obligation/{id}` | `ObligationVO` | Single obligation with full client, country, and issue lookups. |
| `GET` | `/obligation_client/` | `List<ClientVO>` | All ROD clients. |
| `GET` | `/obligation_country/` | `List<CountryVO>` | All ROD countries. |
| `GET` | `/obligation_issue/` | `List<IssueVO>` | All ROD issues. |

### Deadline date filtering

When `deadlineDateFrom` is supplied but `deadlineDateTo` is not, the service treats `deadlineDateTo` as equal to `deadlineDateFrom` (same-day filter). Filtering is performed in-memory in Java after fetching all obligations from ROD: obligations are included only if their `nextDeadline` falls within the specified range, with a same-day tolerance check that compares year, month, and day-of-month independently to avoid timezone edge cases.

---

## Relationships with other services

The Dataflow Service is the primary consumer of the ROD Service. It calls `ObligationControllerZull` (the Feign client registered against the `rod` Consul name) in every method that returns a list of dataflows to users. No other service calls the ROD Service directly; all obligation data flows through the Dataflow Service.

The ROD Service calls the external ROD REST API. It has no outbound calls to any other Reportnet service.

---

## Configuration

| Consul key | Environment variable | Default | Notes |
|---|---|---|---|
| `config/rod/rod.url` | `ROD_URL` | `rod3.devel6cph.eea.europa.eu` | Base URL for calls to the external ROD API. Used both by the ROD Service's Feign clients and by the Dataflow Service when constructing `obligationLink` and `legalInstrumentLink` URLs. |

The ROD Service registers at Consul as `rod` and runs on port `9050`. No database or message broker is involved.
