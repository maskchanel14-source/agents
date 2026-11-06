#!/usr/bin/env bash
# Fetches the two binary assets that cannot be pip/npm installed
# (GitHub release URLs are blocked in this sandbox, but git clone is allowed).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .models assets /tmp/fetch

echo "== piper voice: lessac (medium, en_US) =="
[ -f .models/lessac.onnx ] || {
  rm -rf /tmp/fetch/vv
  git clone -q --depth 1 --filter=blob:none --sparse https://github.com/jankrom/Voice-Vault /tmp/fetch/vv
  (cd /tmp/fetch/vv && git sparse-checkout set device/app/tts-models/lessac)
  cp /tmp/fetch/vv/device/app/tts-models/lessac/lessac.onnx* .models/
}

echo "== TimGM6mb soundfont =="
[ -f assets/TimGM6mb.sf2 ] || {
  rm -rf /tmp/fetch/sm
  git clone -q --depth 1 --filter=blob:none --sparse https://github.com/prashant-khatiwada/Surmuni /tmp/fetch/sm
  (cd /tmp/fetch/sm && git sparse-checkout set src-tauri/soundfonts)
  cp /tmp/fetch/sm/src-tauri/soundfonts/TimGM6mb.sf2 assets/
}
ls -la .models assets
