#!/usr/bin/env python3
"""
SHORTS-2026-024-Binance-63B — REVISION 3 audio engine (2D explainer + host).

Revision 3 replaces the march with a documentary explainer bed and re-times the
film around a new teacher-style VO.

  1. Timeline   - measures the 10 VO clips, applies `atempo`, lays them out with
                  a lead-in + inter-clip gaps, and derives the film length from
                  the result (the length is no longer hard-coded).
  2. Score      - 92 BPM documentary bed: warm pad, plucked arpeggio, soft
                  kick, rim clicks, hats, sub accents. Five sections that follow
                  the story (hook drone -> bed -> full -> tense -> payoff).
  3. SFX        - riser, coin pour, freeze, glitch, sub boom, triggered off VO.
  4. Mix        - music ducked -6 dB under voice (50 ms attack / 250 ms
                  release), SFX peaking at -12 dBFS, loudnorm to -14 LUFS.
  5. Exports    - audio/timing.json, audio/mouth.json (per-frame VO energy for
                  the host's lip sync) and src/data/shorts024Timeline.ts.

Everything is synthesised with numpy; no external audio assets.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shorts024_audio as eng                      # DSP helpers + SFX makers

SR = eng.SR                                        # 44100
FPS = 30

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
ATEMPO = 1.06          # teacher pace: unhurried but never draggy
LEAD_IN = 0.60         # silence before the hook
GAP = 0.20             # breath between lines
TAIL = 1.20            # bed after the last line

ROOT = eng.ROOT
AUDIO = eng.AUDIO
TMP = os.path.join(AUDIO, "_tmp3")
FFMPEG = eng.FFMPEG

# VO clips in script order, with the SFX that fires on each clip's start and
# the on-screen caption chunks (w = relative weight, used to split the caption
# timing inside a clip).
CLIPS = [
    {"id": "L1", "file": "vo3_l1.wav", "sfx": ["riser"],
     "caps": [("20 MINUTES", 3), ("$6.3 BILLION GONE", 6)]},
    {"id": "B1", "file": "vo3_b1.wav", "sfx": [],
     "caps": [("A BANK", 4), ("FOR DIGITAL MONEY", 6)]},
    {"id": "B1b", "file": "vo3_b1b.wav", "sfx": [],
     "caps": [("THE HOT WALLET", 5), ("ALWAYS ONLINE", 5)]},
    {"id": "B2a", "file": "vo3_b2a.wav", "sfx": ["coin_pour"],
     "caps": [("29 OCT · 20:05 UTC", 6), ("10 BLOCKCHAINS", 5)]},
    {"id": "B2b", "file": "vo3_b2b.wav", "sfx": [],
     "caps": [("18,270 BTC", 5), ("NOBODY CAN FREEZE IT", 6)]},
    {"id": "B2c", "file": "vo3_b2c.wav", "sfx": ["freeze"],
     "caps": [("$3B FROZEN", 5), ("$2.4B GONE", 5)]},
    {"id": "B3", "file": "vo3_b3.wav", "sfx": ["glitch"],
     "caps": [("SO HOW?", 2), ("THE VAULT WAS NEVER BROKEN", 6),
              ("A FAKE JOB INTERVIEW", 5), ("THE CODE TEST WAS MALWARE", 6)]},
    {"id": "B3c", "file": "vo3_b3c.wav", "sfx": [],
     "caps": [("ONE LAPTOP", 4), ("ONE CLICK", 3), ("THE KEYS TO EVERYTHING", 6)]},
    {"id": "P1", "file": "vo3_p1.wav", "sfx": [],
     "caps": [("EVERY DOLLAR REPAID", 5), ("WITHDRAWALS REOPENED", 5),
              ("FBI · TRADERTRAITOR", 6)]},
    {"id": "P2", "file": "vo3_p2.wav", "sfx": ["boom"],
     "caps": [("LARGEST CRYPTO THEFT EVER", 6), ("4× THE OLD RECORD", 4),
              ("SOMEBODY ASKED FOR THE KEYS", 6)]},
]

# ----------------------------------------------------------------------------
# Score — 92 BPM documentary bed
# ----------------------------------------------------------------------------
NOTE = eng.NOTE
PROGRESSION = [                       # D minor: i - VI - III - VII
    ("Dm", ["D2", "D3", "F3", "A3"]),
    ("Bb", ["Bb2", "D3", "F3", "Bb3"]),
    ("F",  ["C3", "F3", "A3", "C4"]),
    ("C",  ["C3", "E3", "G3", "C4"]),
]
# sparse arpeggio pattern over the bar (in chord-voice indices, None = rest)
ARP = [0, 2, 1, 3, 2, 1, 3, 2]


def pad(freqs: list[float], dur: float, gain: float = 1.0) -> np.ndarray:
    """Warm sustained pad: detuned sines, slow attack, lowpassed."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for i, f in enumerate(freqs):
        for det, amp in ((-0.6, 1.0), (0.0, 0.8), (0.7, 0.6)):
            sig += amp * np.sin(2 * np.pi * (f + det) * t)
    sig /= len(freqs) * 2.4
    env = eng.adsr(n, 0.28, 0.20, 0.85, 0.30)
    sig = eng.onepole_lp(sig * env, 1800.0)
    return sig * gain


def pluck(freq: float, dur: float, gain: float = 1.0) -> np.ndarray:
    """Short triangular pluck for the arpeggio."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for h, a in ((1, 1.0), (2, 0.34), (3, 0.14), (4, 0.06)):
        sig += a * np.sin(2 * np.pi * freq * h * t)
    sig /= 1.54
    return sig * np.exp(-t / (dur * 0.42)) * eng.adsr(n, 0.004, 0.02, 0.5, 0.05) * gain


def rim(dur: float = 0.09) -> np.ndarray:
    """Rim click — the bed's backbeat, much softer than a march snare."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(23)
    noise = eng.band(rng.normal(0, 1, n), 1400, 8000) * np.exp(-t / 0.012)
    tone = np.sin(2 * np.pi * 420 * t) * np.exp(-t / 0.010) * 0.5
    return (noise * 0.7 + tone) * 0.55


def soft_kick(dur: float = 0.30) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 52.0 + 60.0 * np.exp(-t / 0.040)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.14)
    return body * 0.75


def sub_hit(freq: float = 55.0, dur: float = 1.1) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.45) * 0.6


def build_score(total_seconds: float) -> np.ndarray:
    bpm = 92.0
    beat = 60.0 / bpm                 # 0.652 s
    bar = beat * 4                    # 2.609 s
    out = np.zeros(int(total_seconds * SR))

    kick_s, rim_s = soft_kick(), rim()
    hat_s = eng.hat()
    n_bars = int(total_seconds / bar) + 1
    last = n_bars - 1

    def section(bar_i: int) -> tuple[bool, bool, bool]:
        """(drums, arpeggio, sub accents) per bar."""
        t = bar_i * bar
        if t < 7.0:
            return (False, False, True)      # hook: drone + one sub swell
        if t < 20.0:
            return (True, True, False)       # bed enters
        if t < 41.0:
            return (True, True, True)        # full
        if t < 53.0:
            return (True, False, True)       # tense: no arpeggio
        return (True, True, True)            # payoff

    for b in range(n_bars):
        t0 = b * bar
        if t0 >= total_seconds:
            break
        drums, arp, subs = section(b)
        name, chord = PROGRESSION[b % 4]

        # pad — always present, louder as the film opens up
        g = 0.16 if b == 0 else (0.22 if t0 < 20 else 0.30)
        place_bar = pad([NOTE[f] for f in chord], min(bar + 0.25, total_seconds - t0), g)
        eng.place(out, place_bar, t0)

        if drums:
            for k in range(4):
                if k in (0, 2):
                    eng.place(out, kick_s * (1.0 if k == 0 else 0.72), t0 + k * beat)
                else:
                    eng.place(out, rim_s * 0.8, t0 + k * beat)
            for e in range(8):
                eng.place(out, hat_s * (0.42 if e % 2 == 0 else 0.26),
                          t0 + e * beat / 2)
        elif b == 0:
            eng.place(out, sub_hit(58.0, 1.4) * 0.9, 0.0)

        if arp:
            for s in range(8):
                idx = ARP[(b * 8 + s) % len(ARP)]
                f = chord[min(idx, len(chord) - 1)] if s % 2 == 0 else chord[idx]
                eng.place(out, pluck(NOTE[f] * 2.0, beat * 0.55, 0.16),
                          t0 + s * beat / 2)
            # a quiet upper-octave answer note on the last 8th
            eng.place(out, pluck(NOTE[chord[3]] * 2.0, beat * 0.5, 0.11),
                      t0 + beat * 3.5)

        if subs and b % 2 == 0:
            eng.place(out, sub_hit(58.0, 1.0) * 0.55, t0)

    # final bar: warm unison swell then decay
    end = max(0.0, total_seconds - 2.4)
    for f, g in (("D2", 0.42), ("A2", 0.30), ("D3", 0.26), ("F3", 0.20)):
        eng.place(out, pad([NOTE[f]], 2.3, g), end)
    eng.place(out, sub_hit(48.0, 1.8) * 0.6, end)

    return np.tanh(out * 1.05) * 0.9


# ----------------------------------------------------------------------------
# Timeline
# ----------------------------------------------------------------------------
def build_timeline() -> list[dict]:
    os.makedirs(TMP, exist_ok=True)
    t = LEAD_IN
    timeline = []
    for c in CLIPS:
        src = os.path.join(AUDIO, c["file"])
        raw = eng.wav_duration(src)
        dst = os.path.join(TMP, c["file"])
        eng.time_stretch(src, dst, ATEMPO)
        dur = raw / ATEMPO
        caps = []
        wsum = sum(w for _, w in c["caps"]) or 1
        ct = 0.0
        for text, w in c["caps"]:
            cd = dur * (w / wsum)
            caps.append({"text": text,
                         "start": round(c["start"] if False else t + ct, 4),
                         "end": round(t + ct + cd, 4),
                         "startFrame": int(round((t + ct) * FPS)),
                         "endFrame": int(round((t + ct + cd) * FPS))})
            ct += cd
        timeline.append({
            "id": c["id"], "file": c["file"], "sfx": c["sfx"],
            "start": round(t, 4), "end": round(t + dur, 4),
            "duration": round(dur, 4), "raw_duration": round(raw, 4),
            "startFrame": int(round(t * FPS)), "endFrame": int(round((t + dur) * FPS)),
            "captions": caps,
        })
        t += dur + GAP
    return timeline


def mouth_envelope(vo: np.ndarray, total_frames: int) -> list[int]:
    """Per-frame VO energy, 0-100, for the host's mouth animation."""
    win = int(SR / FPS)
    env = np.zeros(total_frames)
    for f in range(total_frames):
        a, b = f * win, (f + 1) * win
        if a >= len(vo):
            break
        seg = vo[a:min(b, len(vo))]
        if len(seg):
            env[f] = math.sqrt(float(np.mean(seg ** 2)))
    # normalise on the 92nd percentile so loud words reach ~100
    nz = env[env > 0]
    ref = float(np.percentile(nz, 92)) if len(nz) else 1.0
    env = np.clip(env / (ref or 1.0), 0.0, 1.0)
    # smooth: 60 ms attack, 120 ms release
    atk = 1.0 - math.exp(-1.0 / (0.060 * FPS))
    rel = 1.0 - math.exp(-1.0 / (0.120 * FPS))
    val = 0.0
    out = []
    for v in env:
        k = atk if v > val else rel
        val += k * (v - val)
        out.append(int(round(min(1.0, val ** 0.7) * 100)))
    return out


def write_timeline_ts(timeline: list[dict], total_frames: int,
                      total_seconds: float) -> None:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "src", "data", "shorts024Timeline.ts")
    path = os.path.abspath(path)
    lines = [
        "// AUTO-GENERATED by scripts/shorts024_audio_rev3.py — do not edit.",
        "// SHORTS-2026-024-Binance-63B revision 3 (2D explainer + host).",
        "",
        "export type Rev3Caption = {",
        "  text: string;",
        "  startFrame: number;",
        "  endFrame: number;",
        "};",
        "",
        "export type Rev3Clip = {",
        "  id: string;",
        "  startFrame: number;",
        "  endFrame: number;",
        "  captions: Rev3Caption[];",
        "};",
        "",
        f"export const REV3_FPS = {FPS};",
        f"export const REV3_DURATION = {total_frames};",
        f"export const REV3_SECONDS = {round(total_seconds, 2)};",
        "",
        "export const REV3_CLIPS: Rev3Clip[] = [",
    ]
    for c in timeline:
        lines.append("  {")
        lines.append(f"    id: '{c['id']}',")
        lines.append(f"    startFrame: {c['startFrame']},")
        lines.append(f"    endFrame: {c['endFrame']},")
        lines.append("    captions: [")
        for cap in c["captions"]:
            lines.append(f"      {{text: {json.dumps(cap['text'])}, "
                         f"startFrame: {cap['startFrame']}, "
                         f"endFrame: {cap['endFrame']}}},")
        lines.append("    ],")
        lines.append("  },")
    lines.append("];")
    lines.append("")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines))


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main() -> int:
    os.makedirs(AUDIO, exist_ok=True)
    print(f"[1/7] timeline  (atempo={ATEMPO}, lead={LEAD_IN}s, gap={GAP}s)")
    timeline = build_timeline()
    for c in timeline:
        print(f"      {c['id']:>4}  {c['start']:6.2f}s -> {c['end']:6.2f}s "
              f"({c['startFrame']:4d}-{c['endFrame']:4d}f)  {c['file']}")
    vo_end = timeline[-1]["end"]
    total_seconds = math.ceil((vo_end + TAIL) * 2) / 2       # round up to 0.5 s
    total_frames = int(round(total_seconds * FPS))
    print(f"      VO ends at {vo_end:.2f}s -> film {total_seconds:.2f}s "
          f"/ {total_frames} frames")

    print("[2/7] score (92 BPM documentary bed)")
    music = eng.norm_rms(build_score(total_seconds), -18.0)
    eng.write_wav(os.path.join(AUDIO, "music3.wav"), music)

    print("[3/7] sfx")
    bed = np.zeros(int(total_seconds * SR))
    sfx_log = []
    for c in timeline:
        for name in c["sfx"]:
            maker, dur = eng.SFX_MAKERS[name]
            sig = eng.norm_peak(maker(dur), -12.0)
            at = max(0.0, c["start"] - (0.18 if name == "riser" else 0.02))
            eng.place(bed, sig, at)
            sfx_log.append({"name": name, "at": round(at, 3), "dur": dur,
                            "clip": c["id"]})
    eng.write_wav(os.path.join(AUDIO, "sfx3.wav"), bed)

    print("[4/7] vo")
    vo = np.zeros(int(total_seconds * SR))
    for c in timeline:
        x = eng.load_mono(os.path.join(TMP, c["file"]))
        eng.place(vo, x, c["start"])
        fi = int(0.008 * SR)
        i = int(c["start"] * SR)
        if i + fi < len(vo):
            vo[i:i + fi] *= np.linspace(0, 1, fi)
            j = i + len(x)
            if j - fi > 0 and j <= len(vo):
                vo[j - fi:j] *= np.linspace(1, 0, fi)
    eng.write_wav(os.path.join(AUDIO, "vo3.wav"), vo)

    print("[5/7] lip-sync envelope")
    env = mouth_envelope(vo, total_frames)
    with open(os.path.join(AUDIO, "mouth.json"), "w") as f:
        json.dump({"fps": FPS, "frames": total_frames, "env": env}, f)
    mpath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "..", "src", "data", "shorts024Mouth.ts"))
    wrapped = ",\n  ".join(
        ", ".join(str(v) for v in env[i:i + 30]) for i in range(0, len(env), 30))
    with open(mpath, "w") as f:
        f.write("// AUTO-GENERATED by scripts/shorts024_audio_rev3.py — do not edit.\n"
                "// Per-frame voice energy (0-100) driving the host's mouth.\n"
                "export const REV3_MOUTH: number[] = [\n  " + wrapped + ",\n];\n")

    print("[6/7] mix (ducking -6 dB under voice)")
    gain = 10 ** ((-6.0 / 20.0) * eng.duck_envelope(timeline, total_seconds))
    mix = vo + music * gain + bed
    mix = np.tanh(mix * 0.85) / math.tanh(0.85) * 0.92
    eng.write_wav(os.path.join(AUDIO, "mix3.wav"), mix)
    eng.loudnorm(os.path.join(AUDIO, "mix3.wav"), os.path.join(AUDIO, "final3.wav"))

    print("[7/7] exports")
    with open(os.path.join(AUDIO, "timing3.json"), "w") as f:
        json.dump({
            "fps": FPS, "total_frames": total_frames,
            "total_seconds": round(total_seconds, 3),
            "atempo": ATEMPO, "lead_in": LEAD_IN, "gap": GAP,
            "vo_end": round(vo_end, 3),
            "clips": timeline, "sfx": sfx_log,
        }, f, indent=2)
    write_timeline_ts(timeline, total_frames, total_seconds)
    print("      wrote timing3.json, mouth.json, src/data/shorts024Timeline.ts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
