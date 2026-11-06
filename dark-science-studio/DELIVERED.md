# Delivered videos — where to watch

The `.mp4` files are **deliberately not committed to git** (repo rule: `renders/*/*.mp4`
is git-ignored, and a 20 MB binary per episode would bloat every clone). They live in
Google Drive, which is the delivery destination. Local copies are wiped whenever the
sandbox resets, so **Drive is the only durable copy** — this file exists so the links
survive a reset.

| ID | Episode | Length | Drive folder (video + cover + docs) |
|---|---|---|---|
| **DS-003** | Mirror Life — "38 Scientists Begged Us Not to Build This" | 44.00 s | https://drive.google.com/drive/folders/1jIGd-9tl6mfvWk-6eT5s_M8jmwu4hAAZ |
| **DS-004** | Fatal Familial Insomnia — "The Family That Couldn't Sleep" | 49.60 s | https://drive.google.com/drive/folders/1DxVgwRxq6OX0llij2uWM_glyKCXX8f57 |
| **DS-005** | Betelgeuse / Siwarha — "There's Another Star Inside Betelgeuse" | 48.47 s | https://drive.google.com/drive/folders/1EqGFiZ1bUJzMHPgFJtX9xQyuXQ1vjqS_ |
| **DS-006** | KM3NeT KM3-230213A — "A 220 PeV Particle Hit the Sea" | 49.60 s | https://drive.google.com/drive/folders/1bqz6HoBpkTVBRZVDVO9fDD6fyqjgr_9_ |
| **DS-007** | N. fowleri — "The Amoeba That Eats Brains: 167 Cases, 4 Survivors" | 46.72 s | https://drive.google.com/drive/folders/1jLeKZbYaJ-8yg0qrMzTngpbSfzTlI8hL |

## Direct links

**DS-003 final.mp4** — 44.00 s · 1080×1920 · 30 fps · 21.41 MB
https://drive.google.com/file/d/1GrnD9-CbU3sid3Zob9CaI29rbTVs3V17/view
cover: https://drive.google.com/file/d/1JUDsFnfDX-JHbQttJ4yUMuM8b-WoVThh/view

**DS-004 final.mp4** — 49.60 s · 1080×1920 · 30 fps · 19.64 MB
https://drive.google.com/file/d/1cRZ49rJXjcWFflpvh9bMnywHn9VOHD7d/view
cover: https://drive.google.com/file/d/1G5ASmt07SZMJ6Qs82zsfLpMsC05amoxL/view

**DS-005** — 48.47 s · 38.57 MB · https://drive.google.com/file/d/1HQ5mQijQdGtIn0NA29gFyrItoLMArZU6/view
**DS-006** — 49.60 s · 26.21 MB · https://drive.google.com/file/d/1RbhPrx03ME2TmKu2S1H9MdHFwZx3cs1d/view
**DS-007** — 46.72 s · 20.34 MB · https://drive.google.com/file/d/1bkvTkkb2Zek79tqpfxKIFsrSW1lWLtIB/view

Both folders also contain: `cover_frame.png`, `publishing_kit.md`, `publishing_kit.txt`,
`sources_and_licenses.md`, `captions.srt`, `script.txt` (+ `qa_selfreview.md` for DS-004).

## Re-rendering from source

`build/` and `renders/` are git-ignored and do **not** survive a sandbox reset. To rebuild
any episode from the committed sources:

```bash
./setup.sh && tools/fetch_assets.sh          # venv, npm deps, chromium, piper voice

python tools/voice_kit.py   --project projects/DS-004 --build build/DS-004
python tools/make_timeline.py --project projects/DS-004 --build build/DS-004
python tools/audio_kit.py   --project projects/DS-004 --build build/DS-004

# bundle + render (see README for the exact remotion invocation)
python tools/qa_gate.py --project projects/DS-004 --build build/DS-004 \
                        --video renders/DS-004/final.mp4
```

Everything needed is committed: `projects/DS-00N/` holds the script, timeline,
captions, spec and docs; `tools/` holds the whole engine. Only the heavy
intermediates are rebuildable rather than versioned.


## DS-005…DS-007 — one-command rebuild

These three were produced through `pipeline.py`, which chains every stage and skips
anything already built:

```bash
python pipeline.py --video DS-005 --stage all     # voice -> timeline -> score -> render -> qa
python pipeline.py --video DS-005,DS-006,DS-007 --stage render --force   # batch re-render
python tools/cover_kit.py --project projects/DS-005                      # clickbait cover
python tools/docgen.py --project projects/DS-005                         # spec + kit.txt + self-review
```

Logs land in `logs/<id>.log`; per-stage state in `build/<id>/status.json`, so a
killed session resumes by re-running the same command.
