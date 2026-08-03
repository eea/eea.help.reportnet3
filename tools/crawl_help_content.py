#!/usr/bin/env python3
"""
Fetch every planned page from help.reportnet.europa.eu and write it as Markdown.

Reads  migration/path_map.json  (from build_migration_plan.py)
Writes docs/01_user-guide/**/*.md  + shared image assets

What it does
------------
* Pulls the Astra theme's .entry-content block, discarding chrome (menus,
  breadcrumbs, footer, scroll-to-top).
* Converts to Markdown with html2text, unwrapped so diffs stay line-per-
  paragraph rather than reflowing whole blocks on a one-word edit.
* Downloads every /wp-content/uploads/ image into a shared assets directory and
  rewrites the reference. Images are deduplicated by content hash, so a picture
  used on six pages is stored once.
* Rewrites internal links. A link to https://help.reportnet.europa.eu/fme-connectors/
  becomes a relative path to the new Markdown file, so the docs are navigable
  offline and MkDocs can validate them.
* Records pages whose content area is empty rather than writing a blank file.

Idempotent: re-running overwrites the same files with the same bytes.

Usage:
  python tools/crawl_help_content.py --dry-run     # report only, write nothing
  python tools/crawl_help_content.py

Dependencies:
  pip install requests beautifulsoup4 html2text
"""

import os
import re
import sys
import json
import time
import hashlib
import argparse
from pathlib import Path
from urllib.parse import urlparse, urljoin, unquote

import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

try:
    import html2text
except ImportError:
    print("ERROR: pip install html2text", file=sys.stderr)
    sys.exit(1)

SITE = "https://help.reportnet.europa.eu"
CONTENT_SELECTOR = ".entry-content"
TITLE_SELECTOR = "h1.entry-title"
ASSETS_DIRNAME = "assets"

# Links that are already broken on the live site. Each 404s today; the target
# on the right is the page the author clearly meant. Fixing them here rather
# than carrying dead links into the new site.
LINK_FIXES = {
    "/reportnet-3-1-reporter-howto/create-csv-files/":
        "/reportnet-3-1-reporter-howto/load-data/create-csv-files/",
    "/sample-page/create-a-dataset-schema/quality-control-rules/custom-validations-sql/":
        "/sample-page/quality-control-rules/custom-validations-sql/",
}

# Non-image files linked from page bodies (sample scripts, spreadsheets). These
# are content, not decoration, so they come across with the pages.
DOWNLOADABLE_EXT = {".zip", ".py", ".pdf", ".docx", ".doc", ".xlsx", ".xls",
                    ".csv", ".txt", ".json", ".xml", ".gpkg", ".png", ".jpg",
                    ".jpeg", ".gif", ".svg"}

# WordPress/Astra fragments that sit inside .entry-content but are chrome, not
# content. Removed before conversion.
STRIP_SELECTORS = [
    ".ast-single-post-order",     # previous/next post links
    ".post-navigation",
    ".ast-scroll-top",
    ".sharedaddy",
    ".addtoany_share_save_container",
    "script",
    "style",
    "noscript",
]


def make_session():
    s = requests.Session()
    s.headers["User-Agent"] = "reportnet-docs-migration/1.0"
    return s


def make_converter():
    h = html2text.HTML2Text()
    h.body_width = 0          # never hard-wrap; keeps git diffs readable
    h.unicode_snob = True     # keep — and ’ rather than mangling to ASCII
    # body_width=0 already prevents links being split across lines, so
    # protect_links would only add <angle brackets> around every target.
    h.protect_links = False
    h.wrap_links = False
    h.mark_code = True
    h.ignore_images = False
    h.ignore_links = False
    h.single_line_break = False
    return h


def clean_markdown(md):
    """Tidy html2text output.

    html2text marks code blocks with [code]/[/code] when mark_code is on, and
    leaves ragged blank lines. Normalise both so the result reads like
    hand-written Markdown.
    """
    md = re.sub(r"\[code\]\s*\n?", "```\n", md)
    md = re.sub(r"\n?\s*\[/code\]", "\n```", md)
    md = md.replace(" ", " ")            # non-breaking spaces from the CMS
    md = re.sub(r"[ \t]+\n", "\n", md)        # trailing whitespace
    md = re.sub(r"\n{3,}", "\n\n", md)        # collapse blank-line runs
    return md.strip() + "\n"


class Crawler:
    def __init__(self, plan, docs_root, dry_run=False, delay=0.4):
        self.entries = plan["entries"]
        self.docs_root = Path(docs_root)
        self.dry_run = dry_run
        self.delay = delay
        self.session = make_session()
        self.conv = make_converter()

        # old site path -> new docs path, for internal link rewriting
        self.link_map = {e["old_path"]: e["new_path"] for e in self.entries}
        self.title_map = {e["old_path"]: e["title"] for e in self.entries}

        self.assets_dir = self.docs_root / ASSETS_DIRNAME
        self.asset_by_hash = {}   # content hash -> saved filename
        self.stats = {
            "pages": 0, "empty": 0, "stub_index": 0, "failed": 0,
            "images": 0, "images_deduped": 0, "files_downloaded": 0,
            "links_rewritten": 0, "links_external": 0, "links_unresolved": 0,
            "link_text_retitled": 0,
        }
        # Section landing page -> its child entries, for generating stubs.
        self.children = {}
        for e in self.entries:
            self.children.setdefault(e["parent_dir"], []).append(e)
        self.empty_pages, self.failures, self.unresolved = [], [], []

    # -- assets ----------------------------------------------------------
    def save_asset(self, url):
        """Download an image, dedupe by content hash, return its filename."""
        try:
            resp = self.session.get(url, timeout=45)
            resp.raise_for_status()
        except Exception as exc:
            self.failures.append(f"image {url}: {exc}")
            return None

        digest = hashlib.sha256(resp.content).hexdigest()
        if digest in self.asset_by_hash:
            self.stats["images_deduped"] += 1
            return self.asset_by_hash[digest]

        name = unquote(Path(urlparse(url).path).name)
        name = re.sub(r"[^A-Za-z0-9._-]", "-", name) or f"{digest[:12]}.png"

        # Distinct images that share a filename get a short hash suffix.
        target = self.assets_dir / name
        if not self.dry_run and target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                stem, ext = os.path.splitext(name)
                name = f"{stem}-{digest[:8]}{ext}"
                target = self.assets_dir / name

        if not self.dry_run:
            self.assets_dir.mkdir(parents=True, exist_ok=True)
            target.write_bytes(resp.content)

        self.asset_by_hash[digest] = name
        self.stats["images"] += 1
        return name

    # -- rewriting -------------------------------------------------------
    def relative(self, from_path, to_path):
        src_dir = Path(from_path).parent
        return Path(os.path.relpath(Path(to_path), src_dir)).as_posix()

    def normalise_path(self, href):
        """Site path with a trailing slash — except for links to actual files.

        WordPress page URLs always end in a slash. Appending one to
        /wp-content/uploads/foo.zip would turn a real file into a directory
        that resolves to nothing, so file-looking paths are left alone.
        """
        p = urlparse(href).path or "/"
        if os.path.splitext(p)[1].lower() in DOWNLOADABLE_EXT:
            return p
        if not p.endswith("/"):
            p += "/"
        return p

    def rewrite(self, soup, page_new_path):
        """Rewrite links and images in place, before Markdown conversion."""
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#") or href.startswith("mailto:"):
                continue
            absolute = urljoin(SITE, href)
            if urlparse(absolute).netloc != urlparse(SITE).netloc:
                self.stats["links_external"] += 1
                continue

            path = self.normalise_path(absolute)
            path = LINK_FIXES.get(path, path)
            fragment = urlparse(absolute).fragment

            # A link to an uploaded file: bring the file across too.
            if "/wp-content/uploads/" in path:
                name = self.save_asset(urljoin(SITE, path))
                if name:
                    a["href"] = self.relative(
                        page_new_path, self.docs_root / ASSETS_DIRNAME / name)
                    self.stats["files_downloaded"] += 1
                continue

            target = self.link_map.get(path)
            if target:
                rel = self.relative(page_new_path, target)
                a["href"] = f"{rel}#{fragment}" if fragment else rel
                self.stats["links_rewritten"] += 1
                # Authors often pasted the bare URL as the link text. Once the
                # href is a relative path that text is meaningless, so swap in
                # the destination page's title.
                if a.get_text(strip=True).rstrip("/") == absolute.rstrip("/"):
                    a.string = self.title_map.get(path, a.get_text(strip=True))
                    self.stats["link_text_retitled"] += 1
            else:
                # Internal link to a page that is not being migrated — in
                # practice the two empty stubs. Leave it absolute so it keeps
                # working while WordPress is up, and report it.
                self.stats["links_unresolved"] += 1
                self.unresolved.append(f"{page_new_path} -> {path}")

        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            absolute = urljoin(SITE, src)
            if "/wp-content/uploads/" not in absolute:
                continue
            name = self.save_asset(absolute)
            if name:
                rel = self.relative(page_new_path,
                                    self.docs_root / ASSETS_DIRNAME / name)
                img["src"] = rel
            # Responsive attributes are meaningless in Markdown and would
            # otherwise leak into the output.
            for attr in ("srcset", "sizes", "width", "height", "loading",
                         "decoding", "class", "fetchpriority"):
                img.attrs.pop(attr, None)

    # -- pages -----------------------------------------------------------
    def stub_index(self, entry):
        """Landing page for a section whose WordPress page is blank."""
        section_dir = entry["new_path"].rsplit("/", 1)[0]
        kids = sorted(self.children.get(section_dir, []), key=lambda e: e["order"])
        lines = [
            "---",
            f'title: "{entry["title"]}"',
            f'source_url: {entry["old_url"]}',
            "---",
            "",
            f"# {entry['title']}",
            "",
            "<!-- The WordPress page at source_url has an empty content area."
            " This index was generated from the section's children. Replace it"
            " with a real introduction. -->",
            "",
        ]
        for kid in kids:
            rel = self.relative(entry["new_path"], kid["new_path"])
            lines.append(f"- [{kid['title']}]({rel})")
        return "\n".join(lines) + "\n"

    def fetch_page(self, entry):
        url = entry["old_url"]
        try:
            resp = self.session.get(url, timeout=45)
            resp.raise_for_status()
        except Exception as exc:
            self.stats["failed"] += 1
            self.failures.append(f"page {url}: {exc}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        content = soup.select_one(CONTENT_SELECTOR)
        if content is None:
            self.stats["failed"] += 1
            self.failures.append(f"page {url}: no {CONTENT_SELECTOR} block")
            return None

        for sel in STRIP_SELECTORS:
            for node in content.select(sel):
                node.decompose()

        if not content.get_text(strip=True) and not content.find("img"):
            # A section landing page still needs a file, or the section has no
            # index and its URL 404s. Generate one listing the children, which
            # is more useful than the blank page WordPress serves today.
            if entry["is_section"]:
                self.stats["stub_index"] += 1
                self.empty_pages.append(entry["new_path"] + "  (stub index generated)")
                return self.stub_index(entry)
            self.stats["empty"] += 1
            self.empty_pages.append(entry["new_path"])
            return None

        heading = soup.select_one(TITLE_SELECTOR)
        title = heading.get_text(strip=True) if heading else entry["title"]

        self.rewrite(content, entry["new_path"])
        body = clean_markdown(self.conv.handle(str(content)))

        front = [
            "---",
            f'title: "{title}"',
            f'source_url: {url}',
            "---",
            "",
            f"# {title}",
            "",
        ]
        return "\n".join(front) + body

    def run(self):
        total = len(self.entries)
        for i, entry in enumerate(sorted(self.entries, key=lambda e: e["new_path"]), 1):
            print(f"[{i:>2}/{total}] {entry['old_path']}")
            md = self.fetch_page(entry)
            if md is None:
                continue
            self.stats["pages"] += 1
            if not self.dry_run:
                out = Path(entry["new_path"])
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(md, encoding="utf-8")
            time.sleep(self.delay)

    def report(self):
        print("\n" + "=" * 60)
        print("CRAWL SUMMARY" + ("  (dry run — nothing written)" if self.dry_run else ""))
        print("=" * 60)
        for k, v in self.stats.items():
            print(f"  {k:20} {v}")

        if self.empty_pages:
            print(f"\nEmpty content area, not written ({len(self.empty_pages)}):")
            for p in self.empty_pages:
                print(f"  {p}")
        if self.unresolved:
            print(f"\nInternal links left absolute ({len(self.unresolved)}) —"
                  " review these:")
            for u in sorted(set(self.unresolved)):
                print(f"  {u}")
        if self.failures:
            print(f"\nFailures ({len(self.failures)}):")
            for f in self.failures:
                print(f"  {f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="migration/path_map.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--delay", type=float, default=0.4,
                    help="seconds between requests; be polite to the EEA host")
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    crawler = Crawler(plan, plan["docs_root"], args.dry_run, args.delay)
    crawler.run()
    crawler.report()


if __name__ == "__main__":
    main()
