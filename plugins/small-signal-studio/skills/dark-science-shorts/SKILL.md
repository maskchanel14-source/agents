---
name: dark-science-shorts
description: Produce Ultra-HD 1080p60 Dark Science and Frontier Technology YouTube Shorts for Small Signal Studio. Use this skill when creating a new SSS-00X episode, rendering native-1080p vertical science documentaries, designing honest-clickbait 9:16 and 16:9 covers, mastering -14.0 LUFS narration audio, archiving episodes to Google Drive, or applying voluntary Like and Subscribe conversion psychology.
---

# Dark Science Shorts (Small Signal Studio)

Produce broadcast-grade `1080x1920 @ 60fps` Dark Science, Frontier Technology, and Deep Physics YouTube Shorts from peer-reviewed primary sources and genuine `1080p` laboratory footage, while maintaining cross-session visual, sonic, and editorial consistency.

## Channel Identity & Standing Rules

- **Theme**: Dark Science, Unclassified Optics/Acoustics/Physics, Autonomous Robotics, and Frontier Engineering — eerie, counter-intuitive, 100% real peer-reviewed breakthroughs.
- **Language Split**: English spoken narration and on-screen typography; communicate with the creator in **Indonesian** unless asked otherwise.
- **Zero Fabrication**: Every number, institution, hardware spec, and failure limit must be verified against the paper or official code repository before scripting.
- **No Duplicate Topics**: Check Google Drive `Channel Log.txt` (`1tZFUr28z0ulej-fvrZD7DUxCkUFUAarC`) and `projects/SSS-*` before selecting a paper.
- **Canonical Reference Pipeline**: Treat `projects/SSS-003-Seeing-World-Through-Your-Eyes/` as the golden Cinema Engine v5 template.

## End-to-End 8-Step Episode Workflow

### 1. Bootstrap the Sandbox & Check Episode Log
On every fresh container boot, install headless OpenCV, Pillow, NumPy, PyYAML, and static `ffmpeg` (`v9.0.2`) before running any media script:

```bash
bash scripts/bootstrap_media_env.sh
```

Load the `google_drive` connector and inspect `Channel Log.txt` (`1tZFUr28z0ulej-fvrZD7DUxCkUFUAarC`) inside the `Small Signal Studio` root folder (`1yj4hdWZeKLbmAfMPh-mG10AEFQOvc3yY`) to determine the next `SSS-00X` ID and avoid previously covered papers. Full sandbox constraints and Drive IDs are documented in `references/sandbox-and-drive-ops.md`.

### 2. Scout a Primary Source With Native `1080p` GitHub Footage
Because `github.com`, `codeload.github.com`, and `api.github.com` are accessible (`raw.githubusercontent.com` is blocked), search GitHub Pages repositories (`*.github.io`) of top-tier venues (CVPR, SIGGRAPH, NeurIPS, CoRL, RSS, ICRA, USENIX Security, Nature/Science companions) and shallow-clone (`git clone --depth 1`) into `/tmp/scout_sss00X`.

**Hard Footage Gate**:
- Require **at least 12–30 distinct `1080p` MP4 clips** (`height == 1080`, e.g. `1920x1080` or `1080x1080`).
- Reject `360p`/`480p`/`568p` clips; upscaling low-resolution footage into a `1080p` frame causes visible blur.
- Archive active source footage under `.cache/library/footage/<slug>/` (never commit raw MP4s to Git) and inspect representative contact sheets before writing `shotlist.py`.

### 3. Write an 8-Beat Retention Script (`128–136` Words, Zero Verbal Begging)
Target **`55.0s–58.5s`** (`< 60.0s` Shorts ceiling; avoid the `30s–45s` dead zone):
1. **Beat 1 (`0–7s`, Hook)**: Immediate personal/physical stakes in `<= 10` words. Zero channel intro.
2. **Beat 2 (`7–16s`, Physics)**: Exact physical constant or geometry enabling the phenomenon.
3. **Beat 3 (`16–23s`, Lab & Model)**: Named university/lab + core computational architecture.
4. **Beat 4 (`23–31s`, Blockers)**: Two physical/mathematical blockers that stopped prior work.
5. **Beat 5 (`31–37s`, Breakthrough)**: How the algorithm solves both blockers cleanly.
6. **Beat 6 (`37–45s`, Proof + Honest Limit)**: Reconstructions plus **one honest failure boundary** (epistemic trust).
7. **Beat 7 (`45–49.5s`, Twist + `0.60s` Silence)**: Unexpected test leading into a **`0.60s` complete audio dropout** (`-inf dB`).
8. **Beat 8 (`49.5–58s`, Payoff + Loop)**: Reveal what emerged and end on an open bridge word (`"Remember..."`) completing on Beat 1.

Never speak *"Like and subscribe"* in narration. Apply `references/voluntary-conversion-playbook.md`.

### 4. Synthesize Narration (`voice-00`) & Master `-14.0 LUFS` Audio
- Synthesize Beats 1–8 via speech generation with `voice_id="voice-00"` (`1.032x` `atempo`, `48 kHz` mono -> stereo). If a container reset ever invalidates `voice-00`, follow the voice recovery procedure in `references/sandbox-and-drive-ops.md`.
- Score an original procedural Dark Science ambient bed (C#-minor sub-bass drone + subtle optical/sonar pulse, `-21 dB`, zero copyrighted samples -> `100%` Shorts revenue pool).
- Run two-pass `ebur128` + `loudnorm` mastering to hit **`-14.0 LUFS` integrated (`±0.2 LU`)** and **`<= -1.0 dBTP` true peak**, with complete digital silence across the `0.60s` cliffhanger window.

### 5. Generate & Inspect Honest-Clickbait Covers (`9:16` + `16:9`)
Generate dark photorealistic artwork (`offer_options=false` inside multi-asset episode builds), composite bold 2–4 word gold/white/crimson typography via `make_covers.py`, and inspect both `SSS-00X_Viral_Cover_9x16.jpg` (`1080x1920`, embedded at **Frame 0**) and `SSS-00X_Viral_Thumbnail_16x9.png` (`1920x1080`) before rendering.

### 6. Validate 34–36 Non-Repeating Shots & Render Cinema Engine v5
Follow `references/cinema-engine-v5-and-audio.md`:
- `validate_shotlist()` must enforce **zero scene/interval overlap**, `height == 1080` on every source clip, `0.95s–2.30s` cut pacing, and **physical motion continuity** between Shot `N` (pull-back) and Shot `1` (zoom-in).
- Place widescreen `1920x1080` clips inside the **`1036x583` supersampled stage** (`1.85x` native pixel density) and `1080x1080` clips inside the **`1036x720` stage** (`1.04x` native density) — never center-crop `9:16` from `16:9` and never run `minterpolate`.
- Fade in the silent **Peak-End Voluntary Dossier Toast** (`ARCHIVE #00X • LIKE TO SAVE PAPER • + SUBSCRIBE FOR #00(X+1)`) for `~4.5s` right after the `0.60s` silence reveal.

### 7. Forensic Pixel & Loudness Verification Gate
Before claiming completion:
1. Run `ffmpeg -filter_complex ebur128=peak=true` on the MP4 and confirm **`-14.0 LUFS`** (`±0.2`) and **`<= -1.0 dBTP`**.
2. Extract and visually inspect **5+ full-size `1080x1920` frames** from the encoded MP4 (hook, 3D stage, square stage, silence banner, and Peak-End toast).

### 8. Deliver to Google Drive, Prune Snapshot Size, & Sync Git
1. Create subfolder `SSS-00X — <Title>` inside `1yj4hdWZeKLbmAfMPh-mG10AEFQOvc3yY` and upload all 6 deliverables: `1080p60` MP4, `9:16` JPG, `16:9` PNG, VO MP3, `captions.srt`, and `publishing-kit.txt`.
2. Append `[SSS-00X]` to `Channel Log.txt` (`1tZFUr28z0ulej-fvrZD7DUxCkUFUAarC`).
3. Delete `/tmp/sss*`, `.cache/library/footage/*`, and older local MP4s already backed up on Drive so `/home/user` stays `< 128 MB`.
4. Commit `projects/SSS-00X-*/` to Git and present the finished MP4.

## Reference Manuals

- [`references/cinema-engine-v5-and-audio.md`](references/cinema-engine-v5-and-audio.md) — Exact pixel geometry, HUD coordinates, streaming decoder, encoding flags, and `-14.0 LUFS` audio chain.
- [`references/sandbox-and-drive-ops.md`](references/sandbox-and-drive-ops.md) — Container reset bootstrap, network whitelist, `voice-00` continuity, Google Drive IDs, and `<128 MB` workspace rules.
- [`references/voluntary-conversion-playbook.md`](references/voluntary-conversion-playbook.md) — Behavioral psychology and YouTube Shorts retention mechanics that make viewers voluntarily Like and Subscribe.
