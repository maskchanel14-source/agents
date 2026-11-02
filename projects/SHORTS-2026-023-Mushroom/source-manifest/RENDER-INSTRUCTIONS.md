# Render instructions

```bash
cd media-production
npm ci
python3 scripts/generate_audio.py
./scripts/remotion-env.sh npx remotion render src/index.ts \
  SHORTS-2026-023-Mushroom \
  ../projects/SHORTS-2026-023-Mushroom/video.mp4 \
  --codec=h264 --crf=18 --concurrency=1 --timeout=120000
```

The helper resolves an NPM-installed FFmpeg and Chromium. It is necessary on the current minimal sandbox because system packages were not present. On a normal workstation with Chrome/FFmpeg already installed, `npx remotion render` can be used directly.

The project is 1080×1920 at 30 fps and currently runs for 1230 frames (41.0 seconds).

Before publishing, replace the low-resolution mirrored species still with the original binary from the linked Wikimedia Commons source if possible, preserve CC BY 4.0 attribution, and either add a legally cleared moving footage asset or keep the explicit `NOT FOOTAGE` truth label.
