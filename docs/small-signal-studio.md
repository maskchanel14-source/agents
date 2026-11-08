# Small Signal Studio — Cross-Session Production & Voluntary Conversion Handbook

Canonical engineering and editorial SOP for **Small Signal Studio** (`Dark Science • Frontier Technology • Deep Physics`). Any AI agent starting a fresh session in this repository can reproduce exact **Cinema Engine v5** broadcast quality by following this document and the [`small-signal-studio`](../plugins/small-signal-studio/README.md) plugin.

---

## 1. Fast Session Startup Checklist (Run First in Every New Session)

1. **Bootstrap Media & Validation Toolchain** (required after container resets):
   ```bash
   bash scripts/bootstrap_media_env.sh
   ```
   Installs `opencv-python-headless`, `Pillow`, `numpy`, `imageio-ffmpeg` (static `ffmpeg v9.0.2` symlinked to `~/.bin/ffmpeg`), and `pyyaml`.
2. **Load Google Drive & Inspect `Channel Log.txt`**:
   - Root Folder (`Small Signal Studio`): `1yj4hdWZeKLbmAfMPh-mG10AEFQOvc3yY`
   - `Channel Log.txt`: `1tZFUr28z0ulej-fvrZD7DUxCkUFUAarC` (check completed `SSS-001`, `SSS-002`, `SSS-003`, ... to assign the next `SSS-00X` ID and prevent duplicate topics)
   - `Voice.txt`: `1oq-tK0E_0PPcIp3r6MUYhrL87pcuiH50` | Sample MP3: `1UB6d57dDlRZVVeFjTor2lZOwjzm4M1Vh` (`voice_id="voice-00"`)
3. **Copy From the Golden Cinema Engine v5 Reference Pipeline**:
   - [`projects/SSS-003-Seeing-World-Through-Your-Eyes/`](../projects/SSS-003-Seeing-World-Through-Your-Eyes/) (`shotlist.py`, `build_audio.py`, `make_covers.py`, `render_ultrahd.py`, `publishing-kit.txt`)

---

## 2. Complete Toolchain & Architecture Matrix

| Stage | Tool / Script | Non-Negotiable Standard |
| :--- | :--- | :--- |
| **Paper & Footage Scouting** | `gh api` + `git clone --depth 1` | Peer-reviewed venue (CVPR, SIGGRAPH, NeurIPS, RSS, CoRL, USENIX) hosted on `github.com` (`raw.githubusercontent.com` is blocked). Minimum **12–30 native `1080p` MP4s** (`height == 1080`). |
| **Voiceover Synthesis** | `generate_speech` (`voice-00`) | English documentary narration (`128–136` words across 8 beats, `atempo=1.032`, `48 kHz`), **zero verbal begging**. |
| **Audio Mastering** | `build_audio.py` (`ffmpeg` + NumPy) | Custom procedural Dark Science drone (`-21 dB`, `100%` Shorts revenue share), `0.60s` complete silence cliffhanger before Beat 8, two-pass EBU R128 **`-14.0 LUFS`** (`<= -1.0 dBTP`). |
| **Viral Covers** | `generate_image` + `make_covers.py` | Honest-clickbait Dark Science `9:16` Shorts Cover (`1080x1920`, embedded at **Frame 0**) + `16:9` YouTube Thumbnail (`1920x1080`), visually verified at 1:1 resolution. |
| **Shotlist Validation** | `shotlist.py` (`validate_shotlist()`) | **34–36 strictly non-repeating `1080p` cuts** (`0` interval overlaps, `0.95s–2.30s` per shot), physical zoom continuity from final shot back into Shot 1. |
| **Cinema Engine v5 Render** | `render_ultrahd.py` (OpenCV + Pillow + `libx264`) | `1080x1920 @ 60.00fps`, `High@L4.2`, `CRF 17`, `+faststart`, 1:1+ supersampled stage (`1036x583` widescreen / `1036x720` square), zero `minterpolate`, silent Peak-End Voluntary Dossier Toast (`t=50.1s..54.8s`). |
| **Forensic QC & Delivery** | `read_file` + `google_drive` | Inspect 5+ full-size `1080x1920` encoded frames + `ebur128` output, upload all 6 deliverables to Drive, update `Channel Log.txt`, keep `/home/user` `< 128 MB`. |

---

## 3. Summary of Voluntary Like & Subscribe Mechanics

Full behavioral citations and benchmarks live in [`voluntary-conversion-playbook.md`](../plugins/small-signal-studio/skills/dark-science-shorts/references/voluntary-conversion-playbook.md):

1. **Zero Verbal Begging**: Never interrupt the story or kill the replay loop with spoken *"Don't forget to like and subscribe."*
2. **Peak-End Silent Dossier Toast (`+380%` Lift)**: Fade in `ARCHIVE #00X • LIKE TO SAVE PAPER • + SUBSCRIBE FOR #00(X+1)` for `4.5s` right after the `0.60s` silence twist (`~85%` mark) when viewer awe peaks.
3. **Selfish Bookmark Utility**: Frame **Like** as a personal tool to save the cited `arXiv` paper into the viewer's `Liked videos`.
4. **Serialized Archive Identity (`+150%` Lift)**: Number every Short (`DARK SCIENCE ARCHIVE #001, #002, #003...`) to spark channel-page bingeing and `#00(X+1)` anticipation.
5. **Epistemic Honesty**: Always state one real scientific boundary/failure condition so skeptical tech viewers trust the channel immediately.
6. **Infinite Loop + Zeigarnik Pinned Comment**: Pair physical+syntactic `"Remember..."` loop continuity (`>100%` APV) with a Pinned Comment sharing one bonus code/paper insight + a personal question.
