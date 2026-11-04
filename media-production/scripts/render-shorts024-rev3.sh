#!/usr/bin/env bash
# Render SHORTS-2026-024-Binance63B revision 3 (2D editorial explainer + host).
#
# 2D needs no GPU: ~0.55 s/frame on software GL, so the whole 2055-frame film
# takes ~19 minutes. Same npm-provided chromium + ffmpeg trick as the rev-2
# script (the sandbox has no system Chrome).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export LD_LIBRARY_PATH="/tmp/al2023/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH="/home/user/agents/media-production/node_modules/@ffmpeg-installer/linux-x64:$PATH"
OUT="${OUT:-$ROOT/../projects/SHORTS-2026-024-Binance-63B/out/video-silent-rev3.mp4}"
exec npx remotion render src/index.ts SHORTS-2026-024-Binance63B "$OUT" \
  --codec=h264 --crf=18 --concurrency=1 \
  --browser-executable=/tmp/chromium --gl=swangle "$@"
