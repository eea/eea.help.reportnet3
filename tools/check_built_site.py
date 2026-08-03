#!/usr/bin/env python3
"""
Post-build checks on site/ for faults that `mkdocs build --strict` cannot see.

`--strict` validates links written in Markdown. It does not look at links the
navigation emits, and it does not look at the redirect stubs, because
mkdocs-redirects writes those after the build has finished. Both have produced
live breakage on this site, so both are checked here.

Check 1 — unresolved .md links
    A .pages entry that references a file outside its own directory cannot be
    resolved by MkDocs. Rather than failing, it is passed through into the
    sidebar as a literal href ending in .md, which 404s. The only legitimate
    .md links in the output are the "Edit this page" links back to GitHub.

Check 2 — self-referential redirects
    A redirect whose stub lands on the URL of a real page overwrites that page,
    because the stubs are written last. If the collision is with the redirect's
    own target, the result is a page that refreshes to itself forever.

Usage:
  python tools/check_built_site.py [--site site]
"""

import re
import sys
import argparse
from pathlib import Path
from urllib.parse import urljoin

REFRESH = re.compile(
    r'<meta[^>]+http-equiv=["\']refresh["\'][^>]*content=["\'][^"\']*?url=([^"\';]+)',
    re.I)
MD_HREF = re.compile(r'href="([^"]*\.md)"')


def page_url(html_file, site):
    """The site-absolute URL a built HTML file is served at."""
    rel = html_file.relative_to(site).as_posix()
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    if rel == "index.html":
        return "/"
    return "/" + rel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    args = ap.parse_args()

    site = Path(args.site)
    if not site.is_dir():
        print(f"ERROR: {site} not found — run `mkdocs build` first", file=sys.stderr)
        return 2

    bad_links, self_redirects = [], []

    for html_file in sorted(site.rglob("*.html")):
        text = html_file.read_text(encoding="utf-8", errors="replace")
        url = page_url(html_file, site)

        for href in MD_HREF.findall(text):
            if "github.com" in href:
                continue            # the "Edit this page" link, expected
            bad_links.append((url, href))

        m = REFRESH.search(text)
        if m:
            target = urljoin(url, m.group(1).strip())
            if target == url:
                self_redirects.append(url)

    failed = False

    if bad_links:
        failed = True
        print(f"FAIL: {len(bad_links)} unresolved .md link(s) in the built site.")
        print("  A nav entry in a .pages file most likely references a file outside")
        print("  its own directory, which MkDocs cannot resolve. Move the page, or")
        print("  cross-link it from the page body instead of the navigation.\n")
        for url, href in bad_links:
            print(f"    {url}  ->  {href}")
        print()

    if self_redirects:
        failed = True
        print(f"FAIL: {len(self_redirects)} page(s) redirect to themselves.")
        print("  A redirect_maps entry in mkdocs.yml points at a page whose URL is")
        print("  the same as the redirect's own. Because MkDocs serves directory")
        print("  URLs, `foo.md` and `foo/index.md` are both served at /foo/ — so")
        print("  the stub overwrites the page and loops. Remove that entry.\n")
        for url in self_redirects:
            print(f"    {url}")
        print()

    if failed:
        return 1

    print("Built site OK: no unresolved .md links, no self-referential redirects.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
