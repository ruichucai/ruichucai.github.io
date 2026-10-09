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
