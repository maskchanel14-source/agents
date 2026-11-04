SHORTS-2026-024B — "The Twenty-Minute Heist"
REVISION 3 — 2D editorial explainer with a host
============================================================

68.5 s vertical short · 1080x1920 · 30 fps · English VO
Rendered 2026-11-05

A host walks the viewer through the biggest crypto theft on record: what
happened, in plain language, with one illustration per beat.

  Host            vector presenter, on screen for the hook, the hot-wallet
                  explanation, the "how did they get in?" question, the
                  "one laptop" beat and the close. His mouth is driven by the
                  real voice track (audio/mouth.json).
  Illustration    one editorial card per beat, crossfaded, each with a slow
                  push. Two beats (the attribution dossier and the record
                  chart) are hand-drawn vector scenes.
  Type            the numbers are the design: every stat is set in gold,
                  revealed word by word in time with the voice.
  Bottom rail     chapter rail + a key-numbers strip, which fade out whenever
                  the host is on screen.
  Grade           warm bloom, vignette, procedural film grain.

Story, numbers and sources are unchanged from revisions 1 and 2 — only the
telling is new. Full change list: REVISION-3.md. The script is script-rev3.txt.


WHAT IS IN HERE
---------------
01_VIDEO.mp4              The master. H.264 ~3.0 Mb/s + AAC 192 k mono.
02_COVER.png              1080x1920 frame from the hook, for the thumbnail.
03_AUDIO-MIX-14LUFS.wav   68.50 s final mix (music + VO + 5 SFX, ducked -6 dB).
04_STILLS.zip             13 stills, one per beat.
05_QA-REPORTS.zip         The 7 QA agent reports.
06_SOURCE-ARCHIVE.zip     facts.json, both scripts, the changelogs, the
                          generated scene art and the full Remotion source.
PUBLISH-KIT.md            YouTube title / description / tags / chapters.
QC-REPORT.md              Measured QC: per-beat exposure, audio, known issues.
REVISION-2.md             What revision 2 changed (semi-realist 3D).
REVISION-3.md             What revision 3 changed (this one).
SHA256SUMS.txt            Checksums for every file in this folder.


HOW TO RE-RENDER
----------------
  cd media-production
  npm install
  npm run studio                     # Remotion Studio, preview the comp
  python3 scripts/shorts024_audio_rev3.py   # rebuild VO timing + mix + exports
  bash scripts/render-shorts024-rev3.sh     # full 2055-frame render
  ffmpeg -i out/video-silent-rev3.mp4 -i audio/final3.wav \
         -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -ac 1 \
         -shortest out/final.mp4

Composition id: SHORTS-2026-024-Binance63B.
Revision 2 is still renderable as SHORTS-2026-024-Binance63B-3D-rev2.

The scene illustrations are not in git (see .gitignore) — they are in
06_SOURCE-ARCHIVE.zip under public/shorts024/scenes/. Unzip that into
media-production/public/ before rendering.

2D needs no GPU: ~0.55 s/frame, so the whole film renders in ~19 minutes.
(Revision 2's 3D took 2 h 35 min on software GL.)


SOURCES
-------
Every spoken number is in facts.json with the exact source sentence and URL:
TRM Labs, Chainalysis, AP, NBC/Reuters, CNN, Al Jazeera and CoinDesk.
Full link list in PUBLISH-KIT.md.


GIT
---
Branch arena/ce22919c-agents, PR #22 on maskchanel14-source/agents.
Rendered binaries are gitignored; source and docs are committed.
