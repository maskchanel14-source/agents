#!/usr/bin/env python3
"""
make_timeline.py -- builds projects/<ID>/timeline.json + build/<ID>/props.json
from words.json (real voice timings) and a hand-authored shot list.

Shot list format (python literal below): (start_s, end_s, scene, props)

Design rules baked in:
  * mean shot length <= 4.0 s  (DS-002 set the bar at 2.3 s; DS-003 was 5.9 s)
  * every shot must carry internal motion
  * cuts land on sentence boundaries, never mid-word
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FPS = 30


def build_shots() -> list[tuple[float, float, str, dict]]:
    return [
        # 1 - cold open: the colony, already moving
        (0.00, 2.35, "mirror_colony", {"label": "DEC 2024 / SCIENCE", "mirror": False}),
        # 2 - "published a warning"
        (2.35, 4.70, "glitch_reveal", {"kicker": "38 SIGNATORIES", "lines": ["A WARNING"]}),
        # 3 - "not about a bomb"
        (4.70, 6.30, "glitch_reveal", {"lines": ["NOT A BOMB"], "sub": "NOT A WEAPON · NOT AN ACCIDENT"}),
        # 4 - "about a bacterium / one that does not exist yet"
        (6.30, 8.45, "glitch_reveal", {"lines": ["A BACTERIUM"], "sub": "IT DOES NOT EXIST YET"}),
        # 5 - built the same way
        (8.45, 10.45, "mirror_colony", {"label": "ALL LIFE / ONE HANDEDNESS", "mirror": False}),
        # 6 - handedness
        (10.45, 12.95, "handed_helix", {"label": "LIFE / CHIRAL", "split": False}),
        # 7 - sugars right, proteins left
        (12.95, 15.30, "handed_helix", {"label": "SUGARS → / PROTEINS ←", "split": True}),
        # 8 - immune system reads that shape
        (15.30, 17.95, "immune_siege", {"label": "SHAPE RECOGNITION"}),
        # 9 - now flip it
        (17.95, 19.60, "glitch_reveal", {"kicker": "INVERT EVERY BOND", "lines": ["FLIP IT"]}),
        # 10 - build the same cell in mirror image
        (19.60, 21.40, "mirror_colony", {"label": "MIRROR CELL / D-CHIRAL", "mirror": True}),
        # 11 - antibodies would not grip it
        (21.40, 23.60, "immune_siege", {"label": "ANTIBODY BINDING"}),
        # 12 - phages would not infect it
        (23.60, 25.40, "phage_storm", {"label": "PHAGE ASSAY"}),
        # 13 - antibiotics would not touch it
        (25.40, 27.15, "glitch_reveal", {"kicker": "NO TARGET TO HIT", "lines": ["NOTHING", "TOUCHES IT"]}),
        # 14 - eats what you eat
        (27.15, 29.10, "mirror_colony", {"label": "NUTRIENT UPTAKE", "mirror": True, "divide": True}),
        # 15 - nothing on this planet could eat it
        (29.10, 30.85, "phage_storm", {"label": "NO PREDATOR", "noFade": False}),
        # 16 - ten years
        (30.85, 33.90, "counter_slam", {"from": 30, "to": 10, "suffix": "YRS", "label": "CONCERTED FUNDING", "caption": "ten years if we funded it"}),
        # 17 - fifteen to thirty
        (33.90, 36.35, "counter_slam", {"from": 15, "to": 30, "label": "CURRENT TRAJECTORY", "caption": "fifteen to thirty on this path"}),
        # 18 - not a ban on knowledge
        (36.35, 38.70, "glitch_reveal", {"kicker": "OR: A BAN ON QUESTIONS", "lines": ["NOT", "KNOWLEDGE"]}),
        # 19 - asking us to never build it
        (38.70, 40.50, "hand_wall", {"label": "THE ASK", "word": "NEVER"}),
        # 20 - thirty-eight scientists, one warning
        (40.50, 41.75, "hand_wall", {"label": "38 SIGNATORIES", "word": "38"}),
        # 21 - please / loop back
        (41.75, 44.00, "mirror_colony", {"label": "STILL NOT BUILT", "mirror": True}),
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--build", required=True)
    args = ap.parse_args()
    proj, build = Path(args.project), Path(args.build)

    words = json.loads((build / "words.json").read_text())
    voice_end = words[-1]["end"]
    shots_raw = build_shots()

    # stretch the tail shot so the video ends exactly with the voice + 0.4 s
    last = shots_raw[-1]
    shots_raw[-1] = (last[0], max(last[1], voice_end + 0.35), last[2], last[3])

    shots = []
    for start, end, scene, props in shots_raw:
        shots.append(
            {
                "scene": scene,
                "from": int(round(start * FPS)),
                "to": int(round(end * FPS)),
                "props": props,
            }
        )

    total_frames = shots[-1]["to"]
    durations = [(s["to"] - s["from"]) / FPS for s in shots]
    timeline = {
        "fps": FPS,
        "duration_s": round(total_frames / FPS, 3),
        "durationInFrames": total_frames,
        "shot_count": len(shots),
        "cuts": len(shots) - 1,
        "mean_shot_s": round(sum(durations) / len(durations), 2),
        "min_shot_s": round(min(durations), 2),
        "shots": shots,
    }
    (proj / "timeline.json").write_text(json.dumps(timeline, indent=2), encoding="utf-8")

    props = {
        "shots": shots,
        "words": words,
        "durationInFrames": total_frames,
        "mixFile": f"projects/{proj.name}/mix.wav",
    }
    (build / "props.json").write_text(json.dumps(props, indent=2), encoding="utf-8")

    print(f"[timeline] {len(shots)} shots, {total_frames} frames, {timeline['duration_s']}s")
    print(f"[timeline] mean shot {timeline['mean_shot_s']}s, min {timeline['min_shot_s']}s")
    for i, (s, d) in enumerate(zip(shots, durations)):
        print(f"  {i + 1:02d} {s['from'] / FPS:5.2f}-{s['to'] / FPS:5.2f} ({d:.2f}s) {s['scene']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
