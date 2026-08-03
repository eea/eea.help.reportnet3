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

    # Pages the WordPress menu showed in two places are NOT listed twice here.
    # MkDocs navigation cannot reference a file outside the directory its
    # .pages sits in — neither a ../ path nor a docs-relative one resolves, and
    # both are emitted into the sidebar as a raw .md href that 404s. The
    # duplicate is instead carried as a "See also" link in the page body, which
    # MkDocs does resolve; see CROSS_REFERENCES in crawl_help_content.py.
    # A sidebar entry appearing twice also breaks next/previous navigation, so
    # one canonical position per page is the better outcome regardless.

    # Directory -> its display title, taken from the section page that owns it.
    # The docs root gets no title: site_name already names the site, and a
    # title here would reintroduce the wrapper level the sections were lifted
    # out of.
    dir_title = {e["new_path"].rsplit("/", 1)[0]: e["title"]
                 for e in entries if e["is_section"]}

    # The site landing page is not a migrated page, so it is not in the plan.
    # It leads the root nav.
    dirs.setdefault(docs_root, []).insert(0, (-2, "index.md", "About", False))

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


def to_url(doc_path):
    """The URL MkDocs serves a given docs-relative file at.

    Directory URLs are the default, so both `webforms.md` and
    `webforms/index.md` are served at `/webforms/`. Comparing file paths is
    therefore not enough to tell whether two entries collide — they have to be
    reduced to the URL first.
    """
    if doc_path == "index.md":
        return "/"
    if doc_path.endswith("/index.md"):
        return "/" + doc_path[: -len("index.md")]
    return "/" + doc_path[:-3] + "/"


def build_redirects(entries, docs_dir):
    """old WordPress URL path -> new docs-relative markdown file.

    Keys are bare old paths. The WordPress pages were served from the site
    root (/rest-api/, /sample-page/...), so the redirect stub has to be emitted
    at that same root path — not under the new section directory. Values are
    relative to docs_dir, which is what mkdocs-redirects expects.

    A redirect is dropped when its stub would land on the URL of a real page.
    mkdocs-redirects writes its stubs after the build, so such a stub silently
    overwrites the page it collides with. Where the collision is with the
    redirect's own target the result is a page that refreshes to itself
    forever; where it is with a different page, that page disappears.
    """
    prefix = docs_dir + "/"
    pages = {}                              # url -> doc path of a real page
    planned = []
    for e in entries:
        new = e["new_path"]
        assert new.startswith(prefix), new
        dst = new[len(prefix):]
        pages[to_url(dst)] = dst
        old = e["old_path"].strip("/")
        if old:                             # site root needs no redirect
            planned.append((f"{old}/index.md", dst))

    out, dropped = {}, []
    for src, dst in planned:
        src_url = to_url(src)
        collides_with = pages.get(src_url)
        if collides_with is not None:
            dropped.append((src, dst, src_url, collides_with))
            continue
        out[src] = dst
    return dict(sorted(out.items())), dropped


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
    redirects, dropped = build_redirects(plan["entries"], docs_dir)
    inject_redirects(args.mkdocs, redirects)
    print(f"\nInjected {len(redirects)} redirects into {args.mkdocs}")

    if dropped:
        print(f"\nDropped {len(dropped)} redirect(s) that would have overwritten"
              " a real page — the old URL already serves the right content:")
        for src, dst, url, page in dropped:
            note = "its own target" if page == dst else f"the page {page}"
            print(f"  {src} -> {dst}")
            print(f"      stub would land on {url}, which is {note}")


if __name__ == "__main__":
    main()
