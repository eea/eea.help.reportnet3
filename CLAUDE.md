# Documentation Guidelines

This file describes how documentation in this folder should be written. It is intended for Claude (and any contributor) producing or updating documents here.

---

## Purpose of This Folder

The `documentation/` folder holds human-readable technical documentation for the Reportnet3 platform. Its audience is developers who are new to a service, developers returning to a part of the system they haven't touched in a while, and anyone who needs to understand how the system fits together without reading source code. Documents here should make that job faster and easier.

---

## General Principles

**Explain the why, not just the what.** Code, class names, and endpoint paths already tell you *what* exists. Documentation should explain *why* it exists, what problem it solves, and how it relates to the rest of the system. A reader should finish a document with a mental model, not just a list of facts.

**Write in natural language first.** Prose paragraphs should be the default. Use tables and code blocks to support the narrative, not replace it. A document that is nothing but tables and bullet points is a reference sheet, not documentation — it tells you what, but not why or how.

**Tables are for structured comparisons.** Use a table when you are comparing several items across the same set of attributes (e.g. endpoint method / path / purpose, or column / type / notes). Do not use tables as a substitute for explanation.

**Code blocks are for exact values and flows.** Use fenced code blocks for things that must be read precisely: SQL, config keys, class names, step-by-step flows with arrows. Inline backticks for single identifiers (`JobStatusEnum`, `POST /jobs/addImport`).

**No emojis. No filler.** Don't open sections with "This section describes..." or close them with "In summary...". Say the thing directly.

---

## Document Structure

Each document should follow this rough shape:

1. **Title and one-paragraph overview** — what this service/component does, what its core responsibility is, and what it deliberately does *not* do. This is the most important paragraph in the document.

2. **Domain model or data model** — the key entities and what they represent. Explain what each entity *is for*, not just its fields. A short table of fields is fine after the prose explanation.

3. **How it works** — the main behaviour described as a narrative. Walk through the normal path before covering edge cases. For a service: how requests come in, what decisions are made, what gets called, what comes back.

4. **Relationships with other services** — who calls this service, who this service calls, and why. For each relationship, one sentence of context is enough ("the Orchestrator calls the Snapshot Service to create release snapshots across all reporting datasets").

5. **Process flows** — for complex multi-step operations, write them out step by step. Keep flows as prose or simple numbered/arrow sequences. Avoid over-formalising them into diagrams unless the diagram genuinely adds clarity.

6. **Configuration and limits** — any Consul KV keys, environment variables, or thresholds that operators or developers need to know about.

---

## Architecture Document (`architecture.md`)

The architecture document is special. It contains the Mermaid system diagram and the high-level decision table, and it links out to per-service deep-dive documents. It should stay at the overview level — no detailed service logic belongs in it.

When a new service or infrastructure component is added to the system:
- Add it to the Mermaid diagram with the appropriate node style
- Add a row to the Key Architecture Decisions table if it represents a meaningful technology choice
- Add a Critical Data Flow entry if it introduces a new end-to-end flow
- Link to a new deep-dive `.md` file under "Service Deep Dives" if detailed documentation is written

---

## Per-Service Deep-Dive Documents

Each service that warrants detailed documentation gets its own `.md` file (e.g. `orchestrator.md`). The file should be self-contained — a reader should not need to cross-reference the architecture document to understand the service.

Before writing a deep-dive document, do a thorough read of the service's source code:
- All controller classes (endpoints and their parameters)
- All service interfaces and implementations (what each method actually does)
- All entity and enum classes (domain model)
- All scheduler / cron classes
- All Feign client interfaces (outbound calls)
- All Kafka producer/consumer classes (event types, topics)
- `application.yml` (port, key config)

The goal is to describe the service as it *actually works*, not as it was intended to work. If there is a gap between the two, note it.

---

## Database Schema Documents

Database documents (e.g. `postgresql_db.md`) describe tables, columns, types, and constraints. For each table:
- Open with one sentence explaining what the table represents in the business domain
- List columns in a table with type and a short note on anything non-obvious
- Call out foreign keys, inheritance relationships, and indexes that affect query patterns
- Note any Flyway migration file that created or significantly changed the table

Column notes should explain business meaning, not repeat the column name. `obligation_id — Reference to an obligation in the ROD` is useful. `id — The id` is not.

---

## Style

- Use UK/neutral English (finalise, not finalize; behaviour, not behavior).
- Use sentence case for headings, not title case.
- Keep sentences short. If a sentence needs more than two clauses, split it.
- Prefer active voice. "The Orchestrator calls the Snapshot Service" beats "The Snapshot Service is called by the Orchestrator".
- When referencing code identifiers in prose, always use backticks: `JobStatusEnum`, `checkEligibilityOfJob()`.
- Service names are capitalised when referring to the service as a component (Dataset Service, Validation Service) but lowercase when referring to the concept (the validation logic, the dataset).

---

## Wiki verification workflow

The `wiki_output/` folder contains pages extracted from the Redmine wiki. Many of those pages are years old and may no longer reflect how the system actually works. The goal of the verification pass is to find gaps and inaccuracies by comparing each wiki page against two authoritative sources:

1. **Source code** — `/Users/janbliki/Documents/GitHub/eea.reportnet3/`. This is ground truth for what the system actually does today.
2. **Source-code-derived docs** — the `CoreDomain/`, `DataLake/`, `Frontend/`, `Infrastructure/`, `IntegrationServices/`, `Persistence/`, and `SupportServices/` folders in this repo. These are the deep-dive documents produced by reading the source code directly.

### Verification process — per file

For each `.md` file in `wiki_output/`:

1. Read the wiki page in full.
2. Identify which part of the source code it corresponds to (a service, a role enum, a deployment procedure, etc.). If there is no source-code counterpart (e.g. a project management page or a list of SharePoint links), note that and skip the code comparison.
3. Read the relevant source code or source-derived document.
4. Append a `## Verification notes` section at the bottom of the wiki file. In that section:
   - List any factual discrepancies between the wiki and the current code (e.g. a role name that has changed, an endpoint that no longer exists, a service that has been renamed).
   - Note anything the wiki describes that cannot be confirmed in the source (i.e. claims that may be stale or aspirational).
   - Note anything in the source code that the wiki omits entirely and that readers would need to know.
   - If the page is purely administrative or historical (project management, meeting notes, SharePoint links), write a single line: `No source code verification applicable — administrative or historical content.`
5. Do not edit the body of the wiki page yet. Verification notes are the first step; rewrites come later.

### Suggestion files — per folder

After verifying all pages in a folder, create a `suggestion.md` file in that folder. This file lists topics the folder should cover but currently does not — either because no wiki page exists, or because the existing pages are too thin to be useful. Keep each suggestion brief: one heading and two or three sentences explaining what the gap is and why it matters.

### Folder order

Work through folders in order: `01_overview` → `02_development` → `03_infrastructure` → `04_deployment` → `05_operations` → `06_data_runbooks` → `07_validation` → `08_citus` → `09_support`.

### Source mapping reference

| Wiki folder | Primary source docs | Source code location |
|---|---|---|
| 01_overview | — (meta/overview) | `common-interfaces/…/enums/` for roles |
| 02_development | — | service `application.yml` files, `Dockerfile`s |
| 03_infrastructure | `Infrastructure/` | `configuration/`, Kubernetes manifests |
| 04_deployment | — | `Jenkinsfile`, `Jenkinsfile.eea` |
| 05_operations | `Persistence/` | `database/`, migration scripts |
| 06_data_runbooks | `CoreDomain/`, `Persistence/` | `dataflow-service/`, `dataset-service/` |
| 07_validation | `CoreDomain/validation.md` | `validation-service/` |
| 08_citus | `Persistence/postgresql_db.md` | `database/`, `recordstore-service/` |
| 09_support | `SupportServices/` | `collaboration-service/`, `communication-service/` |
