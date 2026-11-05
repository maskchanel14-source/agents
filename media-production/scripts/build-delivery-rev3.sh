#!/usr/bin/env bash
# Build the delivery bundle for SHORTS-2026-024-Binance-63B.
# Revision 4: same 2145-frame edit as revision 3, with the host rebuilt on
# DiceBear Notionists (CC0 1.0). Audio, illustrations and script are unchanged.
#
#   bash scripts/build-delivery-rev3.sh
#
# Writes projects/SHORTS-2026-024-Binance-63B/delivery/ (gitignored) with the
# same numbered layout as revisions 1 and 2.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STUDIO="$(cd "$HERE/.." && pwd)"
PROJ="$(cd "$STUDIO/../projects/SHORTS-2026-024-Binance-63B" && pwd)"
FF="$(node -e "console.log(require('$STUDIO/node_modules/@ffmpeg-installer/ffmpeg').path)")"

COVER_FRAME=60
SMALL_FRAME=92

cd "$PROJ"
rm -rf delivery
mkdir -p delivery

echo "[1/6] master + cover"
cp out/final.mp4 delivery/01_VIDEO.mp4
"$FF" -y -loglevel error -i out/final.mp4 -vf "select=eq(n\,${COVER_FRAME})" -vframes 1 delivery/02_COVER.png
"$FF" -y -loglevel error -i out/final.mp4 -vf "select=eq(n\,${SMALL_FRAME}),scale=540:960" -vframes 1 delivery/cover-small.png

echo "[2/6] audio"
cp audio/final3.wav delivery/03_AUDIO-MIX-14LUFS.wav

echo "[3/6] docs"
cp PUBLISH-KIT.md QC-REPORT.md REVISION-2.md REVISION-3.md REVISION-4.md README.txt delivery/

echo "[4/6] stills + QA reports"
(cd stills && zip -q -r ../delivery/04_STILLS.zip .)
(cd references/reports && zip -q -r ../../delivery/05_QA-REPORTS.zip .)

echo "[5/6] source archive"
STAGE="$(mktemp -d)"
mkdir -p "$STAGE/archive"
cp facts.json script.txt script-rev3.txt STYLE_BIBLE.md README.md \
   REVISION-2.md REVISION-3.md REVISION-4.md QC-REPORT.md PUBLISH-KIT.md "$STAGE/archive/"
cp audio/timing3.json "$STAGE/archive/timing3.json"
mkdir -p "$STAGE/archive/media-production"
cp -r "$STUDIO/src" "$STAGE/archive/media-production/src"
cp -r "$STUDIO/scripts" "$STAGE/archive/media-production/scripts"
rm -rf "$STAGE/archive/media-production/scripts/node_modules"
mkdir -p "$STAGE/archive/public/shorts024"
cp -r "$STUDIO/public/shorts024/scenes" "$STAGE/archive/public/shorts024/scenes"
(cd "$STAGE/archive" && zip -q -r "$PROJ/delivery/06_SOURCE-ARCHIVE.zip" .)
rm -rf "$STAGE"

echo "[6/6] checksums"
(cd delivery && sha256sum * | sort -k2 > SHA256SUMS.txt)

du -sh delivery
ls -la delivery
