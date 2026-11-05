#!/usr/bin/env bash
# Extract the 13 revision-3 delivery stills from the finished master.
#
#   bash scripts/stills-shorts024-rev3.sh
#
# Frame numbers follow the VO (audio/timing3.json -> src/data/shorts024Timeline.ts)
# and the scene/host schedule in src/scenes2d.tsx, so each still lands on one
# spoken beat. Re-derive them if the VO is ever re-cut.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STUDIO="$(cd "$HERE/.." && pwd)"
PROJ="$(cd "$STUDIO/../projects/SHORTS-2026-024-Binance-63B" && pwd)"
FF="$(node -e "console.log(require('$STUDIO/node_modules/@ffmpeg-installer/ffmpeg').path)")"

# beat                                                     frame
FRAMES="90 250 420 560 780 940 1090 1250 1440 1620 1790 1910 2070"
NAMES=(hook-host exchange hotwallet-host clock bitcoin frozen vault-intact-host \
       interview laptop-host reopen dossier chart close-host)

cd "$PROJ"
rm -rf stills
mkdir -p stills

i=0
for f in $FRAMES; do
  n="${NAMES[$i]}"
  printf -v idx "%02d" $((i + 1))
  "$FF" -y -loglevel error -i out/final.mp4 \
    -vf "select=eq(n\\,${f})" -vframes 1 "stills/${idx}_${n}_f${f}.png"
  echo "  stills/${idx}_${n}_f${f}.png"
  i=$((i + 1))
done
ls -la stills
