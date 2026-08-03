#!/usr/bin/env python3
"""
Menu-order extractor for help.reportnet.europa.eu.

Why this script exists
----------------------
The page order and hierarchy of the Reportnet help site live *only* in a
WordPress menu record. They are not in the page content, and they are not
derivable from the URLs: several pages sit flat at the site root
(/fme-connectors/, /import-api-endpoints/, ...) while appearing nested in the
menu, and the Requester section is served from the leftover default WordPress
slug /sample-page/.

The WP REST API (/wp-json/wp/v2/pages) returns 401 on this host, so menu_order
cannot be read directly. The rendered menu is however present server-side in
every page as a nested <ul> under #menu-navigate. This script parses that tree
and writes it to JSON, so the ordering survives independently of WordPress.

Run this before any content migration. Everything downstream (the .pages nav
files, the redirect map) is generated from its output.

Usage:
  python tools/extract_help_menu.py
  python tools/extract_help_menu.py --output migration/help_menu.json

Dependencies:
  pip install requests beautifulsoup4
"""

import re
import sys
import json
import argparse
from pathlib import Path
from urllib.parse import urlparse

import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

SITE = "https://help.reportnet.europa.eu"
MENU_ID = "menu-navigate"
SITEMAP = f"{SITE}/wp-sitemap-posts-page-1.xml"

# The Astra theme renders the same menu twice (desktop header + off-canvas
# mobile). #menu-navigate is the compact sidebar copy and is the one to parse.


def fetch(url, session):
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def path_of(url):
    """Site-relative path, always with leading and trailing slash."""
    p = urlparse(url).path or "/"
    if not p.endswith("/"):
        p += "/"
    return p


def slug_of(url):
    p = path_of(url).strip("/")
    return p.rsplit("/", 1)[-1] if p else "home"


def parse_menu(html):
    """Parse #menu-navigate into an ordered tree.

    Returns a list of nodes, each:
      {title, url, path, slug, wp_menu_item_id, children: [...]}
    Sibling order in the list is the menu order.
    """
    soup = BeautifulSoup(html, "html.parser")
    root = soup.find("ul", id=MENU_ID)
    if root is None:
        raise SystemExit(f"ERROR: no <ul id={MENU_ID}> found — theme or menu changed")

    def walk(ul):
        nodes = []
        # Direct <li> children only; nested sub-menus are handled recursively.
        for li in ul.find_all("li", recursive=False):
            a = li.find("a", recursive=False)
            if a is None:
                continue
            # The dropdown arrow is a <span> inside the <a>; drop it before
            # reading the label, or every parent title gains stray whitespace.
            for span in a.find_all("span"):
                span.decompose()
            title = a.get_text(strip=True)
            url = a.get("href", "")

            classes = li.get("class", [])
            item_id = next(
                (int(c.rsplit("-", 1)[1]) for c in classes
                 if re.fullmatch(r"menu-item-\d+", c)),
                None,
            )

            sub = li.find("ul", class_="sub-menu", recursive=False)
            nodes.append({
                "title": title,
                "url": url,
                "path": path_of(url),
                "slug": slug_of(url),
                "wp_menu_item_id": item_id,
                "children": walk(sub) if sub else [],
            })
        return nodes

    return walk(root)


def fetch_sitemap_paths(session):
    xml = fetch(SITEMAP, session)
    return {path_of(u) for u in re.findall(r"<loc>([^<]+)</loc>", xml)}


def flatten(nodes, depth=0, out=None):
    if out is None:
        out = []
    for n in nodes:
        out.append((depth, n))
        flatten(n["children"], depth + 1, out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", default="migration/help_menu.json",
                    help="where to write the ordered menu tree")
    ap.add_argument("--source-url", default=SITE,
                    help="page to read the menu from (any page carries it)")
    args = ap.parse_args()

    session = requests.Session()
    session.headers["User-Agent"] = "reportnet-docs-migration/1.0"

    print(f"Fetching menu from {args.source_url}")
    tree = parse_menu(fetch(args.source_url, session))

    flat = flatten(tree)
    print(f"Parsed {len(flat)} menu items, {len(tree)} top-level sections\n")

    for depth, n in flat:
        print(f"  {'  ' * depth}{n['title']}  ->  {n['path']}")

    # Cross-check against the sitemap so nothing is silently left behind.
    print(f"\nFetching {SITEMAP}")
    sitemap = fetch_sitemap_paths(session)
    in_menu = {n["path"] for _, n in flat}

    orphans = sorted(sitemap - in_menu)
    dangling = sorted(in_menu - sitemap)

    if orphans:
        print(f"\nPages in the sitemap but NOT in the menu ({len(orphans)}) —"
              " these have no defined position and need one assigned by hand:")
        for p in orphans:
            print(f"  {p}")
    if dangling:
        print(f"\nMenu entries with no sitemap page ({len(dangling)}) —"
              " custom links or drafts:")
        for p in dangling:
            print(f"  {p}")

    payload = {
        "source": args.source_url,
        "menu_id": MENU_ID,
        "counts": {
            "menu_items": len(flat),
            "top_level": len(tree),
            "sitemap_pages": len(sitemap),
            "orphans": len(orphans),
        },
        "orphan_paths": orphans,
        "dangling_paths": dangling,
        "tree": tree,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
