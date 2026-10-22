# Indonesian faceless YouTube renderer

Reusable, local-first renderer for the Ruang Nalar production pack. It is intentionally conservative: no cloud image API, no voice clone, no stock footage, no public upload, and no dependency on Google/Hugging Face.

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install -r workflows/indonesian-faceless-youtube/requirements.txt
.venv/bin/python workflows/indonesian-faceless-youtube/render.py \
  --production "output/YouTube Channel - Ruang Nalar/01_Video/2026-10-22_harga-ayam-rantai-pasok"
```

The renderer expects `02_Naskah/scenes.json`, writes audio/visual/final files into the production folder, and updates timing-sensitive Markdown artifacts. Use `--skip-shorts` only for a diagnostic render; the normal run always creates the main MP4, three vertical Shorts, SRT, PNG thumbnail, and QA report.

## Design notes

- TTS is eSpeak NG Bahasa Indonesia through its local C callback. The generated voice is deliberately marked **suara sementara**.
- SVG stills are programmatic editorial illustrations; they never pretend to be news photos or depict identifiable real people.
- FFmpeg is resolved from `imageio_ffmpeg.get_ffmpeg_exe()` or PATH. The static binary is not copied into the deliverable.
- Audio timing is forced from the actual WAV files, not guessed from word count.
- The script does not read credentials, create accounts, change sharing, upload to YouTube, or overwrite Drive files.
