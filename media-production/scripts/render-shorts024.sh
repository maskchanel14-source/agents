#!/usr/bin/env bash
# Render SHORTS-2026-024-Binance63B in this sandbox.
#
# The sandbox has no system Chrome and no ffmpeg, and Remotion cannot download
# its own headless browser, so we use the npm-shipped binaries:
#   chromium  — @sparticuz/chromium, unpacked by remotion-env.sh
#   ffmpeg    — @ffmpeg-installer/linux-x64
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export LD_LIBRARY_PATH="/tmp/al2023/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH="/home/user/agents/media-production/node_modules/@ffmpeg-installer/linux-x64:$PATH"
OUT="${OUT:-$ROOT/../projects/SHORTS-2026-024-Binance-63B/out/video-silent.mp4}"
exec npx remotion render src/index.ts SHORTS-2026-024-Binance63B "$OUT" \
  --codec=h264 --crf=18 --concurrency=1 \
  --browser-executable=/tmp/chromium --gl=swangle "$@"
