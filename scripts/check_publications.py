#!/usr/bin/env python3
"""Read-only quality checks for publication and project metadata in the static site."""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []

class LinkChecker(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href is not None and not href.strip():
            ERRORS.append(f"{self.path}: anchor has an empty href")

for rel in ("index.html", "zh-cn/index.html"):
    content = (ROOT / rel).read_text(encoding="utf-8")
    parser = LinkChecker(rel)
    parser.feed(content)
    if re.search(r"</li>\s*</li>", content, re.I):
        ERRORS.append(f"{rel}: consecutive closing list-item tags; review list markup")
    if re.search(r"</b>\s*,\s*,", content):
        ERRORS.append(f"{rel}: duplicated comma after bold author markup")

    headings = ("Selected Projects", "科研项目")
    positions = [content.find(h) for h in headings if content.find(h) >= 0]
    start = min(positions, default=-1)
    if start >= 0:
        end = content.find("</ul>", start)
        section = content[start:end if end >= 0 else len(content)]
        records = re.findall(r"<li\b[^>]*>(.*?)</li>", section, re.I | re.S)
        normalized = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", item)).strip() for item in records]
        seen = set()
        for record in normalized:
            if record and record in seen:
                ERRORS.append(f"{rel}: duplicate project record: {record[:100]}")
            seen.add(record)

if ERRORS:
    print("Publication/project checks failed:")
    for error in ERRORS:
        print(f" - {error}")
    sys.exit(1)
print("Publication/project checks passed.")
