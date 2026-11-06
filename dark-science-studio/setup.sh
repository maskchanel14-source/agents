#!/usr/bin/env bash
# Rebuilds the local (non-git) parts of the Dark Science studio.
# Everything tracked in git (tools/, src/, projects/) lives in the repo and survives resets.
set -euo pipefail
cd "$(dirname "$0")"
echo "== python venv =="
[ -d .venv ] || python3 -m venv .venv
./.venv/bin/pip -q install --upgrade pip
./.venv/bin/pip -q install imageio-ffmpeg numpy scipy soundfile brotli piper-tts pretty_midi mido pillow

echo "== node deps (remotion + fonts + spessasynth) =="
cd tools/studio && npm i --no-audit --no-fund && cd ../..

echo "== headless chromium (@sparticuz) =="
mkdir -p .bin && cd .bin
[ -d node_modules ] || npm i @sparticuz/chromium --no-audit --no-fund
cd ..
if [ ! -x .chromium/chromium ]; then
  mkdir -p .chromium
  node -e "
    import('@sparticuz/chromium').then(async m=>{const p=await m.default.executablePath();console.log(p)})" >/dev/null 2>&1 || true
fi

echo "== assets (voice model + soundfont) =="
mkdir -p .models assets
if [ ! -f .models/lessac.onnx ]; then
  echo "  .models/lessac.onnx missing — fetch with tools/fetch_assets.sh"
fi
if [ ! -f assets/TimGM6mb.sf2 ]; then
  echo "  assets/TimGM6mb.sf2 missing — fetch with tools/fetch_assets.sh"
fi
echo "done."
