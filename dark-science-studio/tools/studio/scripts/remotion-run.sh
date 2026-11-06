#!/bin/sh
# Remotion launcher: pins the Sparticuz chromium wrapper + no-WebGL flags.
HERE="$(cd "$(dirname "$0")/../../.." && pwd)"
export LD_LIBRARY_PATH="$HERE/.chromium/libs"
exec "$@"
