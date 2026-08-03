#!/usr/bin/env python3
"""
Fetches the last-updated date and author for every wiki page, then:
  1. Adds/updates  updated: and  updated_by:  in each .md file's frontmatter.
  2. Writes  wiki_output/STALENESS_REPORT.md  with all pages sorted oldest-first.

Usage:
  python fetch_dates.py --session-cookie "VALUE"
"""

import re
import sys
import time
import argparse
import requests
from datetime import datetime, date
from pathlib import Path
from urllib.parse import quote

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

BASE_URL   = "https://taskman.eionet.europa.eu"
PROJECT_ID = "reportnet-3"
WIKI_DIR   = Path("/Users/janbliki/Documents/GitHub/R3_documentation/wiki_output")

# How old (in days) before a page is flagged as stale
STALE_THRESHOLD = 365


def make_session(cookie):
    s = requests.Session()
    s.headers["User-Agent"] = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17 Safari/605.1.15"
    )
    s.cookies.set("_redmine_session", cookie, domain="taskman.eionet.europa.eu")
    return s


def check_auth(session):
    r = session.get(f"{BASE_URL}/projects/{PROJECT_ID}/wiki", timeout=15)
    r.raise_for_status()
    from urllib.parse import urlparse
    parsed = urlparse(r.url)
    if parsed.path.startswith("/login"):
        raise PermissionError(
            "Session cookie is invalid or expired — please copy a fresh one."
        )


def fetch_page_date(session, slug):
    """
    Returns (updated_str, author_str) from the 'author' span on a wiki page.
    updated_str is like '2022-11-25 15:35', author_str is the display name.
    """
    url = f"{BASE_URL}/projects/{PROJECT_ID}/wiki/{quote(slug, safe='')}"
    r = session.get(url, timeout=20)
    if r.status_code == 404:
        return None, None
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # The 'author' paragraph contains "Name, YYYY-MM-DD HH:MM"
    author_el = soup.find(class_="author")
    if not author_el:
        return None, None

    text = author_el.get_text(strip=True)
    # Format: "Firstname Lastname, 2023-04-12 09:14"
    m = re.search(r'(.+?),\s*(\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?)', text)
    if m:
        return m.group(2).strip(), m.group(1).strip()

    return text, ""


def update_frontmatter(md_path: Path, updated: str, author: str):
    """Insert or replace 'updated:' and 'updated_by:' in YAML frontmatter."""
    text = md_path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        return  # no frontmatter to update

    # Find end of frontmatter block
    end = text.index("---", 3)
    fm   = text[3:end]
    body = text[end + 3:]

    # Remove existing updated/updated_by lines
    fm = re.sub(r'^updated:.*\n?', '', fm, flags=re.MULTILINE)
    fm = re.sub(r'^updated_by:.*\n?', '', fm, flags=re.MULTILINE)

    # Append new fields
    fm = fm.rstrip("\n") + f'\nupdated: "{updated}"\n'
    if author:
        fm += f'updated_by: "{author}"\n'

    md_path.write_text("---" + fm + "---" + body, encoding="utf-8")


def age_label(updated_str: str, today: date) -> str:
    """Return a human-readable age string and staleness flag."""
    try:
        dt = datetime.strptime(updated_str[:10], "%Y-%m-%d").date()
        days = (today - dt).days
        years = days // 365
        months = (days % 365) // 30
        if years >= 1:
            age = f"{years}y {months}m"
        else:
            age = f"{months}m"
        flag = " ⚠️" if days > STALE_THRESHOLD else ""
        return age + flag, days
    except ValueError:
        return "?", 99999


def collect_slugs():
    """Walk wiki_output subfolders to find all .md files."""
    results = []
    for md in sorted(WIKI_DIR.rglob("*.md")):
        if md.name == "STALENESS_REPORT.md":
            continue
        # Derive folder name (relative to wiki_output)
        rel = md.relative_to(WIKI_DIR)
        folder = str(rel.parent) if rel.parent != Path(".") else "—"
        slug   = md.stem
        results.append((folder, slug, md))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--session-cookie", required=True, metavar="VALUE")
    parser.add_argument("--delay", type=float, default=0.3)
    args = parser.parse_args()

    session = make_session(args.session_cookie)

    print("Checking authentication…")
    try:
        check_auth(session)
        print("OK\n")
    except PermissionError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    pages = collect_slugs()
    today = date.today()
    results = []  # (folder, slug, updated_str, author, age_label, days)

    for i, (folder, slug, md_path) in enumerate(pages, 1):
        print(f"[{i:3}/{len(pages)}] {folder}/{slug}", end=" … ")
        sys.stdout.flush()

        updated, author = fetch_page_date(session, slug)
        if updated:
            update_frontmatter(md_path, updated, author)
            age, days = age_label(updated, today)
            print(f"{updated}  ({age})")
        else:
            print("no date found")
            age, days = "?", 99999

        results.append((folder, slug, updated or "", author or "", age, days))
        time.sleep(args.delay)

    # --- Write staleness report ---
    results.sort(key=lambda r: r[5], reverse=True)  # oldest first

    report_lines = [
        "# Wiki staleness report",
        f"\nGenerated: {today}  |  Stale threshold: >{STALE_THRESHOLD} days\n",
        "| Page | Folder | Last updated | Author | Age |",
        "|------|--------|--------------|--------|-----|",
    ]
    for folder, slug, updated, author, age, days in results:
        title = slug.replace("_", " ")
        report_lines.append(
            f"| {title} | {folder} | {updated} | {author} | {age} |"
        )

    report_path = WIKI_DIR / "STALENESS_REPORT.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    stale = sum(1 for r in results if r[5] > STALE_THRESHOLD)
    print(f"\nDone.")
    print(f"  {len(results)} pages updated with dates")
    print(f"  {stale} pages flagged as stale (>{STALE_THRESHOLD} days old)")
    print(f"  Report: {report_path}")


if __name__ == "__main__":
    main()
