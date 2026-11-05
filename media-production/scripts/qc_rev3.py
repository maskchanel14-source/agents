#!/usr/bin/env python3
"""
Revision-3 delivery QC: objective measurements for the QC-REPORT.md tables.

  python3 scripts/qc_rev3.py            # prints the markdown tables
  python3 scripts/qc_rev3.py --json     # machine-readable

Measures, on the delivered stills:
  * exposure   - mean luma, 95th percentile, share of pixels below 0.06 luma
                 ("crushed" - the thing that went wrong on the first rev-3 pass)
  * palette    - mean saturation + share of near-black pixels
and, on the master:
  * container  - duration, resolution, codecs, bitrates, size
  * audio      - integrated loudness, true peak, loudness range
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(HERE)
PROJ = os.path.join(os.path.dirname(STUDIO), "projects",
                    "SHORTS-2026-024-Binance-63B")
FFMPEG = subprocess.run(
    ["node", "-e",
     "console.log(require('%s/node_modules/@ffmpeg-installer/ffmpeg').path)" % STUDIO],
    capture_output=True, text=True, check=True).stdout.strip()


def frame_stats(path: str) -> dict:
    im = Image.open(path).convert("RGB")
    a = np.asarray(im, dtype=np.float64) / 255.0
    lum = a @ np.array([0.2126, 0.7152, 0.0722])
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    return {
        "mean": round(float(lum.mean()), 3),
        "p95": round(float(np.percentile(lum, 95)), 3),
        "crushed": round(float((lum < 0.06).mean() * 100), 1),
        "clip": round(float((lum > 0.985).mean() * 100), 2),
        "sat": round(float(sat.mean()), 3),
    }


def probe(path: str) -> dict:
    out = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", path],
        capture_output=True, text=True).stderr
    info = {"raw": out}
    for pat, key in ((r"Duration: (\d+):(\d+):(\d+\.\d+)", "duration"),
                     (r"Stream #.*Video: (.*)", "video"),
                     (r"Stream #.*Audio: (.*)", "audio")):
        m = __import__("re").search(pat, out)
        if m:
            info[key] = m.group(0)
    return info


def loudness(path: str) -> dict:
    out = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", path,
         "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    res = {}
    grab = {"I:": "i", "Peak:": "tp", "LRA:": "lra"}
    for line in out.splitlines():
        for k, v in grab.items():
            if k in line:
                try:
                    res[v] = float(line.split(k)[1].split()[0])
                except (IndexError, ValueError):
                    pass
    return res


def main() -> int:
    as_json = "--json" in sys.argv
    video = os.path.join(PROJ, "out", "final.mp4")
    wav = os.path.join(PROJ, "audio", "final3.wav")
    stills_dir = os.path.join(PROJ, "stills")

    report: dict = {}
    if os.path.exists(video):
        p = probe(video)
        report["master"] = {
            "bytes": os.path.getsize(video),
            "mb": round(os.path.getsize(video) / 1e6, 1),
            "video_line": p.get("video", ""),
            "audio_line": p.get("audio", ""),
            "duration_line": p.get("duration", ""),
        }
    if os.path.exists(wav):
        report["audio"] = loudness(wav)

    rows = []
    if os.path.isdir(stills_dir):
        for name in sorted(os.listdir(stills_dir)):
            if not name.endswith(".png"):
                continue
            st = frame_stats(os.path.join(stills_dir, name))
            beat = name[:-4].split("_", 1)[1].rsplit("_f", 1)
            rows.append({"file": name, "beat": beat[0],
                         "frame": int(beat[1]), **st})
    report["stills"] = rows

    if as_json:
        print(json.dumps(report, indent=2))
        return 0

    if "master" in report:
        m = report["master"]
        print("## master")
        for k in ("duration_line", "video_line", "audio_line"):
            print("  " + (m[k] or "-"))
        print("  size: %.1f MB" % m["mb"])
    if "audio" in report:
        a = report["audio"]
        print("## audio")
        print("  I = %.2f LUFS   TP = %.2f dBFS   LRA = %.2f LU"
              % (a.get("i", float("nan")), a.get("tp", float("nan")),
                 a.get("lra", float("nan"))))
    print("## exposure per still")
    print("| beat | frame | mean | p95 | crushed <0.06 | clipped | sat |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        print("| %s | %d | %.3f | %.3f | %.1f %% | %.2f %% | %.3f |"
              % (r["beat"], r["frame"], r["mean"], r["p95"], r["crushed"],
                 r["clip"], r["sat"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
