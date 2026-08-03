#!/usr/bin/env python3
"""
Turn the extracted WordPress menu tree into a concrete file plan.

Reads  migration/help_menu.json  (from extract_help_menu.py)
Writes migration/path_map.json   — old URL path -> new docs path, plus nav order

Design decisions encoded here
-----------------------------
1. The new path is derived from the page's *menu position*, not its WordPress
   URL. The live URLs do not reflect the hierarchy — /fme-connectors/ is a root
   page that the menu shows two levels deep — so deriving from the menu is what
   makes the file tree match what readers actually see.

2. Filenames are slugified from the *title*, not the WordPress slug. Several WP
   slugs are actively misleading: the whole Requester section is served from
   /sample-page/, "Different dataflow types" lives at /dataset-schema/, and
   "Dataflow home page" and "Dataflows overview page" have their slugs swapped.
   Since the domain is changing anyway, every URL breaks regardless; the
   redirect map is what protects existing links, so we may as well land on
   honest slugs. SLUG_OVERRIDES below shortens a few unwieldy titles.

3. A page listed twice in the menu gets one canonical file at its first
   occurrence. Later occurrences are recorded as "aliases" for review rather
   than silently duplicated.

4. Section landing pages become index.md inside their own directory, so the
   section URL stays clean (/user-guide/reporter/ rather than
   /user-guide/reporter.html).

Usage:
  python tools/build_migration_plan.py
"""

import re
import json
import argparse
import unicodedata
from pathlib import Path

# Where the migrated user guide lands inside the docs tree.
DOCS_ROOT = "docs/01_user-guide"

# Titles that slugify into something too long or awkward to live with.
SLUG_OVERRIDES = {
    "About Multi Factor Authentication (MFA)": "multi-factor-authentication",
    "Example: Configure a simple questionnaire": "example-simple-questionnaire",
    "Change Release Date of Dataset (Custodian/Admin)": "change-release-date",
    "ReportNet3 Import/Export (vs CWS)": "import-export-vs-cws",
    "Validate & Run SQL as Provider": "validate-and-run-sql-as-provider",
    "Validation Results per Release Snapshot": "validation-results-per-snapshot",
    "How to add supporting reporters to my dataflow": "add-supporting-reporters",
    "Import/export data schema's": "import-export-data-schemas",
    "Import/Export table definitions": "import-export-table-definitions",
    "Show/hide release data": "show-hide-release-data",
}

# Orphan pages (in the sitemap, absent from the menu) need a home assigned by
# hand. Anything left as None is reported and excluded from the build.
#
# /sql-db-setup/ and /data-flow-monitoring/ were checked against the live site:
# both render an empty content area. They are unpublished drafts that were
# created in the page tree and never written, which is why the menu omits them.
# Left as None deliberately — do not migrate empty pages.
ORPHAN_PLACEMENT = {
    "/general/get-access/how-to-log-off/": ["General", "Login to Reportnet"],
    "/sql-db-setup/": None,
    "/data-flow-monitoring/": None,
}


def slugify(text):
    """Lowercase ASCII slug. Handles the curly apostrophes WordPress inserts."""
    text = text.replace("’", "").replace("'", "")
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", " ", text).strip().lower()
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")


def file_slug(title):
    return SLUG_OVERRIDES.get(title) or slugify(title)


def build(tree):
    """Walk the menu tree, assigning a docs path to every node.

    Returns (entries, aliases). `entries` is in menu order; each has the nav
    position needed to regenerate .pages files later.
    """
    entries = []
    aliases = []
    seen = {}  # old path -> first entry that claimed it

    def walk(nodes, parent_dir, breadcrumb):
        for order, node in enumerate(nodes):
            title = node["title"]
            old = node["path"]
            slug = file_slug(title)
            crumb = breadcrumb + [title]

            if old in seen:
                # Same WordPress page reachable from two menu positions.
                aliases.append({
                    "title": title,
                    "old_path": old,
                    "canonical": seen[old]["new_path"],
                    "duplicate_at": "/".join(crumb),
                    "parent_dir": parent_dir,
                    "order": order,
                })
                continue

            has_children = bool(node["children"])
            if has_children:
                new_dir = f"{parent_dir}/{slug}"
                new_path = f"{new_dir}/index.md"
            else:
                new_dir = parent_dir
                new_path = f"{parent_dir}/{slug}.md"

            entry = {
                "title": title,
                "old_path": old,
                "old_url": node["url"],
                "new_path": new_path,
                "parent_dir": parent_dir,
                "nav_entry": f"{slug}/" if has_children else f"{slug}.md",
                "order": order,
                "depth": len(breadcrumb),
                "breadcrumb": crumb,
                "is_section": has_children,
                "wp_menu_item_id": node["wp_menu_item_id"],
            }
            seen[old] = entry
            entries.append(entry)

            if has_children:
                walk(node["children"], new_dir, crumb)

    walk(tree, DOCS_ROOT, [])
    return entries, aliases


def place_orphans(entries):
    """Attach orphan pages to the section named in ORPHAN_PLACEMENT."""
    by_crumb = {"/".join(e["breadcrumb"]): e for e in entries}
    placed, unplaced = [], []

    for old_path, crumb in ORPHAN_PLACEMENT.items():
        if crumb is None:
            unplaced.append(old_path)
            continue
        parent = by_crumb.get("/".join(crumb))
        if parent is None:
            unplaced.append(old_path)
            continue
        title = old_path.strip("/").rsplit("/", 1)[-1].replace("-", " ").capitalize()
        slug = slugify(title)
        parent_dir = parent["new_path"].rsplit("/", 1)[0]
        # Orphans go last within their section.
        order = max((e["order"] for e in entries
                     if e["parent_dir"] == parent_dir), default=-1) + 1
        placed.append({
            "title": title,
            "old_path": old_path,
            "old_url": f"https://help.reportnet.europa.eu{old_path}",
            "new_path": f"{parent_dir}/{slug}.md",
            "parent_dir": parent_dir,
            "nav_entry": f"{slug}.md",
            "order": order,
            "depth": parent["depth"] + 1,
            "breadcrumb": crumb + [title],
            "is_section": False,
            "wp_menu_item_id": None,
            "was_orphan": True,
        })
    return placed, unplaced


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--menu", default="migration/help_menu.json")
    ap.add_argument("--output", default="migration/path_map.json")
    args = ap.parse_args()

    data = json.loads(Path(args.menu).read_text(encoding="utf-8"))
    entries, aliases = build(data["tree"])
    placed, unplaced = place_orphans(entries)
    entries.extend(placed)

    print(f"{len(entries)} pages planned  ({len(placed)} placed orphans)\n")
    for e in sorted(entries, key=lambda x: x["new_path"]):
        flag = "  [orphan]" if e.get("was_orphan") else ""
        print(f"  {e['old_path']}\n      -> {e['new_path']}{flag}")

    if aliases:
        print(f"\nDuplicate menu positions ({len(aliases)}) —"
              " one canonical file each, second position needs a decision:")
        for a in aliases:
            print(f"  '{a['title']}' at {a['duplicate_at']}")
            print(f"      canonical: {a['canonical']}")

    if unplaced:
        print(f"\nUnplaced orphans ({len(unplaced)}) — set a section in"
              " ORPHAN_PLACEMENT or they are dropped:")
        for p in unplaced:
            print(f"  {p}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "docs_root": DOCS_ROOT,
        "counts": {
            "pages": len(entries),
            "aliases": len(aliases),
            "unplaced_orphans": len(unplaced),
        },
        "entries": entries,
        "aliases": aliases,
        "unplaced_orphans": unplaced,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
