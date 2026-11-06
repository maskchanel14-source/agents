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


def ds003_shots() -> list[tuple[float, float, str, dict]]:
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


def ds004_shots() -> list[tuple[float, float, str, dict]]:
    """Fatal familial insomnia — 32 shots across ~49 s.

    Beats: Bologna family -> one letter of DNA -> prion protein -> misfolding
    -> disinfection-proof -> thalamus -> stage-by-stage sleep loss -> autosomal
    dominance -> 18 months -> 100% fatality -> "it is you".
    """
    return [
        # 1 - cold open: the family that could not sleep
        (0.00, 1.45, "glitch_reveal", {"kicker": "1765 \u00b7 ITALY", "lines": ["NO SLEEP"], "sub": "ONE FAMILY \u00b7 TWO CENTURIES"}),
        # 2 - a pedigree, not yet diagnosed
        (1.45, 3.40, "pedigree", {"found": False, "label": "PEDIGREE / ONE FAMILY"}),
        # 3 - "traced to a single letter"
        (3.40, 4.60, "glitch_reveal", {"kicker": "DNA", "lines": ["ONE LETTER"]}),
        # 4 - the gene itself
        (4.60, 6.10, "handed_helix", {"label": "PRNP / CHROMOSOME 20", "split": False}),
        # 5 - "one mutation"
        (6.10, 7.40, "glitch_reveal", {"kicker": "MISSENSE", "lines": ["ONE MUTATION"], "sub": "D178N + METHIONINE 129"}),
        # 6 - the native protein
        (7.40, 9.00, "misfold_chain", {"state": "clear", "label": "PRP / NATIVE FOLD"}),
        # 7 - "in your brain right now"
        (9.00, 10.30, "mirror_colony", {"label": "NEURONS / PRP EXPRESSED", "mirror": False, "hud": [["LOCATION", "EVERY CELL"], ["FOLD", "ALPHA HELIX"], ["STATUS", "NORMAL"]]}),
        (10.30, 11.15, "glitch_reveal", {"lines": ["RIGHT NOW"]}),
        # 8 - misfolding begins
        (11.15, 12.55, "misfold_chain", {"state": "seeding", "label": "MISFOLDING / CONTACT"}),
        (12.55, 13.75, "glitch_reveal", {"kicker": "CONTACT", "lines": ["NEIGHBOURS"]}),
        # 9 - the stack locks
        (13.75, 14.90, "misfold_chain", {"state": "locked", "label": "PROPAGATION / LOCKED"}),
        # 10 - the aggregate inside the neuron
        (14.90, 16.30, "mirror_colony", {"label": "INTRACELLULAR / AGGREGATE", "mirror": False, "divide": True, "hud": [["AGGREGATE", "INSOLUBLE"], ["PROTEASE", "RESISTANT"], ["CLEARANCE", "NONE"]]}),
        # 11 - disinfection fails
        (16.30, 17.60, "glitch_reveal", {"kicker": "DISINFECTION: FAILS", "lines": ["SURVIVES"]}),
        (17.60, 19.90, "glitch_reveal", {"lines": ["BOILING", "BLEACH"], "sub": "AUTOCLAVE: 134\u00b0C \u00b7 STILL INFECTIOUS"}),
        # 12 - the thalamus
        (19.90, 21.45, "thalamus_grid", {"dead": None, "label": "THALAMUS / TARGET"}),
        # 13 - walnut-sized
        (21.45, 23.05, "glitch_reveal", {"kicker": "YOUR THALAMUS", "lines": ["WALNUT"], "sub": "ABOUT SIXTY GRAMS"}),
        (23.05, 25.05, "glitch_reveal", {"kicker": "EVERY NIGHT", "lines": ["WHEN YOU SLEEP"]}),
        # 14 - stage by stage: spindles
        (25.05, 26.55, "thalamus_grid", {"dead": "spindles", "label": "SPINDLES / LOST"}),
        (26.55, 27.80, "glitch_reveal", {"lines": ["DEEP SLEEP"], "sub": "STAGE 3-4 \u00b7 ABSENT"}),
        # 15 - and REM
        (27.80, 29.90, "thalamus_grid", {"dead": "rem", "label": "REM / LOST"}),
        # 16 - "awake for months"
        (29.90, 31.25, "glitch_reveal", {"kicker": "FOR MONTHS", "lines": ["AWAKE"]}),
        (31.25, 32.90, "glitch_reveal", {"lines": ["HEART RACING"], "sub": "SWEATING \u00b7 FEVER \u00b7 TACHYCARDIA"}),
        (32.90, 34.90, "glitch_reveal", {"lines": ["BURNING FUEL"], "sub": "THAT THE BODY CANNOT STORE"}),
        # 17 - inheritance
        (34.90, 36.60, "pedigree", {"found": True, "label": "INHERITANCE / 1 IN 2"}),
        (36.60, 38.10, "glitch_reveal", {"kicker": "BEFORE THE FIRST SYMPTOM", "lines": ["DECADES"]}),
        (38.10, 39.90, "pedigree", {"found": True, "label": "CARRIERS / KNOWN EARLY"}),
        # 18 - eighteen months
        (39.90, 41.25, "counter_slam", {"from": 60, "to": 18, "suffix": "MO", "label": "MEDIAN SURVIVAL", "caption": "eighteen months from onset"}),
        (41.25, 43.10, "glitch_reveal", {"kicker": "NO APPROVED THERAPY", "lines": ["NO TREATMENT"]}),
        # 19 - seventy families
        (43.10, 44.40, "counter_slam", {"from": 300, "to": 70, "suffix": "FAM", "label": "KNOWN KINDREDS", "caption": "about seventy families on earth"}),
        # 20 - zero survivors
        (44.40, 46.45, "mortality", {"readout": "100", "caption": "ZERO SURVIVORS"}),
        # 21 - not infectious
        (46.45, 47.75, "glitch_reveal", {"kicker": "IT CANNOT SPREAD TO YOU", "lines": ["NOT", "INFECTIOUS"]}),
        # 22 - "it is you"
        (47.75, 49.60, "glitch_reveal", {"kicker": "PRNP \u00b7 CHROMOSOME 20", "lines": ["IT IS YOU"]}),
    ]


SHOT_LISTS = {
    "DS-003": ds003_shots,
    "DS-004": ds004_shots,
}


def build_shots(project_id: str) -> list[tuple[float, float, str, dict]]:
    if project_id not in SHOT_LISTS:
        raise SystemExit(f"no shot list for {project_id}; known: {sorted(SHOT_LISTS)}")
    return SHOT_LISTS[project_id]()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--build", required=True)
    args = ap.parse_args()
    proj, build = Path(args.project), Path(args.build)

    words = json.loads((build / "words.json").read_text())
    voice_end = words[-1]["end"]
    shots_raw = build_shots(proj.name)

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

    meta_path = proj / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    meta = {
        "accent": meta.get("accent", "#22D3EE"),
        "id": meta.get("id", proj.name),
        "durationS": round(total_frames / FPS, 3),
    }
    props = {
        "shots": shots,
        "words": words,
        "durationInFrames": total_frames,
        "mixFile": f"projects/{proj.name}/mix.wav",
        "meta": meta,
    }
    (build / "props.json").write_text(json.dumps(props, indent=2), encoding="utf-8")

    print(f"[timeline] {len(shots)} shots, {total_frames} frames, {timeline['duration_s']}s")
    print(f"[timeline] mean shot {timeline['mean_shot_s']}s, min {timeline['min_shot_s']}s")
    for i, (s, d) in enumerate(zip(shots, durations)):
        print(f"  {i + 1:02d} {s['from'] / FPS:5.2f}-{s['to'] / FPS:5.2f} ({d:.2f}s) {s['scene']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
