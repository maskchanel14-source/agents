# QC report — footage rebuild checked 3 November 2026 (Asia/Jakarta)

## Render result
- **Status:** full Remotion footage rebuild rendered successfully (exit code 0).
- **File:** `video.mp4`
- **Runtime:** 41.003 s / 1230 frames.
- **Video:** H.264 High / yuvj420p, 1080×1920, 30 fps, 5022 kb/s video stream.
- **Audio:** AAC-LC, stereo, 48 kHz, 317 kb/s audio stream.
- **File size:** 27.4 MB at verification.

## Mechanical verification
- Full decode ran with FFmpeg `-v error -xerror`: **PASS** (no decode errors).
- `blackdetect` recorded only the intentional opening fade from 0.00–0.10 s; no subsequent black interval was detected using `pic_th=0.97`, `pix_th=0.10`.
- Representative decoded output frames were inspected at ~0.5, 4.2, 10.3, 16.7, 21.3, 28.3, 33.0, 37.0 and 40.2 seconds. They show real moving mushroom footage in the hook, report, DNA, pathway, unknown-chemical, evidence, safety and ending beats. Caption and evidence overlays remain inside the vertical frame.
- The old R3F/Three.js mushroom, miniature-figure, molecular and warning-ring scenes are not in this render. The evidence section now remains on full-screen footage and explicitly states that it is generic mushroom footage rather than the named species.
- Cover inspected at its native 1080×1920 and 270×480 small-screen preview: headline remains legible and the AI-illustration label is visible.

## Audio technical check
- Integrated loudness: **−19.6 LUFS**.
- Loudness range: **2.4 LU**.
- Measured true peak: **−4.2 dBFS**; no clipping indicated by this measurement.
- The voice track is present to 40.36 s inside a 41.0 s render; the ambient bed carries the tail.
- **Listening limitation:** this environment exposes technical audio analysis but no reliable human listening tool. I verified track presence, durations, codec and loudness/peak measurements; I do not claim a human listening review.

## Editorial and asset truth check
- All main visual beats use moving, user-provided generic mushroom footage from the licensed source set documented in `PUBLISH-KIT.md` and `source-manifest/ASSET-MANIFEST.md`.
- The on-screen `GENERIC MUSHROOM FOOTAGE` disclosure is always present; the DNA evidence card additionally says that the background is not the named species.
- The *Lanmaoa asiatica* low-resolution still is no longer used in the edited composition or rebuilt render.
- Safety language remains explicit: no tasting and no self-experimentation with wild mushrooms.
