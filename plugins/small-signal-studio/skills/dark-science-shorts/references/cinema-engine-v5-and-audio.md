# Cinema Engine v5 & Audio Mastering Specification

Exact pixel, color, motion, and loudness specification used across `SSS-001` v3, `SSS-002` v4, and `SSS-003` v5 (`projects/SSS-003-Seeing-World-Through-Your-Eyes/render_ultrahd.py`).

## 1. Why Cinema Engine v5 Looks Razor-Sharp on Mobile

Most vertical science channels ruin research footage in one of three ways:
1. **Center-cropping `9:16` (`607x1080`) out of `1920x1080` video and upscaling `1.78x`** — throws away `68%` of horizontal context and blurs fine details.
2. **Upscaling `360p`/`480p` web previews** — creates muddy macroblocks.
3. **Running `ffmpeg minterpolate` optical-flow 60fps conversion** — warps edges into jelly artifacts whenever cameras pan rapidly.

**Cinema Engine v5 eliminates all three failure modes**:
- **100% Native `1080p` Height Gate**: Every clip in `SHOTS` is verified by `validate_shotlist()` to have `height == 1080`.
- **1:1+ Supersampled Documentary Stage (`STAGE_W = 1036`, `STAGE_X = 22`)**:
  - `1920x1080` widescreen clips downsample with `cv2.INTER_AREA` into **`1036x583`** (`1.85x` native pixel density — supersampled, never upscaled), with a smooth `0% -> 4.0%` push-in computed directly on the full `1920x1080` source buffer before downsampling.
  - `1080x1080` square macro/ablation clips crop `1080x750` and downsample into **`1036x720`** (`1.04x` native pixel density).
- **Subtle Fine-Radius Luma Polish Only**: `unsharp_luma(stage_bgr, sigma=0.88, amount=0.25)` in `YCrCb` luma space. Never apply heavy `CLAHE` (`clipLimit >= 2.0`), which amplifies H.264 chroma blocks in dark lab shadows.

## 2. Exact `1080 x 1920` Vertical Layout Coordinates (Safe From YouTube Shorts UI)

| Y Coordinate Band | Layer | Purpose & Styling |
| :--- | :--- | :--- |
| `0 .. 1920` | Obsidian Studio Canvas | Deep vignette (`#060910`) blended with `14%` live `15x15` Gaussian ambient glow sampled from the active stage frame |
| `118 .. 162` | Brand Archive Pill | `SMALL SIGNAL STUDIO • DARK SCIENCE ARCHIVE #00X` (`DejaVuSansMono-Bold` 21px, brushed-gold `2px` border, status LED dot) |
| `182 .. 240` | Bold Beat Header | 2–4 word uppercase chapter headline (`DejaVuSans-Bold` 49px: gold `#FFD844` on hooks/payoffs, crimson `#FF6B6B` on blockers/alerts, white `#F8FAFC` on exposition) |
| `258 .. 266` | 8-Beat Progress Rail | `760px` segmented progress bar showing the viewer's exact position in the 8-beat investigation |
| `stage_y - 44 .. stage_y` | Telemetry Strip | `SHOT XX/36 • 1080P NATIVE` on left + real physical/optical telemetry tag on right |
| `stage_y .. stage_y + stage_h` | Cinema Stage | `1036x583` (`16:9`) or `1036x720` (`4:3`) framed by a `2px` gold/crimson bezel and `22px` corner L-ticks |
| `1218 .. 1414` | Synced Subtitle Card | Rounded dark-glass card (`x=40..1040`) with 2-line captions (`39px`), cyan/gold keyword highlights, and active speech progress bar (switches to crimson `[ ARCHIVAL ... SCAN ]` banner during the `0.60s` silence window) |
| `1442 .. 1496` | Peak-End Dossier Toast | Appears **only** for `~4.5s` right after the `0.60s` silence reveal (`t=50.1s..54.8s`): `ARCHIVE #00X • LIKE TO SAVE PAPER • + SUBSCRIBE FOR #00(X+1)` (`0.35s` smooth alpha fade in/out) |
| `1512 .. 1540` | Primary Source Citation | `SOURCE: <AUTHORS>, <VENUE> • ARXIV:<ID>` safely above YouTube's bottom title/handle overlay (`y > 1580`) |

## 3. Fast Streaming Render Architecture (`~54 ms/frame`, Zero OOM)

- **`StreamShotDecoder`**: Opens only the active clip, seeks once to `src_t0`, and steps forward sequentially (`cur_frame`), keeping peak memory at **2 decoded frames** instead of preloading gigabytes of raw arrays.
- **`uint16` ROI Strip Alpha Blending (`blend_roi_inplace`)**: Pre-crops HUD elements (`top`, `stage`, `cit`), subtitle cards (`cap_cache`), and the Peak-End toast into narrow horizontal RGBA strips converted to `uint16`, blending only non-empty rows in-place.
- **Subprocess Pipe Safety**: Redirect `ffmpeg` `stderr` to a file (`/tmp/sss00X_build/ffmpeg_render.log`) rather than an unread `subprocess.PIPE` buffer so `ffmpeg` never deadlocks on warnings.
- **Canonical H.264 High@L4.2 Encoding Flags**:
  ```text
  -c:v libx264 -preset fast -profile:v high -level:v 4.2 -threads 4
  -pix_fmt yuv420p -crf 17 -maxrate 13M -bufsize 26M -g 60 -bf 2
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest
  ```

## 4. `-14.0 LUFS` EBU R128 Audio & `captions.srt` Pipeline (`build_audio.py`)

1. **Trim & Pace Beats**: Trim leading/trailing TTS silence (`-42 dB`) from `b1.wav`–`b8.wav`, resample to `48 kHz`, and apply `atempo=1.032` for brisk documentary authority without pitch distortion.
2. **Pause-Valley Subtitle Split**: Split each beat into 2-card (`<= 42` chars/line, max 2 lines) chunks by locating the lowest RMS energy valley between `36%` and `64%` of the beat duration so subtitle transitions land on natural breath/phrase boundaries.
3. **Dramatic `0.60s` Silence Cliffhanger**: Between Beat 7 and Beat 8 (`~85%` mark), insert a `0.64s` gap and zero **both** voice and music across the inner `0.600s` (`0.02s` cosine fade-out/in to prevent clicks), preceded by a `62 Hz` sub-drop thud (`0.42s`) at the start of Beat 8.
4. **Two-Pass EBU R128 Loudness Normalization**: Measure `raw_mix.wav` via `ebur128=peak=true`, then run `loudnorm=I=-14.0:TP=-1.2:LRA=7:linear=true` with exact measured `I`, `TP`, `LRA`, and `thresh` values so the final muxed MP4 measures **`-14.0 LUFS`** (`±0.1 LU`).
