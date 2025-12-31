#!/usr/bin/env python3
"""
UI audit for static HTML pages.
Checks structural accessibility and readability heuristics.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Tuple


EXCLUDE_DIRS = {"_includes", "_layouts", "_site", "node_modules", ".git"}


@dataclass
class FileReport:
    path: Path
    has_main: bool = False
    h1_count: int = 0
    paragraph_lengths: List[int] = field(default_factory=list)
    missing_alt: List[str] = field(default_factory=list)
    icon_buttons_missing_label: int = 0
    has_skip_link: bool = False

    @property
    def avg_paragraph_length(self) -> float:
        if not self.paragraph_lengths:
            return 0.0
        return sum(self.paragraph_lengths) / len(self.paragraph_lengths)


class AuditParser(HTMLParser):
    def __init__(self, report: FileReport) -> None:
        super().__init__()
        self.report = report
        self._in_p = False
        self._p_chunks: List[str] = []
        self._button_stack: List[Tuple[bool, bool, List[str]]] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}

        if tag == "main" and attrs_dict.get("id") == "main-content":
            self.report.has_main = True

        if tag == "h1":
            self.report.h1_count += 1

        if tag == "p":
            self._in_p = True
            self._p_chunks = []

        if tag == "img":
            if "alt" not in attrs_dict:
                src = attrs_dict.get("src", "").strip() or "(no src)"
                self.report.missing_alt.append(src)

        if tag == "button":
            has_aria_label = bool(attrs_dict.get("aria-label"))
            has_aria_labelledby = bool(attrs_dict.get("aria-labelledby"))
            self._button_stack.append((has_aria_label, has_aria_labelledby, []))

        if tag == "a":
            href = attrs_dict.get("href", "")
            classes = attrs_dict.get("class", "")
            if href == "#main-content" and "skip-link" in classes.split():
                self.report.has_skip_link = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self._in_p:
            text = re.sub(r"\s+", " ", "".join(self._p_chunks)).strip()
            if text:
                self.report.paragraph_lengths.append(len(text))
            self._in_p = False
            self._p_chunks = []

        if tag == "button" and self._button_stack:
            has_label, has_labelledby, text_chunks = self._button_stack.pop()
            text = re.sub(r"\s+", " ", "".join(text_chunks)).strip()
            if not text and not has_label and not has_labelledby:
                self.report.icon_buttons_missing_label += 1

    def handle_data(self, data: str) -> None:
        if self._in_p:
            self._p_chunks.append(data)
        if self._button_stack:
            self._button_stack[-1][2].append(data)


def find_html_files(root: Path) -> List[Path]:
    files = []
    for path in root.rglob("*.html"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def audit_file(path: Path) -> FileReport:
    content = path.read_text(encoding="utf-8")
    report = FileReport(path=path)

    parser = AuditParser(report)
    parser.feed(content)
    parser.close()
    return report


def render_report(reports: List[FileReport], root: Path) -> str:
    errors = []
    warnings = []

    for report in reports:
        rel = report.path.relative_to(root).as_posix()
        if not report.has_main:
            errors.append(f"{rel}: missing #main-content")
        if report.h1_count != 1:
            errors.append(f"{rel}: expected 1 <h1>, found {report.h1_count}")
        if report.missing_alt:
            errors.append(f"{rel}: {len(report.missing_alt)} img tag(s) missing alt")
        if report.icon_buttons_missing_label:
            errors.append(f"{rel}: {report.icon_buttons_missing_label} icon-only button(s) missing aria-label")
        if not report.has_skip_link:
            warnings.append(f"{rel}: missing skip link")
        if report.avg_paragraph_length > 95:
            warnings.append(
                f"{rel}: average paragraph length {report.avg_paragraph_length:.1f}ch exceeds 95ch"
            )

    total = len(reports)
    total_images_missing_alt = sum(len(r.missing_alt) for r in reports)
    total_icon_buttons_missing_label = sum(r.icon_buttons_missing_label for r in reports)
    total_missing_main = sum(1 for r in reports if not r.has_main)
    total_h1_issues = sum(1 for r in reports if r.h1_count != 1)
    total_missing_skip = sum(1 for r in reports if not r.has_skip_link)
    total_long_paragraphs = sum(1 for r in reports if r.avg_paragraph_length > 95)

    lines = [
        "# UI Audit Report",
        "",
        "## Summary",
        f"- Files scanned: {total}",
        f"- Missing #main-content: {total_missing_main}",
        f"- Pages with invalid h1 count: {total_h1_issues}",
        f"- Images missing alt: {total_images_missing_alt}",
        f"- Icon-only buttons missing aria-label: {total_icon_buttons_missing_label}",
        f"- Pages missing skip link: {total_missing_skip}",
        f"- Pages with avg paragraph length > 95ch: {total_long_paragraphs}",
        "",
        "## Errors",
    ]
    lines.extend([f"- {item}" for item in errors] or ["- None"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend([f"- {item}" for item in warnings] or ["- None"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    root = Path(__file__).parent.parent
    reports = [audit_file(path) for path in find_html_files(root)]
    report_text = render_report(reports, root)

    print(report_text)

    output_path = root / "docs" / "UI-AUDIT.md"
    output_path.write_text(report_text + "\n", encoding="utf-8")

    has_errors = any(
        (not r.has_main) or (r.h1_count != 1) or r.missing_alt or r.icon_buttons_missing_label
        for r in reports
    )
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
