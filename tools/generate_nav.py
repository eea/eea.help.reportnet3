#!/usr/bin/env python3
"""
Generate the navigation files and the redirect map from the migration plan.

Reads  migration/path_map.json
Writes docs/01_user-guide/**/.pages       — per-directory nav order
       mkdocs.yml redirect_maps section   — old WordPress URL -> new page

Why .pages files rather than one big nav:
-----------------------------------------
MkDocs lets you declare the whole site nav in mkdocs.yml. That works, but every
reorder touches one 200-line block and the diff is unreadable. The awesome-pages
plugin instead reads a small .pages file per directory, so moving a page within
a section produces a three-line diff in one file, and adding a page means adding
one line next to its siblings. Order stays explicit and reviewable, and
filenames never have to carry numeric prefixes.

The redirect map matters if help.reportnet.europa.eu is ever repointed at the
new site: mkdocs-redirects emits a stub at every old WordPress URL that
forwards to the new page, so existing bookmarks and the help links embedded in
the Reportnet UI keep working.

Usage:
  python tools/generate_nav.py
"""

import os
import re
import json
import argparse
from pathlib import Path

BEGIN = "  # BEGIN GENERATED REDIRECTS — python tools/generate_nav.py"
END = "  # END GENERATED REDIRECTS"


def yaml_quote(s):
    """Quote a nav title if it contains YAML-significant characters."""
    if re.search(r"[:#\[\]{}&*!|>'\"%@`]", s) or s.strip() != s:
        return '"' + s.replace('"', '\\"') + '"'
    return s


def build_pages_files(entries, aliases, docs_root):
    """Group entries by directory and render one .pages file for each."""
    # directory -> list of (order, nav_entry, title, is_alias)
    dirs = {}

    for e in entries:
        d = e["new_path"].rsplit("/", 1)[0]
        if e["is_section"]:
            # A section owns a directory; it is listed in its *parent's* nav.
            parent = e["parent_dir"]
            dirs.setdefault(parent, []).append(
                (e["order"], e["nav_entry"].rstrip("/"), e["title"], False))
            # Its own index.md leads its own directory.
            dirs.setdefault(d, []).append((-1, "index.md", None, False))
        else:
            dirs.setdefault(d, []).append(
                (e["order"], e["nav_entry"], e["title"], False))

    # A page the WordPress menu shows in two places. One canonical file, listed
    # a second time by relative path so the new menu matches the old exactly.
    for a in aliases:
        rel = Path(os.path.relpath(a["canonical"], a["parent_dir"])).as_posix()
        dirs.setdefault(a["parent_dir"], []).append(
            (a["order"], rel, a["title"], True))

    # Directory -> its display title, taken from the section page that owns it.
    dir_title = {e["new_path"].rsplit("/", 1)[0]: e["title"]
                 for e in entries if e["is_section"]}
    dir_title[docs_root] = "User guide"

    written = []
    for d, items in sorted(dirs.items()):
        items.sort(key=lambda t: t[0])
        lines = []
        if d in dir_title:
            lines.append(f"title: {yaml_quote(dir_title[d])}")
        lines.append("nav:")
        for _, entry, title, is_alias in items:
            if title is None:                       # the section's own index
                lines.append(f"  - {entry}")
            elif is_alias:
                lines.append(f"  - {yaml_quote(title)}: {entry}"
                             f"   # also listed under its canonical section")
            else:
                lines.append(f"  - {yaml_quote(title)}: {entry}")
        path = Path(d) / ".pages"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        written.append(path)
    return written


def build_redirects(entries, docs_dir):
    """old WordPress URL path -> new docs-relative markdown file.

    Keys are bare old paths. The WordPress pages were served from the site
    root (/rest-api/, /sample-page/...), so the redirect stub has to be emitted
    at that same root path — not under the new section directory. Values are
    relative to docs_dir, which is what mkdocs-redirects expects.
    """
    prefix = docs_dir + "/"
    out = {}
    for e in entries:
        old = e["old_path"].strip("/")
        if not old:
            continue                       # site root needs no redirect
        new = e["new_path"]
        assert new.startswith(prefix), new
        src, dst = f"{old}/index.md", new[len(prefix):]
        if src == dst:
            continue                       # already at its final location
        out[src] = dst
    return dict(sorted(out.items()))


def inject_redirects(mkdocs_path, redirects):
    """Rewrite the generated block inside mkdocs.yml, leaving the rest alone."""
    text = Path(mkdocs_path).read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        raise SystemExit(
            f"ERROR: {mkdocs_path} is missing the generated-redirects markers")

    body = [BEGIN]
    for old, new in redirects.items():
        body.append(f"        {old}: {new}")
    body.append(END)

    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)
    Path(mkdocs_path).write_text(pattern.sub("\n".join(body), text),
                                 encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="migration/path_map.json")
    ap.add_argument("--mkdocs", default="mkdocs.yml")
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    docs_root = plan["docs_root"]

    written = build_pages_files(plan["entries"], plan["aliases"], docs_root)
    print(f"Wrote {len(written)} .pages files:")
    for p in written:
        print(f"  {p}")

    # docs_root is "docs/01_user-guide"; redirect targets are relative to the
    # docs_dir ("docs"), so strip the first segment.
    docs_dir = docs_root.split("/", 1)[0]
    redirects = build_redirects(plan["entries"], docs_dir)
    inject_redirects(args.mkdocs, redirects)
    print(f"\nInjected {len(redirects)} redirects into {args.mkdocs}")


if __name__ == "__main__":
    main()
