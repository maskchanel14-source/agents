#!/usr/bin/env python3
"""
setup_chromium.py — prepare the headless browser Remotion needs.

The sandbox blocks release-assets.githubusercontent.com, so Remotion's own
chrome-headless-shell download fails. Instead we use @sparticuz/chromium's
bundled build and decompress its brotli blobs ourselves (the JS API only
works inside a Lambda, where /tmp is writable and cwd is the task root).

Produces:
  .chromium/chromium           the binary
  .chromium/libs/              al2023 shared libs (libnspr4.so etc.)
  .chromium/chrome-wrapper.sh  sets LD_LIBRARY_PATH and execs the binary
"""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / ".bin" / "node_modules" / "@sparticuz" / "chromium" / "bin"
OUT = ROOT / ".chromium"


def brotli_decompress(src: Path, dst: Path) -> None:
    import brotli

    with src.open("rb") as f, dst.open("wb") as o:
        d = brotli.Decompressor()
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            o.write(d.process(chunk))


def main() -> int:
    if not BIN.exists():
        print(f"missing {BIN} — run: cd .bin && npm i @sparticuz/chromium", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    libs = OUT / "libs"

    # 1. shared libraries
    if not (libs / "libnspr4.so").exists():
        tar_path = OUT / "al2023.tar"
        brotli_decompress(BIN / "al2023.tar.br", tar_path)
        with tarfile.open(tar_path) as t:
            t.extractall(OUT / "_al2023")
        srcdir = next((OUT / "_al2023").rglob("libnspr4.so")).parent
        libs.mkdir(exist_ok=True)
        for f in srcdir.iterdir():
            if f.is_file():
                shutil.copy2(f, libs / f.name)
        shutil.rmtree(OUT / "_al2023", ignore_errors=True)
        tar_path.unlink(missing_ok=True)

    # 2. the browser binary
    binary = OUT / "chromium"
    if not binary.exists():
        brotli_decompress(BIN / "chromium.br", binary)
        binary.chmod(binary.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    # 3. wrapper
    wrapper = OUT / "chrome-wrapper.sh"
    wrapper.write_text(
        '#!/bin/sh\n'
        'HERE="$(cd "$(dirname "$0")" && pwd)"\n'
        'LD_LIBRARY_PATH="$HERE/libs" exec "$HERE/chromium" "$@"\n'
    )
    wrapper.chmod(0o755)

    print(f"chromium ready: {binary}")
    print(f"wrapper:        {wrapper}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
