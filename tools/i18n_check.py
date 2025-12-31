#!/usr/bin/env python3
"""
Basic i18n consistency checks for Jekyll HTML pages.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


EXCLUDE_DIRS = {"_includes", "_layouts", "_site", "node_modules", ".git"}
FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass
class PageInfo:
    path: Path
    lang: str | None
    ref: str | None


def parse_front_matter(content: str) -> Dict[str, str]:
    match = FRONT_MATTER_RE.match(content)
    if not match:
        return {}
    raw = match.group(1)
    data = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def find_pages(root: Path) -> List[PageInfo]:
    pages = []
    for path in root.rglob("*.html"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        content = path.read_text(encoding="utf-8")
        fm = parse_front_matter(content)
        pages.append(PageInfo(path=path, lang=fm.get("lang"), ref=fm.get("ref")))
    return pages


def main() -> int:
    root = Path(__file__).parent.parent
    pages = find_pages(root)

    errors = []
    warnings = []

    refs_en = {p.ref for p in pages if p.lang == "en" and p.ref}
    refs_non_en = [p for p in pages if p.lang and p.lang != "en"]

    for page in pages:
        rel = page.path.relative_to(root).as_posix()
        if page.lang is None or page.ref is None:
            errors.append(f"{rel}: missing lang or ref in front matter")
            continue
        if page.lang == "en" and page.path.parts[0] in {"es", "fr", "pt", "de", "it", "ar", "zh-hans"}:
            errors.append(f"{rel}: English lang set in translated path")
        if page.lang != "en" and page.path.parts[0] == "index.html":
            errors.append(f"{rel}: non-English page in root without lang=en")

    for page in refs_non_en:
        if page.ref and page.ref not in refs_en:
            rel = page.path.relative_to(root).as_posix()
            warnings.append(f"{rel}: translation exists without English ref {page.ref}")

    print("i18n check:")
    if errors:
        print("Errors:")
        for err in errors:
            print(f"- {err}")
    else:
        print("Errors: None")

    if warnings:
        print("Warnings:")
        for warn in warnings:
            print(f"- {warn}")
    else:
        print("Warnings: None")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
