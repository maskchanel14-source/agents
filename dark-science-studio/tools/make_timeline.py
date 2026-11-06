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


def ds005_shots() -> list[tuple[float, float, str, dict]]:
    """Betelgeuse / Siwarha - 30 shots across ~47.3 s.

    Beats: hook (a star inside a star) -> scale -> thin envelope -> the radio
    detection -> the disc going out of round -> 2 R* orbit -> undetectable
    directly -> the 2,100-day heartbeat -> loop back to the hook.
    """
    return [
        # 1 - cold open: the companion inside the photosphere
        (0.00, 2.20, "star_wake", {"sep": 0.95}),
        (2.20, 3.45, "glitch_reveal", {"kicker": "BETELGEUSE \u00b7 642 LY", "lines": ["NOT", "NEXT TO IT"]}),
        (3.45, 4.85, "glitch_reveal", {"kicker": "ORBIT: INSIDE", "lines": ["IN", "THE ATMOSPHERE"]}),
        # 2 - scale
        (4.85, 6.35, "star_wake", {"sep": 0.15, "r": 8.8, "label": "RED SUPERGIANT"}),
        (6.35, 7.90, "counter_slam", {"from": 12, "to": 700, "suffix": "R\u2609", "label": "STELLAR RADIUS", "caption": "seven hundred times the width of the sun"}),
        (7.90, 9.45, "star_wake", {"sep": 0.55, "label": "ORBIT OF MARS"}),
        (9.45, 10.85, "glitch_reveal", {"kicker": "SUN REPLACED", "lines": ["SWALLOWS", "MARS"]}),
        # 3 - the envelope is barely a surface
        (10.85, 12.40, "star_wake", {"sep": 0.80, "r": 8.0, "label": "PHOTOSPHERE \u00b7 3,500 K"}),
        (12.40, 13.75, "glitch_reveal", {"lines": ["BARELY"], "sub": "A SURFACE AT ALL"}),
        (13.75, 15.55, "star_wake", {"sep": 0.30, "label": "OUTER ENVELOPE"}),
        # 4 - something is moving through it
        (15.55, 16.85, "star_wake", {"sep": 0.72, "label": "PASSAGE / 2021-2026"}),
        (16.85, 18.20, "glitch_reveal", {"kicker": "SOMETHING ORBITS", "lines": ["THROUGH IT"]}),
        # 5 - the radio detection
        (18.20, 19.90, "glitch_reveal", {"kicker": "VLA + ALMA", "lines": ["RADIO"], "sub": "22 \u2192 485 GHz \u00b7 SEVEN BANDS"}),
        (19.90, 21.60, "counter_slam", {"from": 1, "to": 7, "suffix": "BAND", "label": "RADIO FREQUENCIES", "caption": "twenty two to four hundred eighty five gigahertz"}),
        (21.60, 23.20, "star_wake", {"sep": 0.45, "label": "SIX YEARS OF EPOCHS"}),
        # 6 - the disc deforms
        (23.20, 24.80, "star_wake", {"sep": 0.98, "label": "MAXIMUM SEPARATION"}),
        (24.80, 26.30, "glitch_reveal", {"kicker": "THE DISC", "lines": ["OUT OF ROUND"]}),
        (26.30, 27.60, "star_wake", {"sep": 0.05, "label": "BACK IN ROUND"}),
        # 7 - the 2 R* orbit
        (27.60, 29.60, "star_wake", {"sep": 0.60, "label": "SEPARATION \u2248 2 R\u2609"}),
        (29.60, 31.00, "counter_slam", {"from": 20, "to": 2, "suffix": "R\u2609", "label": "ORBITAL DISTANCE", "caption": "two stellar radii from the core"}),
        (31.00, 32.60, "star_wake", {"sep": 0.88, "label": "GAS IT ORBITS IN"}),
        # 8 - invisible
        (32.60, 34.20, "glitch_reveal", {"kicker": "UNRESOLVED", "lines": ["TOO FAINT"]}),
        (34.20, 35.80, "counter_slam", {"from": 100, "to": 10, "suffix": "x", "label": "BELOW MAP LIMIT", "caption": "ten to a hundred times too faint for the maps"}),
        (35.80, 37.30, "star_wake", {"sep": 0.25, "label": "NO DIRECT IMAGE"}),
        # 9 - the heartbeat
        (37.30, 39.00, "glitch_reveal", {"kicker": "WHY WE KNOW IT IS THERE", "lines": ["IT BREATHES", "UNEVENLY"]}),
        (39.00, 41.20, "counter_slam", {"from": 300, "to": 2100, "suffix": "D", "label": "WOBBLE CYCLE", "caption": "two thousand one hundred days"}),
        (41.20, 43.20, "star_wake", {"sep": 0.70, "label": "CYCLE / REPEATING"}),
        # 10 - loop close
        (43.20, 45.00, "glitch_reveal", {"kicker": "ONE DAY IT EXPLODES", "lines": ["A PASSENGER"]}),
        (45.00, 47.30, "star_wake", {"sep": 0.95}),
    ]


def ds006_shots() -> list[tuple[float, float, str, dict]]:
    """KM3-230213A - 30 shots across ~49.4 s."""
    return [
        # 1 - cold open: the track ripping through the detector
        (0.00, 2.40, "neutrino_shower", {"impact": 0.55, "label": "KM3NeT / ARCA"}),
        (2.40, 4.65, "glitch_reveal", {"kicker": "MEDITERRANEAN SEA", "lines": ["3.5 KM", "DOWN"]}),
        # 2 - one particle, a third of the detector
        (4.65, 6.30, "neutrino_shower", {"impact": 0.30, "label": "SINGLE MUON"}),
        (6.30, 8.00, "counter_slam", {"from": 1, "to": 30, "suffix": "%", "label": "PMTS LIT", "caption": "more than a third of the sensors"}),
        (8.00, 9.30, "neutrino_shower", {"impact": 0.18, "label": "1 KM\u00b3 OF WATER"}),
        # 3 - ghost particles
        (9.30, 10.75, "glitch_reveal", {"kicker": "NEUTRINOS", "lines": ["GHOST", "PARTICLES"]}),
        (10.75, 12.30, "neutrino_shower", {"impact": 0.10, "cone": False, "label": "THROUGH THE PLANET"}),
        (12.30, 13.75, "glitch_reveal", {"lines": ["NO PLANET", "STOPS THEM"]}),
        # 4 - the event
        (13.75, 15.40, "glitch_reveal", {"kicker": "13 FEB 2023", "lines": ["ONE", "MUON"]}),
        (15.40, 16.90, "neutrino_shower", {"impact": 0.34, "label": "EVENT / KM3-230213A"}),
        (16.90, 18.95, "neutrino_shower", {"impact": 0.50, "label": "RECONSTRUCTED TRACK"}),
        # 5 - 220 PeV
        (18.95, 20.80, "glitch_reveal", {"kicker": "RECONSTRUCTED ENERGY", "lines": ["220", "PeV"]}),
        (20.80, 22.70, "counter_slam", {"from": 7, "to": 220, "suffix": "PeV", "label": "NEUTRINO ENERGY", "caption": "two hundred and twenty peta electronvolts"}),
        (22.70, 24.30, "neutrino_shower", {"impact": 0.42, "label": "72 - 2,600 PeV / 90% CL"}),
        # 6 - 30x the record
        (24.30, 26.45, "counter_slam", {"from": 1, "to": 30, "suffix": "x", "label": "PREVIOUS RECORD", "caption": "about thirty times the old maximum"}),
        (26.45, 28.00, "neutrino_shower", {"impact": 0.28, "label": "RECORD / BROKEN"}),
        (28.00, 29.35, "glitch_reveal", {"kicker": "APRIL 2025 -> 2026", "lines": ["BARELY", "BUILT"]}),
        # 7 - detector under construction
        (29.35, 31.10, "counter_slam", {"from": 100, "to": 10, "suffix": "%", "label": "DETECTOR COMPLETE", "caption": "ten percent of the final volume"}),
        (31.10, 32.70, "neutrino_shower", {"impact": 0.20, "label": "UNDER CONSTRUCTION"}),
        (32.70, 34.10, "glitch_reveal", {"kicker": "WHEN FINISHED", "lines": ["200,000", "SENSORS"]}),
        # 8 - the problem
        (34.10, 35.30, "glitch_reveal", {"kicker": "ICECUBE / SOUTH POLE", "lines": ["NOTHING"]}),
        (35.30, 36.80, "neutrino_shower", {"impact": 0.60, "label": "SOUTH POLE / SILENT"}),
        (36.80, 38.40, "glitch_reveal", {"kicker": "TWO DETECTORS \u00b7 ONE SKY", "lines": ["3\u03c3", "DISAGREEMENT"]}),
        # 9 - new physics
        (38.40, 40.10, "glitch_reveal", {"lines": ["NEW", "PHYSICS"]}),
        (40.10, 41.60, "neutrino_shower", {"impact": 0.75, "label": "STERILE NEUTRINOS?"}),
        (41.60, 43.30, "glitch_reveal", {"kicker": "OR", "lines": ["LUCKY"]}),
        # 10 - loop close
        (43.30, 45.20, "glitch_reveal", {"kicker": "ONE FLASH", "lines": ["A CRACK"]}),
        (45.20, 47.60, "neutrino_shower", {"impact": 0.20}),
        (47.60, 49.40, "glitch_reveal", {"lines": ["IN PHYSICS"]}),
    ]


def ds007_shots() -> list[tuple[float, float, str, dict]]:
    """N. fowleri - 30 shots across ~46.7 s. Hard rule: every number must match
    the CDC wording recorded in sources_and_licenses.md."""
    return [
        # 1 - cold open
        (0.00, 2.10, "nerve_invasion", {"invasion": 0.55, "label": "OLFACTORY ROUTE"}),
        (2.10, 3.50, "glitch_reveal", {"kicker": "WARM FRESH WATER", "lines": ["UP", "THE NOSE"]}),
        (3.50, 5.00, "glitch_reveal", {"kicker": "NAEGLERIA FOWLERI", "lines": ["NOT A", "PARASITE"]}),
        # 2 - where it lives
        (5.00, 6.60, "mirror_colony", {"label": "N. FOWLERI / CULTURE", "mirror": False, "divide": True, "hud": [["MODE", "TROPHOZOITE"], ["FEED", "BACTERIA"], ["MOTILE", "YES"]]}),
        (6.60, 8.30, "counter_slam", {"from": 0, "to": 30, "suffix": "\u00b0C", "label": "WATER TEMPERATURE", "caption": "thrives above thirty degrees celsius"}),
        (8.30, 9.70, "mirror_colony", {"label": "FRESH WATER ONLY", "mirror": True, "hud": [["LAKES", "RISK"], ["RIVERS", "RISK"], ["OCEAN", "SAFE"]]}),
        # 3 - not by drinking
        (9.70, 11.20, "glitch_reveal", {"kicker": "SWALLOWED", "lines": ["HARMLESS"]}),
        (11.20, 12.90, "glitch_reveal", {"kicker": "STOMACH ACID", "lines": ["DESTROYS IT"]}),
        # 4 - the route in
        (12.90, 14.60, "nerve_invasion", {"invasion": 0.15, "label": "ENTRY / NASAL"}),
        (14.60, 16.20, "nerve_invasion", {"invasion": 0.45, "label": "CRIBRIFORM PLATE"}),
        (16.20, 17.70, "glitch_reveal", {"kicker": "ONE ROUTE IN", "lines": ["THE NOSE"]}),
        (17.70, 19.40, "nerve_invasion", {"invasion": 0.80, "label": "OLFACTORY NERVE"}),
        (19.40, 21.20, "nerve_invasion", {"invasion": 1.0, "label": "INTO THE BRAIN"}),
        (21.20, 22.60, "glitch_reveal", {"kicker": "THEN", "lines": ["IT MULTIPLIES"]}),
        # 5 - the clock
        (22.60, 24.40, "counter_slam", {"from": 30, "to": 5.3, "suffix": "D", "label": "SYMPTOM TO DEATH", "caption": "five point three days, on average"}),
        (24.40, 26.30, "glitch_reveal", {"kicker": "EXPOSURE TO DEATH", "lines": ["9.9", "DAYS"]}),
        # 6 - the numbers
        (26.30, 28.10, "counter_slam", {"from": 1, "to": 167, "suffix": "CASES", "label": "USA / 1962-2024", "caption": "one hundred sixty seven american cases"}),
        (28.10, 29.70, "nerve_invasion", {"invasion": 0.92, "label": "CDC SURVEILLANCE"}),
        (29.70, 31.10, "counter_slam", {"from": 167, "to": 4, "suffix": "ALIVE", "label": "SURVIVORS", "caption": "four people survived"}),
        (31.10, 32.90, "glitch_reveal", {"lines": ["4", "OF 167"]}),
        # 7 - fatality
        (32.90, 34.60, "counter_slam", {"from": 0, "to": 97, "suffix": "%", "label": "FATALITY", "caption": "above ninety seven percent"}),
        (34.60, 36.20, "glitch_reveal", {"kicker": "NO VACCINE \u00b7 NO IMMUNITY", "lines": ["NO TIME"]}),
        # 8 - the survivor
        (36.20, 38.20, "glitch_reveal", {"kicker": "FLORIDA \u00b7 2016", "lines": ["ONE", "SURVIVOR"]}),
        (38.20, 40.30, "nerve_invasion", {"invasion": 0.35, "label": "TREATED WITHIN HOURS"}),
        # 9 - the twist
        (40.30, 41.70, "glitch_reveal", {"kicker": "SALT WATER", "lines": ["KILLS IT"]}),
        (41.70, 43.20, "mirror_colony", {"label": "SEA WATER / 3.5% NACL", "mirror": False, "hud": [["SALINITY", "LETHAL"], ["OCEAN", "SAFE"]]}),
        (43.20, 44.70, "nerve_invasion", {"invasion": 0.70, "label": "THE LAKE IS NOT"}),
        # 10 - loop close
        (44.70, 46.70, "glitch_reveal", {"kicker": "IT BEGINS AS", "lines": ["A HEADACHE"]}),
    ]


SHOT_LISTS = {
    "DS-003": ds003_shots,
    "DS-004": ds004_shots,
    "DS-005": ds005_shots,
    "DS-006": ds006_shots,
    "DS-007": ds007_shots,
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
