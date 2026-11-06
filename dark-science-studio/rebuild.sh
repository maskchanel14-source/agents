#!/usr/bin/env bash
# Full rebuild of everything non-git after a sandbox reset.
# Everything installable from pypi/npm/github works. apt is NOT reachable
# (deb.debian.org blocked), so ffmpeg/sox/fluidsynth are replaced by:
#   ffmpeg  -> imageio-ffmpeg static build (pypi)
#   sox     -> ffmpeg filters
#   fluidsynth -> spessasynth_core (npm, already the studio's MIDI renderer)
set -euo pipefail
cd "$(dirname "$0")"

echo "== python venv =="
[ -d .venv ] || python3 -m venv .venv
./.venv/bin/pip -q install --upgrade pip
./.venv/bin/pip -q install imageio-ffmpeg numpy scipy soundfile brotli \
  piper-tts pretty_midi mido pillow pyloudnorm requests

echo "== node: remotion studio =="
cd tools/studio
[ -d node_modules ] || npm i --no-audit --no-fund
cd ../..

echo "== headless chromium =="
mkdir -p .bin
cd .bin
[ -d node_modules ] || npm i @sparticuz/chromium --no-audit --no-fund
cd ..
[ -x .chromium/chromium ] || ./.venv/bin/python tools/setup_chromium.py

echo "== assets: piper voice + soundfont =="
bash tools/fetch_assets.sh

echo "== done =="
ls -la .models assets .chromium 2>/dev/null | head -20
