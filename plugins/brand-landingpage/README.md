# Brand Landing Page

A brand-first landing-page builder that turns a short brief into a distinctive, responsive page. Stitch is an optional visual-generation accelerator; the workflow continues with local HTML/CSS/JavaScript when it is unavailable. The builder includes motion/accessibility guidance and a dependency-free structural QA script.

## What it does

- Extracts product, audience, value proposition, CTA, language and brand context without forcing a long interview.
- Chooses a clear visual direction and page structure based on the actual offer instead of repeating generic card layouts.
- Uses Stitch when already connected, then refines its output into one responsive production page.
- Defines restrained motion choreography with `prefers-reduced-motion` support.
- Checks semantic HTML, document metadata, headings, links, image alternatives, form labels, linked CSS and reduced-motion overrides.
- Guides browser checks for mobile/desktop widths, keyboard behavior, CTA destinations and genuine form handling.
- Delivers an HTML bundle, design tokens, design notes and a deployment checklist that reports the actual QA status.

## Quick start

Use the `brand-landingpage` skill for a single-purpose marketing page. It extracts known facts from the user's request, asks only about material unknowns, records assumptions and builds a first draft without blocking on reversible visual preferences.

Stitch/MCP is optional. If it is not already available, do not block on an API key; use the local implementation path. No global dependency installation is required for the bundled HTML validator.

Run the static checker from the plugin root:

```bash
python scripts/validate_landing_page.py path/to/index.html
python scripts/validate_landing_page.py path/to/index.html --strict
```

Run its unit tests from the repository root:

```bash
python -m unittest discover -s plugins/brand-landingpage/tests -v
```

## File structure

```text
brand-landingpage/
  .claude-plugin/plugin.json
  .codex-plugin/plugin.json
  scripts/
    validate_landing_page.py        # Dependency-free structural QA
  skills/brand-landingpage/
    SKILL.md                        # Builder workflow
    references/
      interview-framework.md
      quality-playbook.md           # Visual, motion, accessibility and launch gates
      state-and-pitfalls.md
      stitch-architecture.md
  tests/
    test_validate_landing_page.py
  README.md
```

## Limitations

- Static checks cannot prove contrast, responsive appearance, keyboard usability, browser compatibility, JavaScript behavior, server-backed form delivery or real-world performance. Use a real browser for those checks; do not call a generated design render a browser screenshot.
- A form is not functional without a verified backend/action and privacy handling. The builder must not imply otherwise.
- Stitch output may be static or need cleanup. Treat it as a starting point, not deployment-ready code.
- Keep private/uncommissioned concepts private and noindex; publish only with the appropriate owner authorization.
