# Sandbox Bootstrap, Network Whitelist, Voice Continuity & Google Drive Operations

Operational guide ensuring **100% identical episode output** when switching sessions or recovering from a fresh container reset.

## 1. Fresh Container Reset Behavior & One-Command Bootstrap

In Arena's sandboxed Git environment:
- Only files inside `/home/user/agents` (excluding `.arena`, `.cache`, `.local`, `.venv`, `__pycache__`, `build`, `dist`, `node_modules`) persist across turns/snapshots.
- System packages in `/usr/local` or `/usr/bin` (`ffmpeg`, `cv2`, `pyyaml`) reset on a brand-new container session, and Debian PEP 668 blocks bare `pip install`.
- **Always run at the start of a media session**:
  ```bash
  bash scripts/bootstrap_media_env.sh
  ```
- In every Python script (`build_audio.py`, `render_ultrahd.py`), resolve `ffmpeg` dynamically rather than assuming `/usr/bin/ffmpeg`:
  ```python
  def get_ffmpeg() -> str:
      import shutil
      exe = shutil.which("ffmpeg")
      if exe:
          return exe
      import imageio_ffmpeg
      return imageio_ffmpeg.get_ffmpeg_exe()
  ```

## 2. Outbound Network Whitelist & Footage Acquisition

Outbound access is restricted to:
- `github.com`, `codeload.github.com`, `api.github.com`
- `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org`

**Important**: `raw.githubusercontent.com` and external university hosts are blocked for direct `curl` downloads, **but** any academic project hosted on GitHub Pages (`https://<project>.github.io` backed by `github.com/<org>/<project>.github.io`) can be cloned at full native `1080p` quality via:
```bash
git clone --depth 1 https://github.com/<org>/<repo>.git /tmp/scout_sss00X
```
Use the `gh` CLI (`gh api "search/repositories?q=..."`) to discover peer-reviewed CVPR / SIGGRAPH / NeurIPS / RSS / CoRL / USENIX project pages with embedded `1080p` MP4 demonstrations.

## 3. Channel Voice Continuity (`voice-00`)

Small Signal Studio uses a locked English masculine documentary narrator (`voice-00`).
1. Within an active or resumed session, test synthesizing Beat 1 directly with `voice_id="voice-00"`.
2. If a brand-new session reports that `voice-00` is unregistered, download `/Small Signal Studio/Chosen_Voice_Sample_voice-00.mp3` (`1UB6d57dDlRZVVeFjTor2lZOwjzm4M1Vh`) or inspect `Voice.txt` (`1oq-tK0E_0PPcIp3r6MUYhrL87pcuiH50`) on Google Drive, then register the narrator once via `add_voice(language="en", voice_identity={"gender": "masculine", "use_case": "narration"}, text=...)` using Beat 1 + Beat 2 of the new episode script so the user confirms the locked studio tone in one click.

## 4. Canonical Google Drive Folder & File Inventory

Load the `google_drive` connector in any turn that reads or uploads Drive files (`list_connector_tools` applies per turn).

| Asset | Google Drive ID | Purpose |
| :--- | :--- | :--- |
| **`Small Signal Studio` (Root Folder)** | `1yj4hdWZeKLbmAfMPh-mG10AEFQOvc3yY` | Root production archive for all episodes and studio metadata |
| **`Channel Log.txt`** | `1tZFUr28z0ulej-fvrZD7DUxCkUFUAarC` | Canonical ledger of all published episodes (`[SSS-001]`, `[SSS-002]`, `[SSS-003]`, ...), specs, Drive links, and lessons learned |
| **`Voice.txt`** | `1oq-tK0E_0PPcIp3r6MUYhrL87pcuiH50` | Locked voice identity specification (`voice-00`) |
| **`Chosen_Voice_Sample_voice-00.mp3`** | `1UB6d57dDlRZVVeFjTor2lZOwjzm4M1Vh` | Reference audio sample of `voice-00` |
| **`SSS-001` Folder** | `1ujnjm9ZNKMxzWqzduV1BwPiVubl1SYdA` | Episode #001 (*Ghost Walls Robot Parkour*, `arXiv:2309.05665`) |
| **`SSS-002` Folder** | `1hREP_F8isJhgi_Z8Iwre47PYU4fqk7KU` | Episode #002 (*Universal Manipulation Interface*, `arXiv:2402.10329`) |
| **`SSS-003` Folder** | `1MTSP46ZVgajSfBpi4i2KQcTlENd66FGl` | Episode #003 (*Seeing the World Through Your Eyes*, `arXiv:2306.09348`) |

Every `SSS-00X` Drive subfolder must contain all **6 standard deliverables**:
1. `SSS-00X_<Slug>_UltraHD_1080p60.mp4`
2. `SSS-00X_Viral_Cover_9x16.jpg`
3. `SSS-00X_Viral_Thumbnail_16x9.png`
4. `SSS-00X_Voiceover_Only.mp3`
5. `captions.srt`
6. `publishing-kit.txt`

## 5. Turn-End Snapshot Cap (`< 128 MB`)

Workspace turn-end snapshots across `/home/user` are capped around **`128 MB`**.
- Keep raw cloned footage inside `/tmp/` or `.cache/library/footage/` and delete it once rendering + QC pass.
- Once older `SSS-00X` MP4 masters are verified on Google Drive, remove their local `/home/user/deliverables/SSS-00X/*.mp4` copies if cumulative deliverables approach `90 MB`, keeping the active episode's deliverables local so `present_file` can open them directly.
