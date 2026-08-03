#!/usr/bin/env python3
"""
Redmine wiki extractor for Reportnet 3 (HTML scraping edition).

The Redmine JSON API on this instance is locked to API-key auth only, so this
script scrapes the rendered HTML pages instead, which work with a browser
session cookie.

How to get your session cookie (one-time, while logged in):
  1. Log in at https://taskman.eionet.europa.eu (AD + MFA as normal).
  2. Open DevTools:  Cmd+Option+I  (Chrome/Safari/Firefox on Mac)
  3. Go to:  Application (Chrome) / Storage (Firefox/Safari) → Cookies
             → https://taskman.eionet.europa.eu
  4. Copy the value of the  _redmine_session  cookie.
  5. Pass it with  --session-cookie "VALUE".

Usage:
  python extract_wiki.py --session-cookie "VALUE"
  python extract_wiki.py --session-cookie "VALUE" --output ./wiki_pages

Dependencies:
  pip install requests beautifulsoup4 html2text
"""

import re
import sys
import time
import argparse
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote, quote

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

try:
    import html2text as _h2t
except ImportError:
    print("ERROR: pip install html2text", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://taskman.eionet.europa.eu"
PROJECT_ID = "reportnet-3"


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

def make_session(session_cookie):
    s = requests.Session()
    s.headers["User-Agent"] = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17 Safari/605.1.15"
    )
    s.cookies.set("_redmine_session", session_cookie,
                  domain="taskman.eionet.europa.eu")
    return s


def check_auth(session):
    r = session.get(f"{BASE_URL}/projects/{PROJECT_ID}/wiki", timeout=15)
    r.raise_for_status()
    if "/login" in r.url or "Sign in" in r.text[:2000]:
        raise PermissionError("Session cookie is invalid or expired. "
                              "Log in again and copy a fresh cookie.")
    return r


# ---------------------------------------------------------------------------
# Page discovery
# ---------------------------------------------------------------------------

def list_wiki_pages(session):
    """
    Return a list of page-title strings by scraping the wiki index page.
    Redmine's wiki index lists all pages (including orphans).
    """
    r = session.get(
        f"{BASE_URL}/projects/{PROJECT_ID}/wiki/index",
        timeout=15,
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    titles = []
    prefix = f"/projects/{PROJECT_ID}/wiki/"
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(prefix):
            slug = href[len(prefix):].split("?")[0].split("#")[0]
            if slug and slug not in ("new", "index", "date_index",
                                     "export", "diff"):
                titles.append(unquote(slug))

    # Deduplicate, preserve order
    seen = set()
    unique = []
    for t in titles:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique


# ---------------------------------------------------------------------------
# Fetch a single wiki page
# ---------------------------------------------------------------------------

def fetch_wiki_page(session, slug):
    """
    Return (title, soup_of_wiki_div, attachment_links, updated_str).
    attachment_links: list of (display_text, href) for .attachment anchors.
    """
    url = f"{BASE_URL}/projects/{PROJECT_ID}/wiki/{quote(slug, safe='')}"
    r = session.get(url, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # Page title from <h1 class="wiki-page"> or <title>
    title_tag = soup.find("h2", {"id": "main-menu-name"})
    page_title_tag = soup.find("div", {"id": "wiki_title"})
    title = slug.replace("_", " ")
    if page_title_tag:
        title = page_title_tag.get_text(strip=True)
    elif title_tag:
        title = title_tag.get_text(strip=True)
    else:
        html_title = soup.find("title")
        if html_title:
            # "Page Name - Project - Taskman..."
            title = html_title.get_text().split(" - ")[0].strip()

    # Wiki content
    wiki_div = soup.find("div", class_="wiki")

    # Attachments listed below the wiki body
    attachments = []
    att_section = soup.find("div", class_="attachments")
    if att_section:
        for a in att_section.find_all("a", href=True):
            attachments.append((a.get_text(strip=True), a["href"]))

    # Also pick up inline attachment links inside the wiki body
    if wiki_div:
        for a in wiki_div.find_all("a", class_="attachment", href=True):
            attachments.append((a.get_text(strip=True), a["href"]))

    # Deduplicate attachments by href
    seen_hrefs = set()
    unique_att = []
    for text, href in attachments:
        if href not in seen_hrefs:
            seen_hrefs.add(href)
            unique_att.append((text, href))

    # Updated date
    updated = ""
    updated_tag = soup.find("p", class_="author")
    if updated_tag:
        updated = updated_tag.get_text(strip=True)

    return title, wiki_div, unique_att, updated


# ---------------------------------------------------------------------------
# HTML → Markdown conversion
# ---------------------------------------------------------------------------

def make_converter(base_url, page_slug, attachments_rel_path):
    """Return a configured html2text converter."""
    h = _h2t.HTML2Text(baseurl=base_url)
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0          # no hard line-wrapping
    h.protect_links = False
    h.wrap_links = False
    h.mark_code = True
    return h


def rewrite_links(wiki_div, slug, att_map):
    """
    Rewrite hrefs and src attributes in-place before html2text sees them:
      - /projects/PROJECT/wiki/OtherPage  →  OtherPage.md
      - /attachments/download/ID/file.ext  →  attachments/file.ext
      - /attachments/ID  (inline img)  →  attachments/filename (from att_map)
    """
    prefix = f"/projects/{PROJECT_ID}/wiki/"

    for a in wiki_div.find_all("a", href=True):
        href = a["href"]
        if href.startswith(prefix):
            target = unquote(href[len(prefix):]).split("?")[0].split("#")[0]
            a["href"] = f"{target}.md"
        elif href.startswith("/attachments/"):
            # Try to resolve to a local path
            parts = href.split("/")
            if len(parts) >= 5 and parts[2] == "download":
                filename = unquote(parts[4])
                a["href"] = f"attachments/{filename}"
            elif href in att_map:
                a["href"] = f"attachments/{att_map[href]}"

    for img in wiki_div.find_all("img", src=True):
        src = img["src"]
        if src.startswith("/attachments/download/"):
            parts = src.split("/")
            if len(parts) >= 5:
                filename = unquote(parts[4])
                img["src"] = f"attachments/{filename}"
        elif src.startswith("/attachments/"):
            if src in att_map:
                img["src"] = f"attachments/{att_map[src]}"

    # Remove paragraph anchors (clutter in Markdown)
    for a in wiki_div.find_all("a", class_="wiki-anchor"):
        a.decompose()

    return wiki_div


def html_to_markdown(wiki_div):
    if wiki_div is None:
        return ""
    h = _h2t.HTML2Text()
    h.body_width = 0
    h.ignore_images = False
    h.ignore_links = False
    h.mark_code = True
    return h.handle(str(wiki_div)).strip()


# ---------------------------------------------------------------------------
# Attachment downloading
# ---------------------------------------------------------------------------

def resolve_attachment_url(session, href):
    """
    /attachments/ID  →  follow redirect to get download URL and filename.
    /attachments/download/ID/filename  →  use directly.
    """
    if href.startswith("/attachments/download/"):
        parts = href.split("/")
        filename = unquote(parts[4]) if len(parts) >= 5 else "attachment"
        return BASE_URL + href, filename

    # Follow redirect from /attachments/ID
    url = BASE_URL + href
    r = session.head(url, allow_redirects=True, timeout=15)
    final = r.url
    filename = final.rstrip("/").split("/")[-1]
    filename = unquote(filename)
    return final, filename


def download_file(session, url, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = session.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with dest.open("wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def safe_name(s):
    return re.sub(r'[<>:"/\\|?*]', '_', s)


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Redmine wiki to Markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--session-cookie", required=True, metavar="VALUE",
        help="Value of the _redmine_session cookie from your browser",
    )
    parser.add_argument(
        "--output", default="./wiki_output", metavar="DIR",
        help="Output directory (default: ./wiki_output)",
    )
    parser.add_argument(
        "--delay", type=float, default=0.3, metavar="SEC",
        help="Seconds between requests (default: 0.3)",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    session = make_session(args.session_cookie)

    print("Checking authentication…")
    try:
        check_auth(session)
        print("OK — session is valid.\n")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching page list…")
    slugs = list_wiki_pages(session)
    print(f"Found {len(slugs)} pages.\n")

    errors = []

    for i, slug in enumerate(slugs, 1):
        print(f"[{i:3}/{len(slugs)}] {slug}")

        try:
            title, wiki_div, att_links, updated = fetch_wiki_page(session, slug)
        except Exception as e:
            print(f"         ERROR: {e}")
            errors.append((slug, str(e)))
            continue

        time.sleep(args.delay)

        safe_slug = safe_name(slug)
        att_dir = output_dir / safe_slug / "attachments"

        # Download attachments; build href→filename map for link rewriting
        att_map = {}  # href → local filename
        for display, href in att_links:
            try:
                dl_url, filename = resolve_attachment_url(session, href)
                dest = att_dir / filename
                if not dest.exists():
                    if args.verbose:
                        print(f"         attachment: {filename}")
                    download_file(session, dl_url, dest)
                att_map[href] = filename
                time.sleep(args.delay)
            except Exception as e:
                print(f"         ERROR downloading {href}: {e}")
                errors.append((f"{slug}/{href}", str(e)))

        # Rewrite links inside the wiki div, then convert to Markdown
        if wiki_div:
            rewrite_links(wiki_div, slug, att_map)
        md_body = html_to_markdown(wiki_div)

        # YAML front matter
        fm = [
            "---",
            f'title: "{title}"',
        ]
        if updated:
            fm.append(f'updated: "{updated}"')
        fm.append("---\n")

        md_path = output_dir / f"{safe_slug}.md"
        md_path.write_text("\n".join(fm) + "\n" + md_body + "\n", encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Done.  {len(slugs) - len(errors)}/{len(slugs)} pages saved to {output_dir.resolve()}")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for name, msg in errors:
            print(f"  {name}: {msg}")


if __name__ == "__main__":
    main()
