#!/usr/bin/env python3
"""Deterministic, offline-capable Kokoro-82M v1.0 ONNX TTS + studio mastering for Small Signal Studio.

Bootstraps weights from npm (`kokoro-q8-shards@1.0.0` + `kokoro-js@1.2.1`) into /tmp/kokoro-tts
if not already unpacked, so any brand-new session can recreate the exact chosen voice from Voice.txt
without API keys, Hugging Face tokens, or session-bound voice IDs.
"""
from __future__ import annotations

import argparse
import glob
import os
import subprocess
import numpy as np
import soundfile as sf

CACHE_DIR = "/tmp/kokoro-tts"
MODEL_PATH = os.path.join(CACHE_DIR, "kokoro-v1.0.q8.onnx")
VOICES_NPZ = os.path.join(CACHE_DIR, "voices-v1.0.npz")


def ensure_kokoro_assets() -> tuple[str, str]:
    os.makedirs(CACHE_DIR, exist_ok=True)
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VOICES_NPZ):
        subprocess.run(
            ["npm", "pack", "kokoro-q8-shards@1.0.0", "kokoro-js@1.2.1"],
            cwd=CACHE_DIR,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        q8_dir = os.path.join(CACHE_DIR, "unpacked_q8")
        js_dir = os.path.join(CACHE_DIR, "unpacked_js")
        os.makedirs(q8_dir, exist_ok=True)
        os.makedirs(js_dir, exist_ok=True)
        q8_tgz = sorted(glob.glob(os.path.join(CACHE_DIR, "kokoro-q8-shards-*.tgz")))[0]
        js_tgz = sorted(glob.glob(os.path.join(CACHE_DIR, "kokoro-js-*.tgz")))[0]
        subprocess.run(["tar", "-xzf", q8_tgz, "-C", q8_dir], check=True)
        subprocess.run(["tar", "-xzf", js_tgz, "-C", js_dir], check=True)

        parts = sorted(glob.glob(os.path.join(q8_dir, "package", "kokoro-q8.part*.bin")))
        with open(MODEL_PATH, "wb") as out:
            for part in parts:
                with open(part, "rb") as inp:
                    out.write(inp.read())

        voices = {}
        for p in sorted(glob.glob(os.path.join(js_dir, "package", "voices", "*.bin"))):
            name = os.path.splitext(os.path.basename(p))[0]
            voices[name] = np.fromfile(p, dtype=np.float32).reshape(-1, 1, 256)
        # Deterministic custom cinematic blend: 65% am_onyx + 35% am_fenrir
        if "am_onyx" in voices and "am_fenrir" in voices:
            voices["am_onyx_fenrir_65_35"] = (
                0.65 * voices["am_onyx"] + 0.35 * voices["am_fenrir"]
            ).astype(np.float32)
        np.savez(VOICES_NPZ, **voices)
    else:
        data = dict(np.load(VOICES_NPZ))
        if "am_onyx_fenrir_65_35" not in data and "am_onyx" in data and "am_fenrir" in data:
            data["am_onyx_fenrir_65_35"] = (
                0.65 * data["am_onyx"] + 0.35 * data["am_fenrir"]
            ).astype(np.float32)
            np.savez(VOICES_NPZ, **data)
    return MODEL_PATH, VOICES_NPZ


def synthesize(
    text: str,
    voice: str,
    lang: str,
    speed: float,
    out_path: str,
    af_chain: str,
) -> None:
    from kokoro_onnx import Kokoro

    model_path, voices_path = ensure_kokoro_assets()
    kokoro = Kokoro(model_path, voices_path)
    samples, sr = kokoro.create(text, voice=voice, speed=speed, lang=lang)
    raw_wav = out_path + ".raw.wav"
    sf.write(raw_wav, samples, sr)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", raw_wav,
        "-af", af_chain,
        "-ar", "48000", "-ac", "2",
    ]
    if out_path.lower().endswith(".mp3"):
        cmd += ["-c:a", "libmp3lame", "-b:a", "192k"]
    else:
        cmd += ["-c:a", "pcm_s16le"]
    cmd.append(out_path)
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(raw_wav)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--voice", required=True)
    parser.add_argument("--lang", default="en-us")
    parser.add_argument("--speed", type=float, default=0.95)
    parser.add_argument(
        "--af",
        default="highpass=f=65,equalizer=f=125:t=q:w=1.1:g=2.2,equalizer=f=3400:t=q:w=1.4:g=1.4,loudnorm=I=-16:TP=-1.5:LRA=9",
    )
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    synthesize(args.text, args.voice, args.lang, args.speed, args.out, args.af)


if __name__ == "__main__":
    main()
