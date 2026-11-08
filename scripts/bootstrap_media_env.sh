#!/usr/bin/env bash
# Bootstrap headless Cinema Engine v5 dependencies after a fresh container reset.
# Safe to run repeatedly (idempotent). Uses only whitelisted PyPI hosts.
set -euo pipefail

echo "[bootstrap_media_env] Installing Python media & validation packages..."
pip install --quiet --break-system-packages \
  opencv-python-headless \
  Pillow \
  numpy \
  imageio-ffmpeg \
  pyyaml

mkdir -p "$HOME/.bin"
FFMPEG_BIN="$(python3 -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')"
ln -sf "$FFMPEG_BIN" "$HOME/.bin/ffmpeg"

echo "[bootstrap_media_env] Verifying toolchain..."
python3 - << 'EOF'
import cv2, PIL, numpy, yaml, imageio_ffmpeg, subprocess
ff = imageio_ffmpeg.get_ffmpeg_exe()
ver = subprocess.check_output([ff, "-version"], text=True).splitlines()[0]
print(f"  OpenCV : {cv2.__version__}")
print(f"  Pillow : {PIL.__version__}")
print(f"  NumPy  : {numpy.__version__}")
print(f"  FFmpeg : {ver}")
EOF
echo "[bootstrap_media_env] Ready. Add \$HOME/.bin to PATH or resolve via imageio_ffmpeg.get_ffmpeg_exe()."
