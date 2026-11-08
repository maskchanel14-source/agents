# SSS-002 — Universal Manipulation Interface (`UMI`): How a $73 GoPro Claw Taught Robots Human Hands

Reproducible production pipeline for **Small Signal Studio Episode #002 (`SSS-002`)**, profiling **Stanford University, Columbia University, MIT, and Toyota Research Institute's** RSS 2024 Best Systems Paper Finalist:
> **Cheng Chi\*, Zhenjia Xu\*, Chuer Pan, Eric Cousineau, Benjamin Burchfiel, Siyuan Feng, Russ Tedrake, Shuran Song**, *"Universal Manipulation Interface: In-The-Wild Robot Teaching Without In-The-Wild Robots"*, `arXiv:2402.10329` (`https://umi-gripper.github.io/`).

## Master Specifications (Upgraded v4 Cinema Stage)

| Parameter | Verified Output |
| :--- | :--- |
| **Resolution / Aspect** | `1080 × 1920` (`9:16` Vertical Cinema Stage, 1:1+ supersampled native pixels) |
| **Frame Rate / Frames** | `60.00 fps` (`3,485` frames, zero `minterpolate` smear) |
| **Duration** | `58.083s` (`< 60.0s` YouTube Shorts ceiling, `0.60s` silence cliffhanger at `47.98s–48.58s`) |
| **Source Footage Quality** | **100% native `1080p` vertical height** (`1920×1080` & `1320×1080`) across **36 non-repeating shots** (`0` overlaps) |
| **Video Codec** | H.264 `High@L4.2`, `yuv420p`, `CRF 17` (`40.33 MiB`, `+faststart`, Frame 0 = `9:16` Viral Cover) |
| **Audio Master** | `voice-00` narration + stereo D-minor synth & kinematic sub-impacts, `48 kHz` AAC `256 kbps`, **`-14.0 LUFS`** (`-1.1 dBTP`) |

## Pipeline Files

- `shotlist.py` — 36-shot non-repeating `1080p` timeline validator (`validate_shotlist()`).
- `build_audio.py` — Trims & paces 8 `voice-00` beats, detects natural valley splits for `captions.srt` / `timings.json`, inserts the `0.60s` dramatic silence dropout, and normalizes the stereo master to `-14.0 LUFS`.
- `make_covers.py` — Composites the high-CTR, factually accurate `9:16` Shorts Cover (`1080×1920`) and `16:9` YouTube Thumbnail (`1920×1080`).
- `render_ultrahd.py` — Fast `uint16` ROI alpha-compositing 1:1 native-pixel `1080p60` renderer with live 8-beat progress rail, hardware telemetry header, keyword-highlighted subtitles, and crimson sabotage alert banner.
- `captions.srt` — Frame-accurate 16-card SRT subtitle file.
- `publishing-kit.txt` — Ready-to-publish YouTube Shorts titles, description, tags, pinned comment, and full script.
