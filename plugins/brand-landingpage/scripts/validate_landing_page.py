#!/usr/bin/env python3
"""Run dependency-free structural QA on a generated landing-page HTML file.

This catches common, statically observable defects. It does not replace browser,
keyboard, contrast, responsive, or runtime testing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None


class LandingPageParser(HTMLParser):
    """Collect page structure and report high-confidence HTML issues."""

    VOID_ELEMENTS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.findings: list[Finding] = []
        self.html_lang: str | None = None
        self.has_doctype = False
        self.has_viewport = False
        self.description: str | None = None
        self.title_text: list[str] = []
        self.in_title = False
        self.main_count = 0
        self.nav_labels: list[str] = []
        self.headings: list[tuple[int, str, int]] = []
        self.heading_stack: list[dict[str, object]] = []
        self.ids: dict[str, int] = {}
        self.fragment_refs: list[tuple[str, int]] = []
        self.aria_labelledby_refs: list[tuple[str, int]] = []
        self.link_stack: list[dict[str, object]] = []
        self.button_stack: list[dict[str, object]] = []
        self.label_targets: set[str] = set()
        self.label_depth = 0
        self.controls: list[dict[str, object]] = []
        self.forms: list[dict[str, object]] = []
        self.stylesheet_hrefs: list[str] = []
        self.inline_css: list[str] = []
        self.in_style = False
        self.style_depth = 0

    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str | None]:
        return {name.lower(): value for name, value in attrs}

    def _add(self, severity: str, code: str, message: str, line: int | None = None) -> None:
        self.findings.append(Finding(severity, code, message, line))

    def handle_decl(self, decl: str) -> None:
        if decl.strip().lower().startswith("doctype html"):
            self.has_doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = self._attrs(attrs)
        line = self.getpos()[0]

        labelledby = (values.get("aria-labelledby") or "").split()
        if labelledby:
            self.aria_labelledby_refs.extend((target, line) for target in labelledby)
        if values.get("style"):
            self.inline_css.append(str(values["style"]))

        element_id = values.get("id")
        if element_id:
            if element_id in self.ids:
                self._add("error", "DUPLICATE_ID", f"Duplicate id '{element_id}'.", line)
            else:
                self.ids[element_id] = line

        if tag == "html":
            self.html_lang = (values.get("lang") or "").strip() or None
        elif tag == "meta":
            name = (values.get("name") or "").strip().lower()
            content = (values.get("content") or "").strip()
            if name == "viewport":
                self.has_viewport = bool(re.search(r"width\s*=\s*device-width", content, re.I))
            elif name == "description":
                self.description = content
        elif tag == "title":
            self.in_title = True
        elif tag == "main":
            self.main_count += 1
        elif tag == "nav":
            self.nav_labels.append(
                (values.get("aria-label") or values.get("aria-labelledby") or "").strip()
            )
        elif re.fullmatch(r"h[1-6]", tag):
            self.heading_stack.append(
                {"level": int(tag[1]), "line": line, "parts": []}
            )
        elif tag == "img":
            if "alt" not in values:
                self._add("error", "IMAGE_ALT_MISSING", "Image is missing an alt attribute.", line)
            if not (values.get("src") or "").strip():
                self._add("error", "IMAGE_SRC_MISSING", "Image is missing a source URL.", line)
            if values.get("alt"):
                alt = str(values["alt"]).strip()
                for link in self.link_stack:
                    link["parts"].append(alt)  # type: ignore[union-attr]
        elif tag == "a":
            href = (values.get("href") or "").strip()
            if not href:
                self._add("error", "LINK_HREF_MISSING", "Link is missing a destination.", line)
            elif href == "#":
                self._add("error", "PLACEHOLDER_LINK", "Link uses '#' as a placeholder destination.", line)
            elif href.lower().startswith("javascript:"):
                self._add("error", "JAVASCRIPT_LINK", "Avoid javascript: URLs; use a button and a real handler.", line)
            elif href.startswith("#") and len(href) > 1:
                self.fragment_refs.append((href[1:], line))

            if (values.get("target") or "").lower() == "_blank":
                rel = set((values.get("rel") or "").lower().split())
                if not {"noopener", "noreferrer"}.intersection(rel):
                    self._add("warning", "EXTERNAL_LINK_REL", "target='_blank' should use rel='noopener' or rel='noreferrer'.", line)

            self.link_stack.append(
                {"attrs": values, "parts": [], "line": line}
            )
        elif tag == "button":
            self.button_stack.append(
                {"attrs": values, "parts": [], "line": line}
            )
        elif tag == "label":
            target = (values.get("for") or "").strip()
            if target:
                self.label_targets.add(target)
            self.label_depth += 1
        elif tag in {"input", "select", "textarea"}:
            control_type = (values.get("type") or "text").lower() if tag == "input" else tag
            self.controls.append(
                {
                    "tag": tag,
                    "type": control_type,
                    "id": (values.get("id") or "").strip(),
                    "name": (values.get("name") or "").strip(),
                    "aria_label": (values.get("aria-label") or "").strip(),
                    "aria_labelledby": (values.get("aria-labelledby") or "").strip(),
                    "value": (values.get("value") or "").strip(),
                    "inside_label": self.label_depth > 0,
                    "line": line,
                }
            )
        elif tag == "form":
            self.forms.append(
                {
                    "action": (values.get("action") or "").strip(),
                    "method": (values.get("method") or "").strip(),
                    "line": line,
                }
            )
        elif tag == "link":
            rel = set((values.get("rel") or "").lower().split())
            href = (values.get("href") or "").strip()
            if "stylesheet" in rel and href:
                self.stylesheet_hrefs.append(href)
        elif tag == "style":
            self.in_style = True
            self.style_depth += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.VOID_ELEMENTS:
            self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_text.append(data)
        if self.in_style:
            self.inline_css.append(data)
        for heading in self.heading_stack:
            heading["parts"].append(data)  # type: ignore[union-attr]
        for link in self.link_stack:
            link["parts"].append(data)  # type: ignore[union-attr]
        for button in self.button_stack:
            button["parts"].append(data)  # type: ignore[union-attr]

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif re.fullmatch(r"h[1-6]", tag) and self.heading_stack:
            heading = self.heading_stack.pop()
            text = " ".join(str(part).strip() for part in heading["parts"] if str(part).strip())
            self.headings.append((int(heading["level"]), text, int(heading["line"])))
        elif tag == "a" and self.link_stack:
            link = self.link_stack.pop()
            values = link["attrs"]
            accessible_name = (
                values.get("aria-label")
                or values.get("aria-labelledby")
                or values.get("title")
                or ""
            ).strip()
            if not accessible_name:
                accessible_name = " ".join(
                    str(part).strip() for part in link["parts"] if str(part).strip()
                )
            if not accessible_name:
                self._add("error", "LINK_NAME_MISSING", "Link has no accessible name; add text or an aria-label.", int(link["line"]))
        elif tag == "button" and self.button_stack:
            button = self.button_stack.pop()
            values = button["attrs"]
            accessible_name = (
                values.get("aria-label")
                or values.get("aria-labelledby")
                or values.get("title")
                or ""
            ).strip()
            if not accessible_name:
                accessible_name = " ".join(
                    str(part).strip() for part in button["parts"] if str(part).strip()
                )
            if not accessible_name:
                self._add("error", "BUTTON_NAME_MISSING", "Button has no accessible name; add visible text or an aria-label.", int(button["line"]))
        elif tag == "label" and self.label_depth:
            self.label_depth -= 1
        elif tag == "style" and self.style_depth:
            self.style_depth -= 1
            self.in_style = self.style_depth > 0

    def finish(self) -> list[Finding]:
        if not self.has_doctype:
            self._add("error", "DOCTYPE_MISSING", "Add the HTML5 <!doctype html> declaration.")
        if not self.html_lang:
            self._add("error", "LANG_MISSING", "Set a valid lang attribute on the root <html> element.")
        if not self.has_viewport:
            self._add("error", "VIEWPORT_MISSING", "Add a responsive viewport meta tag with width=device-width.")
        if not "".join(self.title_text).strip():
            self._add("error", "TITLE_MISSING", "Add a non-empty <title> element.")
        if not self.description:
            self._add("warning", "DESCRIPTION_MISSING", "Add a concise meta description for search and link previews.")
        elif not 50 <= len(self.description) <= 160:
            self._add("warning", "DESCRIPTION_LENGTH", f"Meta description is {len(self.description)} characters; aim for roughly 50–160.")
        if self.main_count == 0:
            self._add("error", "MAIN_MISSING", "Add one <main> landmark around the primary page content.")
        elif self.main_count > 1:
            self._add("error", "MULTIPLE_MAIN", f"Found {self.main_count} <main> landmarks; use one per page.")
        if not any(level == 1 for level, _, _ in self.headings):
            self._add("error", "H1_MISSING", "Add a descriptive page-level <h1>.")
        elif sum(level == 1 for level, _, _ in self.headings) > 1:
            self._add("error", "MULTIPLE_H1", "Use a single visible <h1> for the primary page title.")

        if len(self.nav_labels) > 1 and any(not label for label in self.nav_labels):
            self._add("warning", "NAV_LABEL_MISSING", "Give each of multiple navigation landmarks a distinct accessible label.")

        previous_level = 0
        for level, text, line in self.headings:
            if not text:
                self._add("error", "HEADING_NAME_MISSING", f"<h{level}> has no text.", line)
            if previous_level and level > previous_level + 1:
                self._add("warning", "HEADING_LEVEL_SKIP", f"Heading jumps from h{previous_level} to h{level}; use a logical hierarchy.", line)
            previous_level = level

        for target, line in self.fragment_refs:
            if target not in self.ids:
                self._add("error", "FRAGMENT_TARGET_MISSING", f"Internal link points to missing id '#{target}'.", line)
        for target, line in self.aria_labelledby_refs:
            if target not in self.ids:
                self._add("error", "ARIA_LABELLED_BY_TARGET_MISSING", f"aria-labelledby references missing id '{target}'.", line)

        for control in self.controls:
            control_type = str(control["type"])
            if control_type == "hidden":
                continue
            value_name = control_type in {"submit", "button", "reset", "image"} and bool(control["value"])
            labeled = (
                bool(control["aria_label"])
                or bool(control["aria_labelledby"])
                or bool(control["inside_label"])
                or (bool(control["id"]) and str(control["id"]) in self.label_targets)
                or value_name
            )
            if not labeled:
                self._add("error", "FORM_CONTROL_LABEL_MISSING", f"<{control['tag']}> control has no associated label or accessible name.", int(control["line"]))
            if self.forms and not control["name"] and control_type not in {"button", "submit", "reset", "image"}:
                self._add("warning", "FORM_CONTROL_NAME_MISSING", f"<{control['tag']}> control has no name attribute; form handlers usually need one.", int(control["line"]))

        for form in self.forms:
            if not form["action"]:
                self._add("warning", "FORM_ACTION_UNSET", "Form has no action; verify that a real JavaScript/backend handler is connected.", int(form["line"]))
            if not form["method"]:
                self._add("warning", "FORM_METHOD_UNSET", "Form has no explicit method; choose GET or POST intentionally.", int(form["line"]))

        return self.findings


def _load_css(parser: LandingPageParser, html_path: Path, explicit_css: list[str]) -> tuple[list[str], list[Finding]]:
    css_texts = list(parser.inline_css)
    findings: list[Finding] = []
    candidates: list[Path] = []

    for href in parser.stylesheet_hrefs:
        parsed = urlsplit(href)
        if parsed.scheme or href.startswith("//") or not parsed.path:
            continue
        candidates.append((html_path.parent / parsed.path).resolve())

    for css_arg in explicit_css:
        css_path = Path(css_arg)
        if not css_path.is_absolute():
            relative_to_html = (html_path.parent / css_path).resolve()
            css_path = relative_to_html if relative_to_html.exists() else css_path.resolve()
        candidates.append(css_path)

    seen: set[Path] = set()
    for css_path in candidates:
        if css_path in seen:
            continue
        seen.add(css_path)
        if not css_path.is_file():
            findings.append(Finding("warning", "CSS_NOT_FOUND", f"Could not read linked stylesheet: {css_path}"))
            continue
        try:
            css_texts.append(css_path.read_text(encoding="utf-8"))
        except OSError as exc:
            findings.append(Finding("warning", "CSS_READ_FAILED", f"Could not read {css_path}: {exc}"))
    return css_texts, findings


def _audit_motion(css_texts: list[str]) -> list[Finding]:
    combined = "\n".join(css_texts)
    combined = re.sub(r"/\*.*?\*/", "", combined, flags=re.S)
    has_motion = bool(
        re.search(r"\b(?:animation(?:-name|-duration|-timing-function)?|transition(?:-duration|-property|-timing-function)?|scroll-behavior)\s*:", combined, re.I)
        or re.search(r"@keyframes\b", combined, re.I)
    )
    has_reduced_motion = bool(
        re.search(r"prefers-reduced-motion\s*:\s*reduce", combined, re.I)
    )
    if has_motion and not has_reduced_motion:
        return [Finding(
            "warning",
            "REDUCED_MOTION_MISSING",
            "CSS includes motion but no prefers-reduced-motion: reduce override was found.",
        )]
    return []


def audit_html(html_path: Path, explicit_css: list[str] | None = None) -> list[Finding]:
    try:
        source = html_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [Finding("error", "HTML_READ_FAILED", f"Could not read {html_path}: {exc}")]

    parser = LandingPageParser()
    try:
        parser.feed(source)
        parser.close()
    except Exception as exc:  # HTMLParser should be tolerant; surface unusual parser failures.
        return [Finding("error", "HTML_PARSE_FAILED", f"Could not parse {html_path}: {exc}")]

    findings = parser.finish()
    css_texts, css_findings = _load_css(parser, html_path.resolve(), explicit_css or [])
    findings.extend(css_findings)
    findings.extend(_audit_motion(css_texts))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check generated landing-page HTML for common structural, accessibility and motion issues."
    )
    parser.add_argument("html", type=Path, help="HTML file to audit")
    parser.add_argument("--css", action="append", default=[], help="Additional stylesheet to audit (repeatable)")
    parser.add_argument("--strict", action="store_true", help="Return a failing status for warnings as well as errors")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON findings")
    args = parser.parse_args(argv)

    findings = audit_html(args.html, args.css)
    if args.json:
        print(json.dumps([asdict(item) for item in findings], indent=2))
    elif not findings:
        print(f"PASS  {args.html}: no static issues found")
    else:
        for item in findings:
            line = f":{item.line}" if item.line is not None else ""
            print(f"{item.severity.upper():7} {item.code:28} {args.html}{line}  {item.message}")
        errors = sum(item.severity == "error" for item in findings)
        warnings = sum(item.severity == "warning" for item in findings)
        print(f"\n{errors} error(s), {warnings} warning(s).")

    has_errors = any(item.severity == "error" for item in findings)
    has_warnings = any(item.severity == "warning" for item in findings)
    return 1 if has_errors or (args.strict and has_warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
