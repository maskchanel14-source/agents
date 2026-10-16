from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_landing_page.py"
SPEC = importlib.util.spec_from_file_location("validate_landing_page", SCRIPT)
assert SPEC and SPEC.loader
qa = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = qa
SPEC.loader.exec_module(qa)


VALID_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="A clear description that explains this product to visitors and helps them decide what to do next.">
  <title>Example landing page</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header><nav aria-label="Main navigation"><a href="#main">Content</a></nav></header>
  <main id="main">
    <h1>Example product</h1>
    <h2>Benefits</h2>
    <a href="https://example.test" target="_blank" rel="noopener">Learn more</a>
    <img src="hero.jpg" width="1200" height="700" alt="A product on a desk">
    <form action="/subscribe" method="post">
      <label for="email">Email</label>
      <input id="email" name="email" type="email">
      <button type="submit">Subscribe</button>
    </form>
  </main>
  <footer>Footer</footer>
</body>
</html>
"""


class LandingPageAuditTests(unittest.TestCase):
    def test_valid_page_and_reduced_motion_stylesheet_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            html_path = root / "index.html"
            html_path.write_text(VALID_HTML, encoding="utf-8")
            (root / "styles.css").write_text(
                ".hero { transition: opacity 200ms ease; }\n"
                "@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; scroll-behavior: auto !important; } }\n",
                encoding="utf-8",
            )

            findings = qa.audit_html(html_path)

        self.assertEqual([], findings)

    def test_reports_accessibility_structure_and_placeholder_defects(self) -> None:
        html = """<!doctype html>
<html>
<head><title></title></head>
<body>
  <h1></h1><h3>Skipped level</h3><h1>Second title</h1>
  <img src="cake.jpg">
  <a href="#"></a>
  <a href="#missing">Jump</a>
  <a href="https://example.test" target="_blank">External</a>
  <button></button>
  <button aria-labelledby="missing-label"></button>
  <input type="email" name="email">
</body>
</html>
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            html_path = Path(temp_dir) / "bad.html"
            html_path.write_text(html, encoding="utf-8")
            findings = qa.audit_html(html_path)

        codes = {finding.code for finding in findings}
        self.assertTrue(
            {
                "LANG_MISSING",
                "VIEWPORT_MISSING",
                "TITLE_MISSING",
                "MAIN_MISSING",
                "MULTIPLE_H1",
                "HEADING_NAME_MISSING",
                "HEADING_LEVEL_SKIP",
                "IMAGE_ALT_MISSING",
                "PLACEHOLDER_LINK",
                "LINK_NAME_MISSING",
                "FRAGMENT_TARGET_MISSING",
                "EXTERNAL_LINK_REL",
                "BUTTON_NAME_MISSING",
                "ARIA_LABELLED_BY_TARGET_MISSING",
                "FORM_CONTROL_LABEL_MISSING",
            }.issubset(codes)
        )

    def test_warns_if_motion_has_no_reduced_motion_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            html_path = root / "index.html"
            html_path.write_text(VALID_HTML, encoding="utf-8")
            (root / "styles.css").write_text(".hero { animation: appear 300ms ease; }", encoding="utf-8")

            findings = qa.audit_html(html_path)

        self.assertIn("REDUCED_MOTION_MISSING", {finding.code for finding in findings})

    def test_ignores_motion_declarations_inside_css_comments(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            html_path = root / "index.html"
            html_path.write_text(VALID_HTML, encoding="utf-8")
            (root / "styles.css").write_text("/* transition: all 1s; */ .hero { color: #111; }", encoding="utf-8")

            findings = qa.audit_html(html_path)

        self.assertNotIn("REDUCED_MOTION_MISSING", {finding.code for finding in findings})

    def test_reports_duplicate_ids(self) -> None:
        html = VALID_HTML.replace(
            '<h1>Example product</h1>',
            '<h1 id="same">Example product</h1><p id="same">Duplicate</p>',
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            html_path = Path(temp_dir) / "duplicate.html"
            html_path.write_text(html, encoding="utf-8")
            findings = qa.audit_html(html_path)

        self.assertIn("DUPLICATE_ID", {finding.code for finding in findings})


if __name__ == "__main__":
    unittest.main()
