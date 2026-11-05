#!/usr/bin/env python3
"""Measure one rendered lab sheet cell by cell.

    python3 scripts/lab_cells.py /tmp/host/lab1.png 8 8

Prints, for every cell, the ink bounding box (as a fraction of the cell), the
share of non-background pixels and the mean luma of the ink — enough to pick
parts (short vs long hair, closed vs open mouth) without seeing them.
"""
from __future__ import annotations

import sys

import numpy as np
from PIL import Image


def main() -> int:
    path = sys.argv[1]
    cols = int(sys.argv[2])
    rows = int(sys.argv[3])
    im = Image.open(path).convert('RGB')
    a = np.asarray(im, dtype=np.float64) / 255.0
    H, W, _ = a.shape
    lum = a @ np.array([0.2126, 0.7152, 0.0722])
    # the sheet background is a flat mid grey; anything far from it is ink
    bg = np.median(lum)
    ink = np.abs(lum - bg) > 0.06
    cw = W // cols
    chh = H // rows
    out = []
    for r in range(rows):
        for c in range(cols):
            # shrink: the 1 px cell border must not count as ink
            pad = 5
            y0, y1 = r * chh + pad, (r + 1) * chh - pad
            x0, x1 = c * cw + pad, (c + 1) * cw - pad
            sub = ink[y0:y1, x0:x1]
            ys, xs = np.nonzero(sub)
            if len(xs) == 0:
                out.append((r * cols + c, 0, 0, 0, 0, 0, 0))
                continue
            cwi = x1 - x0
            chi = y1 - y0
            bw = (xs.max() - xs.min() + 1) / cwi
            bh = (ys.max() - ys.min() + 1) / chi
            cover = sub.mean()
            meanl = lum[y0:y1, x0:x1][sub].mean()
            # horizontal symmetry of the silhouette
            left = sub[:, : cwi // 2].sum()
            right = sub[:, cwi // 2:].sum()
            sym = min(left, right) / max(left, right) if max(left, right) else 0
            out.append((r * cols + c, bw, bh, cover, meanl, sym,
                        (xs.min() / cwi, xs.max() / cwi, ys.min() / chi, ys.max() / chi)))
    print('idx    bbox_w bbox_h  cover  ink_luma  sym')
    for i, bw, bh, cover, meanl, sym, box in out:
        print('%3d   %6.3f %6.3f  %5.3f  %8.3f  %4.2f' % (i, bw, bh, cover, meanl, sym))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
