---
title: "Geospatial Data Features"
source_url: https://help.reportnet.europa.eu/geospatial-data-features/
---

# Geospatial Data Features
**Geospatial Data in Reportnet 3 (RN3)**

_User Guide for Working with Points, Lines, Polygons & Coordinate Systems_

**Introduction**

This page explains how geospatial information (locations, shapes, areas) is handled in Reportnet 3 (RN3).
It covers:

  * Supported geospatial data types
  * Supported coordinate systems (EPSG codes)
  * Capabilities and limitations when using the Dremio backend
  * What happens from **import → validation → preview → export**

This guide is written for RN3 users, not developers.

**1\. What Is Geospatial Data?**

Geospatial data is information that includes a **location on Earth**.
Instead of only describing _what_ something is, it also describes _where_ it is.
RN3 supports geospatial fields across many reporting obligations.

**2\. Supported Geospatial Data Types in RN3**

RN3 supports standard **vector geometries** :

  * **Point** : A single coordinate.
  * **Multi-Point** : A collection of points.
  * **Line** : A path formed by several connected coordinates.
  * **Multi-Line** : Several lines stored as one geometry.
  * **Polygon** : A closed area boundary.

**3\. Coordinate Systems (EPSG Codes)**

When importing geospatial data, users must select the correct **EPSG code** , which tells RN3 how to interpret the coordinates.

Below are the three EPSG codes supported.

**EPSG:4326 — WGS84**

**The global standard used by GPS and web maps**

  * Coordinates are in **latitude/longitude**
  * Most common default
  * Works for global or general-purpose datasets

Use when:

  * Data comes from GPS
  * Data is provided in a global coordinate system
  * You are unsure what CRS was used

**EPSG:4258 — ETRS89**

**European-standard latitude/longitude system**

  * Similar to WGS84 but fixed to the European continent
  * Used by many national mapping agencies

Use when:

  * The reporting guidelines specify ETRS89
  * Data originates from official European datasets

**EPSG:3035 — LAEA ETRS89**

**A European projection in meters (Lambert Azimuthal Equal Area)**
Ideal for area-based datasets.

  * Coordinates are **X/Y in meters**
  * Best for **polygons** where area or extent matters

Use when:

  * Reporting land cover, habitats, Natura 2000 sites, etc.
  * National datasets say “LAEA 3035”
  * You work with large geospatial polygons

**Choosing the Wrong EPSG**

If the wrong CRS is selected, your geometry may:

  * appear in the wrong place
  * appear outside Europe
  * not appear at all

**4\. RN3 Capabilities & Limitations (with Dremio Backend)**

RN3 uses the Dremio backend to handle large datasets efficiently

**Capabilities**

**a. Supports large datasets**

RN3 can handle millions of rows, including geospatial fields.

**b. Stores geospatial geometries**

Points, lines, and polygons remain linked to their data.

**c. Map preview inside RN3**

Users can visually confirm that shapes appear in the right place.

**d. Automatic geometry validation**

RN3 detects:

  * invalid geometry text
  * missing or empty geometry fields

**e. Export including geometry**

Geometry fields are included in all supported export formats.

**Limitations**

**a. Import size limitation**

When importing data using Dremio, if the spatial data field size exceeds 60MB then a warning is thrown and the field will not be stored

**b. CRS (EPSG) options are limited**

Only WGS84 (4326), ETRS89 (4258), and LAEA-ETRS89 (3035) are available.

**5\. From Import to Export: How Geospatial Data Moves Through RN3**

Below is the complete workflow explained simply.

**Step 1 — Prepare Your File**

You prepare your dataset (e.g. CSV or Excel) with:

  * Attributes (ID, name, etc.)
  * Geometry (point/line/polygon)
  * CRS information (EPSG code)

**Step 2 — Import into RN3**

When you upload your file:

  1. RN3 identifies the dataset and table
  2. It checks whether the table allows importing
  3. It starts a background “import job”
  4. If the dataset uses Dremio, RN3 processes the file using the Big Data backend

You only see a progress indicator in the user interface.

**Step 3 — Validation**

RN3 automatically checks:

  * Required fields are present
  * Data types match the schema
  * Geometry is valid
  * Coordinates fit chosen EPSG
  * Business rules for the dataflow
  * Links to reference datasets (if applicable)

Errors or warnings are shown to the user.

**Step 4 — Export**

When exporting:

  1. You choose the dataset, table, and file format
  2. You can apply filters (optional)
  3. RN3 collects the data
  4. Geometry is included (typically as WKT text)
  5. The file is downloaded to your computer

Exports work for both normal and Dremio-based datasets.

**6\. Summary**

RN3 makes it possible to upload, validate, view, store, and export geospatial information in a controlled and user-friendly way.

**Supported:**

  * Points
  * Multi-points
  * Lines
  * Multi-lines
  * Polygons
  * 3 EPSG codes (4326, 4258, 3035)
  * Map preview
  * Large datasets (via Dremio)
