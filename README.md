# Reportnet 3 documentation

Source for the Reportnet 3 help pages.

**Published site: <https://eea.github.io/eea.help.reportnet3/>**

Every page on the site comes from a Markdown file in `docs/`. Change the file, and the site rebuilds itself. There is no CMS to log into and no separate publishing step.

---

## How publishing works

Pushing to `main` triggers a GitHub Actions workflow that builds the site and deploys it. It takes about a minute. You can watch it under the [Actions tab](https://github.com/eea/eea.help.reportnet3/actions).

Pull requests run the same build, but do not deploy. The build uses `--strict`, which means it **fails** on a broken internal link or a page missing from the navigation. If your pull request shows a red cross, the site would have been broken — read the log, fix it, push again.

This is deliberate. It is the reason pages cannot quietly go missing or end up unreachable.

---

## Maintaining the pages

Two ways to work. Use whichever suits the change.

**Directly on GitHub** — no software to install. Good for typos, wording, adding a paragraph. Every page on the published site has an "Edit this page" pencil icon at the top right that takes you straight to the right file in the GitHub editor.

**On your own machine** — needed if you are adding images, moving pages around, or want to preview before publishing. See [Working locally](#working-locally).

### Editing an existing page

1. Open the page on the published site and click the pencil icon at the top right. This opens the exact source file on GitHub.
2. Click the pencil icon again in GitHub to enter edit mode.
3. Make your change. The content is [Markdown](#markdown-quick-reference).
4. Scroll down to **Commit changes**. Write a short line saying what you changed.
5. Choose **Create a new branch and start a pull request**, then **Propose changes**.
6. On the next screen, click **Create pull request**.
7. Wait for the check to go green, then click **Merge pull request**.

The site updates about a minute after merging.

Committing straight to `main` also works and skips steps 5 to 7, but you lose the safety net — if the build fails, the live site keeps the last good version, but your change is not published and nobody is told.

### Adding a new page

A new page needs two things: the file, and a line in its section's `.pages` file telling the navigation where it goes. **Both are required.** A page that is not listed in `.pages` fails the build, on purpose, so that pages cannot become orphans.

1. Decide which section it belongs to — that is which folder under `docs/` it goes in. For example, a new page about validating data belongs in `docs/reporter/validate-data/`.
2. Create the file with a short, lowercase, hyphenated name ending in `.md`, for example `bulk-validation.md`. Do not put numbers in the filename; ordering is handled separately.
3. Start the file with a single `#` heading — this is the page title.
4. Open the `.pages` file in that same folder.
5. Add a line under `nav:` at the position where the page should appear in the menu:

   ```yaml
   title: Validate data
   nav:
     - index.md
     - Quality control rules: quality-control-rules.md
     - Execute validation: execute-validation.md
     - Bulk validation: bulk-validation.md      # <- the new page
     - Filter table data: filter-table-data.md
   ```

   The text before the colon is what appears in the menu. It does not have to match the filename or the heading, though it usually should.
6. Commit both files together.

### Adding a new section

A section is a folder with its own landing page.

1. Create the folder under `docs/`, for example `docs/reporter/bulk-operations/`.
2. Create `index.md` inside it. This is the section's landing page — what people see when they click the section name in the menu. Give it a `#` heading and a short paragraph explaining what the section covers.
3. Create a `.pages` file inside the folder:

   ```yaml
   title: Bulk operations
   nav:
     - index.md
     - Bulk import: bulk-import.md
     - Bulk export: bulk-export.md
   ```

   `title:` is the section name in the menu. `index.md` must be listed first so the landing page appears at the top.
4. Add the folder to the **parent** folder's `.pages` file, at the position you want it:

   ```yaml
   title: Reporters
   nav:
     - index.md
     - Dataflows overview page: dataflows-overview-page.md
     - Bulk operations: bulk-operations        # <- folder name, no .md
     - Submit data: submit-data
   ```

   Note the difference: pages end in `.md`, folders do not.

To add a whole new top-level tab, do the same but edit `docs/.pages` as the parent.

### Linking to a page in a different section

A `.pages` file can only list files that live in **its own folder or a subfolder of it**. It cannot point at a page somewhere else in the site — neither `../other-section/page.md` nor a path from the top of `docs/` works. MkDocs passes such an entry straight through into the sidebar as a link ending in `.md`, which 404s, and the build still passes. The automated check described under [How publishing works](#how-publishing-works) exists to catch exactly this.

So a page cannot appear in two places in the menu. If a page is relevant to a second section, link to it from that section's text instead:

```markdown
## See also

- [Manage dataset copies](../submit-data/manage-dataset-copies.md)
```

Links written in the page body are resolved properly, unlike navigation entries. Three pages carry such a block already, because the old WordPress menu listed them twice.

### Changing the order of pages

Reorder the lines in the relevant `.pages` file. That is the entire process.

Order is **not** alphabetical and is **not** encoded in filenames, which is why you never need to rename anything to move a page. Renaming would change its URL and break every link pointing at it; reordering a line does not.

### Renaming or moving a page

Renaming a file changes its published URL, so anyone who bookmarked the old address gets a 404. If the page has been live for a while, add a redirect:

1. Rename or move the file, and update its line in the `.pages` file.
2. Open `mkdocs.yml` and find the `redirect_maps:` block.
3. Add a line **below** the `# END GENERATED REDIRECTS` marker, in the form `old-path/index.md: new/path.md`.

Do not edit between the `BEGIN GENERATED` and `END GENERATED` markers. Those lines are regenerated by the migration tooling and your change would be overwritten.

### Adding images

Images live in `docs/assets/`, all in one folder regardless of which page uses them. That way an image used on several pages is stored once.

1. Add the image file to `docs/assets/`. Use a descriptive name — `release-to-data-collection.png`, not `image-63.png`.
2. Reference it from your page with a relative path back up to `assets/`. The number of `../` depends on how deep the page sits:

   ```markdown
   ![Releasing to a data collection](../../assets/release-to-data-collection.png)
   ```

   From `docs/reporter/submit-data/dataset-actions.md` that is `../../assets/`. From `docs/webforms.md`, which sits at the top level, it is just `assets/`.
3. The text in the square brackets is the alt text, read aloud by screen readers. Write something that describes the image.

If you get the path wrong the build fails and tells you, so this is safe to guess at.

### Deleting a page

Delete the file and remove its line from the `.pages` file. Both, or the build fails. Consider adding a redirect to whatever replaced it, as described above.

---

## Working locally

Needed for previewing, and easier than the web editor for anything touching more than one file.

```bash
git clone https://github.com/eea/eea.help.reportnet3.git
cd eea.help.reportnet3
python3 -m venv .venv
.venv/bin/pip install -r requirements-docs.txt
.venv/bin/mkdocs serve
```

Open <http://127.0.0.1:8000/>. The preview reloads as you save, so you can keep it open in a browser beside your editor.

Before pushing, check that the real build passes:

```bash
.venv/bin/mkdocs build --strict
```

If that succeeds, so will the pull request check.

---

## Markdown quick reference

```markdown
# Page title            (one per page, at the top)
## A section heading
### A subheading

**bold**   *italic*   `inline code`

- a bullet
- another bullet

1. a numbered step
2. another step

[link to another page](../general/whats-new.md)
[link to a website](https://reportnet.europa.eu/)

![alt text](../assets/screenshot.png)

| Column | Column |
|--------|--------|
| value  | value  |
```

Links between pages use the **file path**, ending in `.md`, not the published URL. The build rewrites them and fails if the target does not exist — which is how broken links get caught before anyone sees them.

For callouts, use an admonition:

```markdown
!!! note
    Text of the note, indented by four spaces.

!!! warning
    Use for things that can lose data.
```

---

## What is in this repository

| Path | Contents |
|---|---|
| `docs/` | The published site. Everything else below is not published. |
| `docs/assets/` | All images and downloadable files |
| `docs/assets/theme/` | Logo, favicon and the brand colours in `extra.css`. The header colour is sampled from the logo, which has a solid background rather than a transparent one — change one and you must change the other. |
| `CoreDomain/`, `Persistence/`, `Infrastructure/`, `SupportServices/`, `IntegrationServices/`, `DataLake/`, `Frontend/` | Per-service deep dives written by reading the Reportnet 3 source code |
| `architecture.md`, `RestAPI.md`, `api_key.md` | System architecture, the full REST endpoint surface, and the API key mechanism |
| `wiki_output/` | Pages extracted from the Redmine developer wiki, with verification notes |
| `tools/`, `migration/` | The help-site migration pipeline and its records |
| `CLAUDE.md` | Writing conventions — explain why rather than restating what, prose before tables, UK English |

---

## Background: the migration

The pages came from `help.reportnet.europa.eu`, a WordPress site. Its page order and hierarchy lived **only** in a WordPress menu record — the URLs did not reflect it. `/fme-connectors/` and `/import-api-endpoints/` were root-level pages displayed two levels deep in the menu, and the entire Requester section was served from `/sample-page/`, the default slug WordPress creates on install. The WordPress REST API was locked, so the ordering could not be read directly.

The tooling in `tools/` therefore captured the menu first and generated everything else from it. 61 pages, 210 images and 3 linked files came across, with 102 internal links rewritten.

`mkdocs.yml` carries 59 generated redirects mapping every old WordPress URL to its new page, so if `help.reportnet.europa.eu` is ever pointed at this site, existing bookmarks and the help links embedded in the Reportnet 3 interface keep working.

[`migration/README.md`](migration/README.md) records every decision, including which pages were not migrated and why.

### Known gaps

- The landing page for "ReportNet3 Import/Export (vs CWS)" is generated from its children, because the WordPress original has no content. It needs writing.
- Two links in the Rest API section point at `/sql-db-setup/` and `/data-flow-monitoring/`, WordPress drafts that were never written. Either write them or remove the links.
- The developer and operations documentation is in this repository but not on the site. Folding it in means moving it under `docs/` and adding it to `docs/.pages`.
