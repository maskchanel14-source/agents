# SSS-001 — How "Ghost Walls" Taught a 1-Camera Robot Parkour

Production package for **Small Signal Studio — Episode #001 (`SSS-001`)**, a `58.067s` Ultra-HD (`1080×1920 @ 60fps`) documentary YouTube Short covering Stanford, Carnegie Mellon, ShanghaiTech, and Shanghai Qi Zhi Institute's autonomous quadruped parkour research (*Robot Parkour Learning*, CoRL 2023 Oral — Best Systems Paper Finalist), supplemented with companion single-camera Unitree A1 field experiments from CMU and UC Berkeley so **zero video clips ever repeat across all 35 cuts**.

## Google Drive Delivery Links

- **Episode Folder (`SSS-001`)**: <https://drive.google.com/drive/folders/1ujnjm9ZNKMxzWqzduV1BwPiVubl1SYdA>
- **Ultra-HD 1080p60 Master (`SSS-001_Ghost_Walls_Robot_Parkour_UltraHD_1080p60.mp4`, 93.35 MiB)**: <https://drive.google.com/file/d/1GTx2b5eeyoPb6vbrfLX35tXszi-AkyKe/view?usp=drivesdk>
- **9:16 Viral Shorts Cover (`SSS-001_Viral_Cover_9x16.jpg`, also embedded at Frame 0 `0:00.00`)**: <https://drive.google.com/file/d/1ScdbjLPCcUWbjkZsmTiq87KOAl4VKryx/view?usp=drivesdk>
- **16:9 YouTube Studio Thumbnail (`SSS-001_Viral_Thumbnail_16x9.png`)**: <https://drive.google.com/file/d/1GG__JbiTl75j8SWz8x05QPskTOnTcROu/view?usp=drivesdk>
- **Standalone Voiceover (`SSS-001_Voiceover_Only.mp3`, `voice-00`)**: <https://drive.google.com/file/d/1EuuJEeNOUGL1JFOd1uBVw0OyMDK2mF16/view?usp=drivesdk>
- **Publishing Kit (`publishing-kit.txt`)**: <https://drive.google.com/file/d/1tddiqwH_Mz6q-sbif319Jnc2xnrDr44i/view?usp=drivesdk>
- **Synced Captions (`captions.srt`)**: <https://drive.google.com/file/d/1E5J7MH1zivd-mXSdiJCYkT2vO8bdYHrs/view?usp=drivesdk>

## Verified Master Specifications

| Metric | Target | Verified Measurement |
| :--- | :--- | :--- |
| Resolution & Aspect | `1080×1920` (`9:16`) | `1080×1920` (`9:16`) |
| Frame Rate & Count | `60 fps` | `60/1 fps` (`3,484` frames: Frame 0 cover + 35 motion shots) |
| Runtime | `< 60.0 s` | `58.067 s` |
| Video Codec & Bitrate | H.264 High@L4.2 Ultra-HD | `13.22 Mbps` video / `13.49 Mbps` total (`97,896,003` bytes) |
| Footage Diversity | Zero repeated clips | **35 shots = 35 distinct source video files (`0%` clip reuse)** |
| Max Single-Clip Share | `<= 20%` | `8.4%` (`4.88s` unbroken stone-wall retry proof take) |
| Audio Format | `48 kHz` Stereo AAC | `48,000 Hz` Stereo AAC LC @ `256 kbps` |
| Integrated Loudness | `-14.0 LUFS` (±1 LU) | `-14.0 LUFS` |
| Loudness Range (LRA) | `> 5.0 LU` | `10.9 LU` |
| True Peak | `<= -1.0 dBTP` | `-1.3 dBTP` |

## Package Contents

- `shotlist.py` — Frame-exact 35-shot zero-repetition manifest (`frames 1..3484`) with automated uniqueness and contiguity assertions.
- `render_ultrahd.py` — Reproducible Ultra-HD optical-clarity renderer (8×8-tap `Lanczos-4` upscaling, CIE `LAB` luminance-only `CLAHE` micro-contrast, luminance unsharp mask, Montserrat Black `#FFFFFF` / `#C9A25B` caption compositor, and x264 `-tune film` pipe).
- `captions.srt` — 21-cue SRT subtitle file synced to the `voice-00` narration.
- `cover-9x16.jpg` — `1080×1920` vertical Shorts cover (embedded on Frame 0 for YouTube Mobile's frame-picker).
- `PUBLISH-KIT.md` — Copy-paste titles, description, hashtags, tags, pinned comment, and disclosure settings.
- `QC-REPORT.md` — Full stream, loudness, and 35-shot source provenance audit.

## Reproducing Locally

1. Clone the three open-access academic footage repositories into `.cache/library/footage/{robot_parkour,extreme_parkour,vision_locomotion}` (see `QC-REPORT.md` for repository URLs).
2. Place `SSS-001_Voiceover_Only.mp3` / `master_audio.wav` from the Episode Google Drive folder into `/tmp/prod_v2/master_audio.wav`.
3. Validate the zero-repetition shot manifest and render:

```bash
python3 projects/SSS-001-Ghost-Walls-Robot-Parkour/shotlist.py
python3 projects/SSS-001-Ghost-Walls-Robot-Parkour/render_ultrahd.py
```
