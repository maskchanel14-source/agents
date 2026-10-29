# Installed from harveyz-skill (Harvey's skill collection)

Source: `github.com/harveyzhang814/harveyz-skill` at commit `a9077aa`, package
`harveyz-skill` v0.42.1. Installed 29 October 2026 with the repo's own CLI at
project scope:

```bash
node bin/cli.js install --skill rephrase   --target claude --scope project
node bin/cli.js install --skill handoff    --target claude --scope project
node bin/cli.js install --skill clip-url   --target claude --scope project
node bin/cli.js install --skill forge-doc  --target claude --scope project
```

## What was deliberately not installed

- **Git hooks** (`hooks/`, `scripts/git/install-git-hooks.sh`). Upstream ships
  pre-commit and pre-push hooks that block commits to `main` and `staging`. This
  repo has its own review flow and an agent working on a keyed branch; adding a
  third party's commit gate would break pushes for reasons unrelated to the work.
- **Shell tools** (`hub`, `sync`, `browser-fetch`, `roster`). None of them is used
  by the skills below.
- **Skill test fixtures.** `forge-doc/tests/` alone was 4.4 MB of generated
  docx and pdf samples. Removed after install; the scripts and styles are intact.

## Local patch, needed to make forge-doc run

`scripts/md_to_docx.py` loads `assets/default-style.json` as its base style and
exits if the file is missing, but that file is not shipped in the package. Fixed by
copying `bcg-style.json` to `default-style.json`. Without it every DOCX conversion
fails with "not found — reinstall the skill".

## What each installed skill is used for here

| Skill | Use |
| --- | --- |
| `handoff` | `docs/commute/2026-10-29-outreach-handoff.md` |
| `forge-doc` | `outreach/OUTREACH-DOSSIER.docx`, BCG style |
| `rephrase` | Restating terse owner instructions before acting on them |
| `clip-url` | Installed, unused. It needs browser-fetch and a knowledge root; the sandbox has no working browser automation. |

## Reinstalling

The install is a plain copy into this directory. Re-running the CLI with `--force`
overwrites it, which will also remove the `default-style.json` fix.
