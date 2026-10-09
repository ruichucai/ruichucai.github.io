#!/usr/bin/env python3
"""Lightweight, read-only checks for this static academic website."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []

def check(condition, message):
    if not condition:
        ERRORS.append(message)

for rel, expected in [
    ("index.html", "https://ruichucai.github.io/"),
    ("zh-cn/index.html", "https://ruichucai.github.io/zh-cn/"),
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    canonicals = re.findall(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', text, re.I)
    check(canonicals == [expected], f"{rel}: expected exactly one canonical URL {expected}")
    check(not re.search(r"20206/\d{1,2}/\d{1,2}", text), f"{rel}: malformed year like 20206/MM/DD")
    check(not re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']noindex', text, re.I),
          f"{rel}: noindex directive conflicts with indexing policy")
    blocks = re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script\s*>', text, re.I | re.S)
    if rel == "index.html":
        check(len(blocks) == 1, "index.html: expected exactly one JSON-LD block")
        if len(blocks) == 1:
            try:
                data = json.loads(blocks[0])
                check(data.get("@type") == "Person", "index.html: JSON-LD @type should be Person")
            except json.JSONDecodeError as exc:
                ERRORS.append(f"index.html: invalid JSON-LD: {exc}")

robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
check("Allow: /" in robots and "Sitemap: https://ruichucai.github.io/sitemap.xml" in robots,
      "robots.txt: expected site-wide crawl allowance and sitemap declaration")
for url in ("https://ruichucai.github.io/", "https://ruichucai.github.io/zh-cn/"):
    check(f"<loc>{url}</loc>" in sitemap, f"sitemap.xml: missing {url}")

if ERRORS:
    print("Site checks failed:")
    for error in ERRORS:
        print(f" - {error}")
    sys.exit(1)
print("Site checks passed.")


# Publication-list audit: report-only so legacy bibliography inconsistencies do not
# block unrelated content updates. These checks never rewrite academic records.
def audit_publications(rel, text):
    from html import unescape
    match = re.search(
        r"<h2\b[^>]*>\s*(?:Selected Publications|主要论文).*?</h2>(.*?)(?=<h2\b|$)",
        text, re.I | re.S,
    )
    if not match:
        print(f"WARNING: {rel}: publication section not found; audit skipped")
        return

    section = match.group(1)
    items = re.findall(r"<li\b[^>]*>(.*?)</li\s*>", section, re.I | re.S)
    normalized = []
    linked_records = 0
    for item in items:
        if re.search(r"<a\b[^>]*href=[\"']https?://", item, re.I):
            linked_records += 1
        visible = re.sub(r"<[^>]+>", " ", item)
        visible = unescape(visible)
        visible = re.sub(r"\s+", " ", visible).strip().lower()
        # Ignore empty/list-layout artifacts; preserve the full citation for duplicate checks.
        if visible:
            normalized.append(visible)

    missing_links = len(normalized) - linked_records
    print(f"Publication links: {rel}: {linked_records}/{len(normalized)} records have an external HTTP(S) link")
    if normalized and missing_links:
        print(f"INFO: {rel}: {missing_links} record(s) have no external HTTP(S) link; review link coverage when convenient")

    duplicates = sorted({entry for entry in normalized if normalized.count(entry) > 1})
    if duplicates:
        print(f"WARNING: {rel}: {len(duplicates)} exact duplicate publication record(s) detected")
        for entry in duplicates:
            print(f"  - duplicate: {entry[:180]}")
    else:
        print(f"Publication audit: {rel}: {len(normalized)} records; no exact duplicates detected")

    checks = [
        (r",\s*,", "repeated comma"),
        (r",(?=[A-Za-z])", "comma immediately followed by a name/word"),
        (r"</li\s*>\s*</li\s*>", "consecutive closing list-item tags"),
        (r"</i>\s*</b>", "potentially mismatched italic/bold closing tags"),
    ]
    for pattern, label in checks:
        count = len(re.findall(pattern, section, re.I))
        if count:
            print(f"WARNING: {rel}: {count} possible formatting issue(s): {label}")

# Run advisory publication checks on both language versions. Warnings are
# intentionally non-fatal until records are reviewed by a human.
for rel in ("index.html", "zh-cn/index.html"):
    audit_publications(rel, (ROOT / rel).read_text(encoding="utf-8"))
