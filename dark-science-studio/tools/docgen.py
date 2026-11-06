#!/usr/bin/env python3
"""
docgen.py -- derive the per-episode paperwork that must not be hand-typed.

    python tools/docgen.py --project projects/DS-005

Reads  projects/<id>/script.txt, timeline.json, qa_report.json, meta.json
Writes projects/<id>/script_spec.json      (engine, wpm, per-line table)
       <id>/publishing_kit.txt             (plain-text twin of the .md kit)
       <id>/qa_selfreview.md               (measured table + honest verdict)
The prose that needs a human (claims, titles, pinned comment) stays hand-written
in publishing_kit.md and sources_and_licenses.md.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def spec(proj: Path) -> dict:
    build = ROOT / "build" / proj.name
    words = json.loads((build / "words.json").read_text())
    lines = [ln for ln in (proj / "script.txt").read_text().split("\n") if ln.strip()]
    i = 0
    table = []
    for n, ln in enumerate(lines):
        count = len(ln.split())
        table.append({"i": n, "text": ln, "start": round(words[i]["start"], 3), "end": round(words[i + count - 1]["end"], 3)})
        i += count
    dur = round(words[-1]["end"], 3)
    return {
        "engine": "piper en_US-lessac-medium (offline, no key)",
        "length_scale": 0.95,
        "sample_rate": 16000,
        "duration_s": dur,
        "word_count": sum(len(ln.split()) for ln in lines),
        "wpm": round(sum(len(ln.split()) for ln in lines) / dur * 60, 1),
        "lines": table,
    }


def selfreview(proj: Path, score: dict) -> str:
    d = json.loads((proj / "qa_report.json").read_text())
    t = json.loads((proj / "timeline.json").read_text())
    s, fz, sc, ld, cp, lm = (d["specs"], d["freeze_black"], d["scene_changes"],
                             d["loudness"], d["captions"], d["luminance"])
    notes = score["notes"]
    rows = [
        ("Specs", f"{s['duration_s']} s · {s['width']}×{s['height']} · {int(s['fps'])} fps · {s['video_codec']} + {s['audio_codec']} · {s['size_mb']} MB", "9:16, ≤ 58 s", s["passed"]),
        ("Freeze / black", f"{fz['frozen_runs']} frozen runs · {fz['black_frames']} black frames", "0 / 0", fz["passed"]),
        ("Cut density", f"{sc['cuts']} detected cuts (authored {t['cut_count'] if 'cut_count' in t else t['cuts']}) · mean shot {t['mean_shot_s']} s", "≥ 1 cut / 3 s", sc["passed"]),
        ("Loudness", f"{ld['integrated_lufs']} LUFS · {ld['true_peak_dbtp']} dBTP", "−14 ±1 / ≤ −1 dBTP", ld["passed"]),
        ("Captions", f"{cp['cues']} cues · monotonic {cp['monotonic']} · max gap {cp['max_gap_s']} s · last end {cp['last_end_s']} s", "monotonic, gap ≤ 0.4 s", cp["passed"]),
        ("Luminance", f"mean {lm['mean_luma']} ({lm['min_luma']}–{lm['max_luma']})", "0.03–0.20", lm["passed"]),
        ("Whisper ASR", "**SKIPPED** — faster-whisper weights unreachable (huggingface.co blocked)", "≥ 0.97 word match", None),
    ]
    out = [
        f"# {proj.name} — QA Self-Review",
        "",
        f"**Delivered:** {score['date']} · `renders/{proj.name}/final.mp4`",
        f"**Gate result:** `all_passed: {d['all_passed']}` · `degraded: {d['degraded']}` · `skipped_checks: {d['skipped_checks']}`",
        f"**Self-score: {score['score']} / 10**",
        "",
        "---",
        "",
        "## 1. Measured results (`qa_report.json`)",
        "",
        "| Check | Result | Threshold | Verdict |",
        "|---|---|---|---|",
    ]
    for name, res, thr, ok in rows:
        verdict = "PASS" if ok else ("not verified" if ok is None else "**FAIL**")
        out.append(f"| {name} | {res} | {thr} | {verdict} |")
    out += ["", "---", "", "## 2. What I judged by eye (contact sheet at 12 fps)", ""]
    out += [f"- {n}" for n in notes["eye"]]
    out += ["", "## 3. What is not perfect", ""]
    out += [f"- {n}" for n in notes["weak"]]
    out += ["", "## 4. Score breakdown", "", "| Axis | Score | Why |", "|---|---|---|"]
    for axis, val, why in notes["axes"]:
        out.append(f"| {axis} | {val} | {why} |")
    out += ["", f"**Total {score['score']} / 10.** Publishable as-is; the gaps above are disclosed in the "
                "publishing kit and the pinned comment rather than hidden.", ""]
    return "\n".join(out)


def plain_kit(md: str) -> str:
    """Markdown -> paste-friendly text for YouTube's description box."""
    txt = md
    txt = re.sub(r"^#{1,6} ", "", txt, flags=re.M)
    txt = re.sub(r"\*\*(.+?)\*\*", r"\1", txt)
    txt = re.sub(r"`([^`]+)`", r"\1", txt)
    txt = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", txt)
    txt = re.sub(r"^\s*\|.*\|\s*$", "", txt, flags=re.M)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip() + "\n"


SCORES = {
    "DS-005": {
        "date": "2026-11-07",
        "score": 8.8,
        "notes": {
            "eye": [
                "Frame 1 opens on the star with its companion already mid-orbit — the most striking moving image in the episode, no title card first.",
                "The `star_wake` disc visibly deforms as the companion crosses maximum separation, which is exactly what the VLA/ALMA ellipticity measurement shows. The visual argument matches the narration.",
                "The counter slams from 12 → 700 R☉ and 300 → 2,100 D with real numeral roll, so the biggest numbers are the only thing moving in those beats.",
                "Contact sheet reads as one film: orange photosphere, cyan HUD, identical type stack, no shot that looks like a different channel.",
            ],
            "weak": [
                "The companion is drawn oversized relative to a true 2 R☉ / ~1 R★ mass-ratio pair so it survives a 1080-wide frame. Disclosed on screen as `SEPARATION ≈ 2 R☉`, which is the real figure, but the dot itself is illustrative.",
                "The 2,100-day cycle is a 2024 *proposed* period. The narration says \"if the model holds\"; the counter slider cannot carry that nuance, so the pinned comment repeats it.",
                "No real telescope imagery in the episode: the VLA/ALMA radio maps are not public-domain, and a real map would have been the honest anchor. Everything is animation, disclosed in the kit.",
                "Whisper transcription check was skipped (weights unreachable), so caption accuracy is authored-timing only, not ASR-verified.",
            ],
            "axes": [
                ("Hook", "9", "Opens inside the story (a star with a passenger), not on a title or a logo."),
                ("Accuracy", "9", "Every number is traceable; the two soft claims (2,100-day period, companion size in frame) are hedged in narration and disclosed here."),
                ("Visual craft", "9", "Continuous 3D motion, a new image every 1.67 s on average, zero still frames."),
                ("Sound", "8", "−14.0 LUFS / −1.49 dBTP, voice dominates, but the score is synthesized from a GM soundfont and is functional rather than memorable."),
                ("Retention design", "9", "Number slams at 7.9, 21.6, 31.0 and 39.0 s; the loop returns to the opening frame."),
                ("Packaging", "9", "Cover is a four-line shout with a ringed companion and a 2,100 badge; titles are curiosity-gap, not spoilers."),
            ],
        },
    },
    "DS-006": {
        "date": "2026-11-07",
        "score": 8.9,
        "notes": {
            "eye": [
                "Frame 1 is the muon track already slicing through a detector it is too small to see — motion, scale and mystery in one image.",
                "The Cherenkov cone expands *after* the interaction point, so the moment of detection is a visible event rather than a static diagram.",
                "220 PeV and 30× arrive as separate number slams, so the two facts that make the story land each get their own beat.",
                "The loop closes on \"a crack in physics\" cutting straight back to the particle crossing the sea.",
            ],
            "weak": [
                "The detector is drawn as 8 strings of 9 modules; the real ARCA grid is 230 m × 700 m with 100 m string spacing and ~200,000 PMTs. The geometry is illustrative, the labels are real.",
                "The 3σ tension with IceCube is stated as a disagreement, not as proof of new physics. The narration offers \"either lucky, or missing physics\" — that is the honest framing.",
                "The energy counter starts at 7 PeV (the old record) which is a narrative device, not a measured intermediate value.",
                "Whisper transcription check skipped (weights unreachable).",
            ],
            "axes": [
                ("Hook", "9", "First frame is the impossible image; first line is the impossible sentence."),
                ("Accuracy", "9", "Nature DOI, 90 % credible interval and the tension citation are all in the sources file; no invented physics."),
                ("Visual craft", "9", "New scene geometry built for this episode; additive glow, depth-sorted tubes, no borrowed clip art."),
                ("Sound", "8", "Clean and on target, but the score is a synthesised bed rather than a composed cue."),
                ("Retention design", "9", "33 s of the run is numbers, claims and reversals; nothing sits still longer than 2.4 s."),
                ("Packaging", "9", "Cover: \"1 PARTICLE / 220 PeV / SHOULD NOT EXIST\" with a 30× badge — three hooks stacked, still readable at 320 px."),
            ],
        },
    },
    "DS-007": {
        "date": "2026-11-07",
        "score": 8.7,
        "notes": {
            "eye": [
                "Frame 1 is the amoeba already on the olfactory nerve, halfway to the brain, before a single word is spoken.",
                "The `nerve_invasion` scene animates the actual route — nasal cavity, cribriform plate, nerve bundle, bulb — so the anatomy is the story, not decoration.",
                "Counters land 167 → 4 and 0 → 97 %, which is the whole episode in two beats.",
                "Loop: \"it begins as a headache\" cuts back to the organism entering the nose.",
            ],
            "weak": [
                "Every number follows CDC wording, which means the episode under-claims on purpose: \"above ninety seven percent\" rather than a clean 99 %, and \"one hundred sixty seven cases\" rather than \"about 200\".",
                "The 2016 survivor is named only by age and state in the narration; the pinned comment names him, because the case is public and widely reported.",
                "The organisms are drawn as comma-shaped trophozoites at a scale that would be enormous next to a real 10–25 µm cell. Illustrative, not to scale — no on-screen claim says otherwise.",
                "Whisper transcription check skipped (weights unreachable).",
            ],
            "axes": [
                ("Hook", "9", "Highest-stakes first line in the series so far, and the image supports it immediately."),
                ("Accuracy", "9", "CDC + NCBI Bookshelf only; the temptation to say 99 % or 'flesh-eating' was refused."),
                ("Visual craft", "8", "The nerve scene carries the episode; the two `mirror_colony` beats are less specific to this topic than the rest."),
                ("Sound", "8", "On target, functional score."),
                ("Retention design", "9", "Survivor reveal at 36 s gives the video a second act instead of a single doom beat."),
                ("Packaging", "9", "Cover: \"IT EATS YOUR BRAIN IN 5 DAYS\" + 4/167 badge. Aggressive without inventing a single fact."),
            ],
        },
    },
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()
    proj = Path(args.project)
    if not proj.is_absolute():
        proj = ROOT / proj
    vid = proj.name

    sp = spec(proj)
    (proj / "script_spec.json").write_text(json.dumps(sp, indent=2), encoding="utf-8")

    if vid in SCORES:
        (proj / "qa_selfreview.md").write_text(selfreview(proj, SCORES[vid]), encoding="utf-8")

    kit = proj / "publishing_kit.md"
    if kit.exists():
        (proj / "publishing_kit.txt").write_text(plain_kit(kit.read_text()), encoding="utf-8")

    print(f"[docgen] {vid}: {sp['word_count']} words, {sp['duration_s']} s, {sp['wpm']} wpm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
