# Help site migration

The user guide under `docs/01_user-guide/` was migrated from
`help.reportnet.europa.eu`, a WordPress site running the Astra theme. This
folder holds the machine-readable record of that migration, so the process can
be re-run and audited rather than being a one-off manual copy.

## Why the tooling exists

The page order and hierarchy of the help site lived **only** in a WordPress menu
record. They were not derivable from anything else:

- The WP REST API (`/wp-json/wp/v2/pages`) returns 401 on that host, so
  `menu_order` could not be read directly.
- The URLs do not reflect the hierarchy. `/fme-connectors/`,
  `/import-api-endpoints/`, `/geospatial-data-features/`, `/dataflow-users-list/`
  and `/change-release-date-of-dataset/` are all root-level pages that the menu
  displayed two or three levels deep.
- The whole Requester section was served from `/sample-page/`, the default page
  slug WordPress creates on install, which was repurposed and never renamed.
- The Reporter section prefix hardcoded a version: `/reportnet-3-1-reporter-howto/`.

Exporting the pages without first capturing the menu would have lost the
structure entirely. So the menu is extracted first, and everything else is
generated from it.

## Pipeline

Run in order. Each step reads the previous step's output.

```
python tools/extract_help_menu.py      ->  migration/help_menu.json
python tools/build_migration_plan.py   ->  migration/path_map.json
python tools/crawl_help_content.py     ->  docs/01_user-guide/**/*.md + assets/
python tools/generate_nav.py           ->  **/.pages + mkdocs.yml redirects
mkdocs build --strict
```

`extract_help_menu.py` also cross-checks the menu against the sitemap and
reports pages that appear in one but not the other.

## Files

| File | What it holds |
|---|---|
| `help_menu.json` | The WordPress menu as an ordered tree — the authoritative record of page order and hierarchy |
| `path_map.json` | Old URL to new file path for every page, plus nav order and duplicate-position aliases |

## Decisions taken during the migration

**Paths derive from menu position, not from the old URL.** This is what makes
the file tree match what readers actually see, and it is why the flat root
pages ended up nested.

**Filenames derive from page titles, not WordPress slugs.** Several slugs were
actively misleading — "Different dataflow types" lived at `/dataset-schema/`,
and "Dataflow home page" and "Dataflows overview page" had their slugs swapped.
Since the domain changes anyway, every URL breaks regardless; the redirect map
is what protects existing links.

**Three pages appeared twice in the menu.** Each has one canonical file, listed
a second time in the other section's `.pages` file so the navigation still
matches the old site:

- Manage dataset copies — canonical under Reporter / Submit data
- Example: Configure a simple questionnaire — canonical under Requester
- External integration possibilities — canonical under Requester / Import-Export vs CWS

**Two broken links were repaired.** Both 404 on the live site today; see
`LINK_FIXES` in `tools/crawl_help_content.py`.

**Two pages were not migrated.** `/sql-db-setup/` and `/data-flow-monitoring/`
render an empty content area — they are unpublished drafts that were created in
the page tree and never written, which is why the menu omits them. The Rest API
landing page links to both; those two links are left absolute and are the only
unresolved links in the migrated content.

**One section landing page was empty.** "ReportNet3 Import/Export (vs CWS)" has
no content on the live site, so `crawl_help_content.py` generated an index
listing its children. It carries an HTML comment marking it for replacement.

## Re-running against the live site

The scripts are idempotent — re-running overwrites the same files with the same
bytes. To pick up changes made in WordPress since the migration, run the full
pipeline and review the diff. Note that `generate_nav.py` rewrites the `.pages`
files wholesale, so any hand-editing of navigation order should be made in
WordPress first, or the pipeline should be retired once WordPress is switched
off.
