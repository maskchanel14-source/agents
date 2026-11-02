#!/usr/bin/env bash
# Portable local-render helper for this sandbox. It resolves the NPM-provided encoder
# and headless Chromium, avoiding a browser download at render time.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
FFMPEG_PATH="$(node -e "console.log(require('@ffmpeg-installer/ffmpeg').path)")"
BROWSER_PATH="$(node --input-type=module -e "import chromium from '@sparticuz/chromium'; console.log(await chromium.executablePath())")"
# The package is built for AWS Lambda. Its included NSS/NSPR libraries are safe to
# unpack locally and are required on this minimal renderer image.
node --input-type=module -e "import {inflate} from '@sparticuz/chromium'; await inflate('./node_modules/@sparticuz/chromium/bin/al2023.tar.br')" >/dev/null
export PATH="$(dirname "$FFMPEG_PATH"):$PATH"
export LD_LIBRARY_PATH="/tmp/al2023/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export REMOTION_BROWSER_EXECUTABLE="$BROWSER_PATH"
exec "$@" --browser-executable="$BROWSER_PATH"
