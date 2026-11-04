#!/usr/bin/env python3
"""
Print a frame as ASCII so it can be inspected without an image viewer.

  python3 scripts/ascii_frame.py frame.png [width=60] [mode=lum|hue]

Characters are about twice as tall as they are wide, so the row count is
derived from the source aspect ratio.

  lum  — 10-step luminance ramp   " .:-=+*#%@"
  hue  — colour family per cell   r red, y yellow, g green, c cyan, b blue,
                                  m magenta, w white/grey, k near-black,
                                  . dark grey
"""
import sys
import numpy as np
from PIL import Image

RAMP = " .:-=+*#%@"


def hue_char(rgb: np.ndarray) -> str:
    r, g, b = float(rgb[0]), float(rgb[1]), float(rgb[2])
    mx, mn = max(r, g, b), min(r, g, b)
    v = mx / 255.0
    if v < 0.10:
        return "k"
    s = 0.0 if mx == 0 else (mx - mn) / mx
    if s < 0.14:
        return "w" if v > 0.45 else "."
    if mx == r:
        return "y" if g > b + 18 else ("m" if b > g + 18 else "r")
    if mx == g:
        return "y" if r > b + 18 else "g"
    return "c" if g > r + 18 else "b"


def main() -> None:
    path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    mode = sys.argv[3] if len(sys.argv) > 3 else "lum"

    im = Image.open(path).convert("RGB")
    w, h = im.size
    rows = max(1, int(width * (h / w) * 0.5))
    small = np.asarray(im.resize((width, rows), Image.LANCZOS)).astype(np.float32)

    lum = (0.2126 * small[:, :, 0] + 0.7152 * small[:, :, 1] + 0.0722 * small[:, :, 2]) / 255.0

    print(f"{path}  {w}x{h}  ->  {width}x{rows}  mode={mode}")
    print("+" + "-" * width + "+")
    for y in range(rows):
        line = []
        for x in range(width):
            if mode == "hue":
                line.append(hue_char(small[y, x]))
            else:
                line.append(RAMP[min(len(RAMP) - 1, int(lum[y, x] * len(RAMP)))])
        print("|" + "".join(line) + "|")
    print("+" + "-" * width + "+")

    # quick numeric summary
    print(
        f"luma  min={lum.min():.3f} mean={lum.mean():.3f} max={lum.max():.3f} "
        f"p05={np.percentile(lum,5):.3f} p95={np.percentile(lum,95):.3f}"
    )
    sat = (small.max(axis=2) - small.min(axis=2)) / np.maximum(small.max(axis=2), 1)
    print(f"saturation mean={sat.mean():.3f}  pct_below_0.06_luma={(lum < 0.06).mean()*100:.2f}%")


if __name__ == "__main__":
    main()
