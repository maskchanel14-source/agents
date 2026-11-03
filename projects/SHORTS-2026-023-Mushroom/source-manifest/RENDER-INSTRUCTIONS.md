# Render instructions — footage rebuild

The source archive includes the three 1080p/HD video proxies required by the composition. They must remain under:

```text
media-production/public/shorts023/footage/
```

Expected filenames:

```text
mushroom-growth-timelapse-1080p.mp4
fungus-moss-log-macro-1080p.mp4
mushroom-moss-macro-hd.mp4
```

Render:

```bash
cd media-production
npm ci
python3 scripts/generate_audio.py
./scripts/remotion-env.sh npx remotion render src/index.ts \
  SHORTS-2026-023-Mushroom \
  ../projects/SHORTS-2026-023-Mushroom/video.mp4 \
  --codec=h264 --crf=18 --concurrency=1
```

The helper resolves an NPM-installed FFmpeg and Chromium. It is necessary on the current minimal sandbox because system packages are not present. On a normal workstation with Chrome/FFmpeg already installed, `npx remotion render` can be used directly.

The composition is 1080×1920 at 30 fps for 1230 frames (41.0 seconds). The footage was deliberately converted to 1080p proxies before rendering: the original 4K sources are retained in the user’s `footage yt` Drive folder, while the archive stays small enough to upload and reproduce the final edit.

Do not remove the `GENERIC MUSHROOM FOOTAGE` disclosure or use the clips to identify a species. The background clips are contextual footage, not *Lanmaoa asiatica* records.
