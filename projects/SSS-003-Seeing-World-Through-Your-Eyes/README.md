# SSS-003 — Seeing the World Through Your Eyes (`EyeNeRF` Dark Science Archive #003)

Reproducible **Cinema Engine v5** pipeline for **Small Signal Studio Episode #003 (`SSS-003`)**, profiling **University of Maryland, College Park's** CVPR 2024 Oral presentation:
> **Hadi Alzayer\*, Kevin Zhang\*, Brandon Y. Feng, Christopher Metzler, Jia-Bin Huang**, *"Seeing the World through Your Eyes"*, `arXiv:2306.09348` (`https://world-from-eyes.github.io/`).

## Master Specifications (Cinema Engine v5)

| Parameter | Verified Output |
| :--- | :--- |
| **Resolution / Aspect** | `1080 × 1920` (`9:16` Vertical Cinema Stage: `1036×583` widescreen & `1036×720` square `1080p` ablation views) |
| **Frame Rate / Frames** | `60.00 fps` (`3,467` frames, zero `minterpolate` smear) |
| **Duration** | `57.783s` (`< 60.0s` YouTube Shorts ceiling, `0.60s` silence cliffhanger at `49.185s–49.785s`) |
| **Source Footage Quality** | **100% native `1080p` vertical height** (`1920×1080` & `1080×1080`) across **36 non-repeating shots** (`0` overlaps) |
| **Voluntary Conversion Cue** | Non-begging Peak-End Dossier Toast (`t=50.10s–54.80s`: `ARCHIVE #003 • LIKE TO SAVE PAPER • + SUBSCRIBE FOR #004`) |
| **Video Codec** | H.264 `High@L4.2`, `yuv420p`, `CRF 17` (`27.74 MiB`, `+faststart`, Frame 0 = `9:16` Viral Cover) |
| **Audio Master** | `voice-00` narration + C#-minor Dark Science analog bass drone & optical sonar shimmer, `48 kHz` AAC `256 kbps`, **`-14.0 LUFS`** (`-1.2 dBTP`) |

## Pipeline Files

- `shotlist.py` — 36-shot non-repeating `1080p` timeline validator (`validate_shotlist()`).
- `build_audio.py` — Auto-resolves `ffmpeg` (`PATH` or `imageio-ffmpeg`), trims & paces 8 `voice-00` beats, detects natural pause valleys for `captions.srt` / `timings.json`, inserts the `0.60s` chilling silence dropout, and normalizes the stereo master to `-14.0 LUFS`.
- `make_covers.py` — Composites the high-CTR, factually accurate Dark Science `9:16` Shorts Cover (`1080×1920`) and `16:9` YouTube Thumbnail (`1920×1080`).
- `render_ultrahd.py` — Cinema Engine v5 `1080p60` renderer with Peak-End Voluntary Like/Subscribe Dossier Toast and physical eye-zoom loop continuity.
