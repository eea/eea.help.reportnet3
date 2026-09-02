# QC Rule Types and How They're Applied: Understanding What's Checked and Why

## Overview

This page explains how QC (validation) rules are created and applied in Reportnet — the different rule types, and which of them are generated automatically versus which must be added manually.

It serves two audiences:
- **Custodians**, designing a dataflow, can see at a glance which checks are **already in place automatically** once the schema is defined, so they can focus their effort on adding only the **custom checks** still needed on top of that, without creating rules that duplicate or conflict with what already exists.
- **Reporters**, submitting data, can understand **what is being checked and why** — so a validation error is not just a message to fix, but something traceable to a specific, understandable rule (automatic or custom).

### How this differs from the existing Reportnet Help pages

The official Reportnet Help site (help.reportnet.europa.eu) already documents QC rules in detail — see "Manage quality control rules" and "Custom validations (SQL)" — but from a **how-to / UI-navigation** angle: which button to click, which dialog tab to open, how to fill in each field of the rule builder.

This page has a different purpose. It is organized by **rule category and origin** (Mandatory / Expression / Custom, automatic vs. custodian-created) rather than by UI step, so that both custodians and reporters can answer questions the existing docs don't directly address:
1. *What checks already exist automatically once a schema is designed, so they aren't recreated?*
2. *How is a rule set planned so that no two QCs end up responding to the same underlying error?*
3. *What kind of check is behind a given validation error, and why does it exist?*

For the step-by-step mechanics of actually creating a rule in the interface, refer to the official "Manage quality control rules" and "Custom validations (SQL)" pages; this page is meant to be read alongside them, not as a replacement.

Validation rules are grouped into three categories:

- **Mandatory Rules** – structural checks that data must always satisfy (presence, type, schema).
- **Expression Rules** – logical/value-based checks comparing fields or values.
- **Custom Rules** – SQL-based checks for more complex or cross-dataset logic.

---

## 1. Mandatory Rules

Mandatory rules validate the basic structural integrity of the dataset before any deeper logic is applied.

### 1.1 Existence
Checks whether required data is present. This includes:
- **Mandatory** – the field/attribute must contain a value.
- **Primary Keys** – the field(s) designated as primary key(s) must be present and populated.
- **Cardinality** – the number of occurrences of a field or record must respect the defined minimum/maximum (e.g., 0..1, 1..1, 1..n).

### 1.2 Type Check
Verifies that the value provided matches the expected data type:
- Integer
- Geometry
- Boolean
- Text
- **Enum** – the value must belong to a defined set of allowed values. This can be implemented in two ways:
  - **Predefined list (type enum)** – the allowed values are fixed and defined directly in the type/schema definition.
  - **Reference field** – the allowed values are not fixed in the schema but instead derived from a list of values held in a reference dataset (i.e., the enum is validated dynamically against reference data rather than a static list).

### 1.3 Schema Rules
Validates the dataset against the expected schema definition:
- **Table columns** – the columns present must match those defined in the schema.
- **Table names** – the tables submitted must match the expected table names.

---

## 2. Expression Rules

Expression rules evaluate the value(s) of one or more fields using logical or comparative expressions.

### 2.1 Comparison
Compares a field's value against another field, a fixed value, or a pattern:
- Greater than / Lower than
- Equal to
- Partial match (e.g., contains, starts with)

### 2.2 Conditional Comparison
Applies a comparison only when a specified condition is met (e.g., "if Field A meets condition X, then Field B must satisfy comparison Y").

---

## 3. Custom Rules

Custom rules allow validation logic to be expressed directly in SQL, enabling more complex or cross-referenced checks that go beyond standard field-level rules.

### 3.1 SQL on Reporters Data
SQL queries executed directly against the data submitted by the reporter, without referencing external datasets.

### 3.2 SQL on Reference vs Reporting Data
SQL queries that compare the reporter's submitted data against a reference dataset (e.g., checking consistency with an official reference list or master data source).

### 3.3 SQL on Ranges of Reference Data
SQL queries that validate whether submitted values fall within an expected range defined in a reference dataset (e.g., valid value ranges, valid code lists, allowed intervals).

---

## 4. Rule Origin: Automatic vs Custom Rules

All validation rules are executed together — there is no conditional gating between rules. What differs is **how each rule is created** and **who is responsible for it**. This distinction is the key thing a custodian needs to know before adding a new QC: is this check already generated automatically, or does it need to be built manually?

### 4.1 Automatic rules (generated by Reportnet)

As soon as a custodian designs a dataflow and defines the schema (tables, fields, field types, primary keys, links), Reportnet **automatically generates** the corresponding QC rules — no manual configuration is required. Examples include:

- **Mandatory / Required field** – triggered whenever a field is marked as required (including automatically for any field set as Primary Key).
- **Type check** – triggered by the field type selected in the schema (Integer, Boolean, Geometry, Enum, etc.).
- **Table type unique Constraint** – added automatically when a field is marked as Primary Key (or otherwise set as unique), checking that values are unique within the table.
- **Field type LINK** – added automatically when a field is configured as a Link or External Link to another table, checking that the value exists in the linked (parent/reference) table.
- **Table Completeness** – added automatically when the "All PK values must be used on link" option is enabled on a link, checking that all parent-table PK values are also present in the child table.

These automatic rules default to **BLOCKER** severity and can be reviewed (and their metadata/message edited) at any time from the "QC Rules" dialog, alongside any manually added rules.

### 4.2 Custom rules (added by the custodian)

Anything beyond the schema-driven checks above must be **added and tested manually** by the custodian. This covers:

- **Expression rules** – Field comparison and If-then (conditional) row constraints.
- **Custom SQL rules** – SQL on reporter data, SQL comparing reference vs. reporting data, and SQL validating ranges against reference data.
- **Table/row constraints and additional uniqueness constraints** not already covered by a PK or Link.

In short: schema design gives a custodian a baseline set of checks "for free" (existence, type, uniqueness, link integrity). Everything else — business logic, cross-checks, ranges, conditional rules — needs to be deliberately created and validated by the custodian in the "QC Rules" dialog.

---

## 5. Controlling Validation Flow (Best Practices)

Since all rules are executed regardless of one another's outcome, planning the rule set carefully — before adding custom QCs — is what keeps validation results clear and useful. This comes down to two principles:

### 5.1 Avoid overlap with automatic rules

Before creating a custom QC, check the "QC Rules" dialog to confirm the check doesn't already exist as an automatic rule (see Section 4.1). A custom rule should only be added for checks that:
- are **not already covered** by an automatic rule (e.g. Mandatory, Type check, Table type unique Constraint, Field type LINK, Table Completeness), and
- represent genuine additional business logic specific to the dataflow.

Adding a custom rule that duplicates an existing automatic one creates redundant validation effort and, more importantly, risks **two QCs firing on the same underlying error** — which is confusing for the reporter (two error messages for one root cause) and harder for the custodian to maintain (a schema change now needs to be reflected in two places instead of one).

### 5.2 Plan the rule set to avoid duplicate error responses

More generally, when adding multiple custom rules — or a custom rule alongside an automatic one — check that no two QCs are designed to respond to the same underlying condition. Before adding a new rule, ask: *if this check fails, will another existing rule also fail for the same reason?* If so, keep only the one that gives the clearest, most specific error message, and remove or adjust the other.

Two concrete patterns help with this:

1. **Confirm field presence first** – use **Mandatory field** rules to make sure required fields actually contain values. This makes it clear, when reviewing results, whether a failure elsewhere is due to missing data or an actual data quality issue — rather than letting a downstream Expression or SQL rule fail for the same underlying reason with a less specific message.
2. **Validate sequences/ranges with Custom SQL** – use a **Custom SQL rule** to check the full range or sequence of values at once, rather than relying on multiple isolated field-level checks. This ensures sequence-dependent logic (e.g., continuous ranges, ordered values) is validated consistently across the whole dataset, through a single rule rather than several overlapping ones.

Following this design pattern — existence checks kept separate from range/sequence validation via SQL, and no custom rule duplicating an automatic one — keeps validation results clear, since each failure can be traced to one specific rule and root cause, even though all rules run independently and simultaneously.
