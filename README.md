# Reportnet 3 documentation

Documentation for the [Reportnet 3](https://reportnet.europa.eu/) platform — the European Environment Agency's system for environmental data reporting.

**Published site: <https://eea.github.io/eea.help.reportnet3/>**

The site rebuilds automatically from `main`. Every pull request runs the same build with `--strict`, so a broken internal link or a page missing from the navigation fails the check rather than reaching the site.

---

## What is in this repository

| Path | Contents |
|---|---|
| `docs/01_user-guide/` | The user guide, migrated from `help.reportnet.europa.eu`. This is what the published site serves. |
| `CoreDomain/`, `Persistence/`, `Infrastructure/`, `SupportServices/`, `IntegrationServices/`, `DataLake/`, `Frontend/` | Per-service deep dives written by reading the Reportnet 3 source code |
| `architecture.md`, `RestAPI.md`, `api_key.md` | System architecture diagram, the full REST endpoint surface, and the API key mechanism |
| `wiki_output/` | Pages extracted from the Redmine developer wiki, reorganised into numbered folders and annotated with verification notes |
| `tools/` | The help-site migration pipeline |
| `migration/` | Machine-readable record of that migration |

Only `docs/` is published. The rest is source material that has not yet been folded into the site — see [Next steps](#next-steps).

## Working on the documentation

Writing conventions are in [`CLAUDE.md`](CLAUDE.md): explain why something exists rather than restating what the code already says, prose before tables, UK English, sentence-case headings.

To preview locally:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-docs.txt
.venv/bin/mkdocs serve
```

Then open <http://127.0.0.1:8000/>.

### Page order

Navigation order is **not** alphabetical and **not** encoded in filenames. Each directory carries a `.pages` file listing its children in order, read by the `awesome-pages` plugin:

```yaml
title: Reporter
nav:
  - index.md
  - Dataflows overview page: dataflows-overview-page.md
  - Dataflow home page: dataflow-home-page
  - Submit data: submit-data
  - Validate data: validate-data
  - Release data: release-data
```

To move a page, reorder the lines. To add one, add a line next to its siblings. Filenames never need renaming, so links and URLs stay stable when the order changes.

A new page that is not listed in a `.pages` file will fail the strict build. That is deliberate — it means pages cannot be silently orphaned.

## The help-site migration

The user guide came from a WordPress site whose page order and hierarchy lived **only** in a menu record. The URLs did not reflect the structure: `/fme-connectors/` and `/import-api-endpoints/` were root-level pages shown two levels deep in the menu, and the entire Requester section was served from `/sample-page/`, the default slug WordPress creates on install. The WordPress REST API is locked on that host, so `menu_order` could not be read directly.

The pipeline therefore captures the menu first and generates everything else from it:

```
tools/extract_help_menu.py      ->  migration/help_menu.json     the ordering, captured
tools/build_migration_plan.py   ->  migration/path_map.json      old URL -> new file
tools/crawl_help_content.py     ->  docs/01_user-guide/**/*.md   content + assets
tools/generate_nav.py           ->  **/.pages + redirect map
```

61 pages, 210 images and 3 linked files were migrated, with 102 internal links rewritten to relative paths.

`mkdocs.yml` carries 60 generated redirects mapping every old WordPress URL to its new page. If `help.reportnet.europa.eu` is ever repointed at this site, existing bookmarks and the help links embedded in the Reportnet 3 UI keep working.

[`migration/README.md`](migration/README.md) records every decision taken, including the pages that were not migrated and why.

## Next steps

- Fold the developer deep dives and `wiki_output/` into `docs/` so they are searchable alongside the user guide. `docs/.pages` has a commented slot for them.
- Replace the generated index for "ReportNet3 Import/Export (vs CWS)", whose WordPress page is empty.
- Two Rest API links point at `/sql-db-setup/` and `/data-flow-monitoring/`, unpublished WordPress drafts with no content. Either write them or remove the links.
