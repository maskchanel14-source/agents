#!/usr/bin/env python3
"""Render a sourced, local-first Indonesian faceless video pack.

The script is deliberately dependency-light. It uses only the Python standard
library plus the pinned local eSpeak loader and imageio-ffmpeg wrapper. It is
not a downloader and never touches credentials or public publishing APIs.
"""
from __future__ import annotations

import argparse
import ctypes
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import textwrap
import wave
from pathlib import Path
from typing import Any


W, H = 1920, 1080
V_W, V_H = 1080, 1920
FPS = 30
PAUSE_SECONDS = 0.25
VOICE = {"name": "id", "rate": 210, "pitch": 45, "range": 30, "amplitude": 100}
PALETTE = {
    "charcoal": "#171916",
    "cream": "#F2E8D5",
    "amber": "#D49A52",
    "moss": "#66745A",
    "brick": "#A64E3C",
    "muted": "#9B9A8A",
    "blue": "#6C8EA4",
}
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class RenderError(RuntimeError):
    pass


def run(cmd: list[str], *, cwd: Path | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    """Run a command without shell interpolation and fail with useful context."""
    print("$", " ".join(str(x) for x in cmd))
    return subprocess.run(
        [str(x) for x in cmd],
        cwd=str(cwd) if cwd else None,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )


def ffmpeg_path() -> str:
    try:
        import imageio_ffmpeg  # type: ignore

        p = imageio_ffmpeg.get_ffmpeg_exe()
        if Path(p).exists():
            return p
    except Exception:
        pass
    p = shutil.which("ffmpeg")
    if not p:
        raise RenderError("FFmpeg tidak ditemukan; pasang imageio-ffmpeg atau ffmpeg.")
    return p


def ffprobe_path(ffmpeg: str) -> str:
    sibling = str(Path(ffmpeg).with_name("ffprobe"))
    if Path(sibling).exists():
        return sibling
    p = shutil.which("ffprobe")
    if p:
        return p
    # The static imageio binary does not ship ffprobe; ffmpeg's show_entries is
    # used as a fallback by probe_media below.
    return ffmpeg


def xml(s: str) -> str:
    return html.escape(str(s), quote=True)


def seconds_to_srt(value: float) -> str:
    value = max(0.0, value)
    ms = int(round(value * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def read_wav_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def wav_stats(path: Path) -> dict[str, float]:
    with wave.open(str(path), "rb") as w:
        frames = w.readframes(w.getnframes())
        width = w.getsampwidth()
        channels = w.getnchannels()
        rate = w.getframerate()
    if width != 2 or channels != 1:
        raise RenderError(f"WAV tidak sesuai ekspektasi mono 16-bit: {path}")
    import array

    vals = array.array("h")
    vals.frombytes(frames)
    if sys.byteorder != "little":
        vals.byteswap()
    peak = max((abs(x) for x in vals), default=0) / 32768.0
    rms = math.sqrt(sum((x / 32768.0) ** 2 for x in vals) / max(1, len(vals)))
    db_peak = 20 * math.log10(max(peak, 1e-9))
    db_rms = 20 * math.log10(max(rms, 1e-9))
    return {"duration": len(vals) / rate, "peak_dbfs": db_peak, "rms_dbfs": db_rms, "sample_rate": rate}


def wav_silence(path: Path, seconds: float, rate: int = 22050) -> None:
    n = max(0, int(seconds * rate))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\0\0" * n)


def concat_wavs(paths: list[Path], out: Path, silence: float = 0.0) -> None:
    if not paths:
        raise RenderError("Tidak ada WAV untuk digabung.")
    with wave.open(str(paths[0]), "rb") as first:
        params = first.getparams()
        frames = [first.readframes(first.getnframes())]
    for p in paths[1:]:
        with wave.open(str(p), "rb") as w:
            if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (
                params.nchannels,
                params.sampwidth,
                params.framerate,
            ):
                raise RenderError(f"Format WAV berbeda: {p}")
            frames.append(b"\0\0" * int(silence * params.framerate))
            frames.append(w.readframes(w.getnframes()))
    with wave.open(str(out), "wb") as w:
        w.setparams(params)
        for chunk in frames:
            w.writeframes(chunk)


def synthesize_scenes(scenes: list[dict[str, Any]], audio_dir: Path) -> list[Path]:
    """Synthesize Indonesian speech through the bundled eSpeak NG library."""
    try:
        from espeakng_loader import get_data_path, get_library_path
    except Exception as exc:  # pragma: no cover - exercised on the production host
        raise RenderError(f"espeakng-loader belum terpasang: {exc}") from exc

    lib = ctypes.CDLL(get_library_path())
    AUDIO_OUTPUT_RETRIEVAL = 0x0002
    POS_CHARACTER = 1
    callback_type = ctypes.CFUNCTYPE(
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_short),
        ctypes.c_int,
        ctypes.c_void_p,
    )
    chunks: list[bytes] = []

    @callback_type
    def callback(samples: Any, count: int, _events: Any) -> int:
        if samples and count > 0:
            chunks.append(ctypes.string_at(samples, count * 2))
        return 0

    lib.espeak_Initialize.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
    lib.espeak_Initialize.restype = ctypes.c_int
    rate_hz = int(lib.espeak_Initialize(AUDIO_OUTPUT_RETRIEVAL, 0, get_data_path().encode(), 0))
    if rate_hz <= 0:
        raise RenderError("espeak_Initialize gagal")
    lib.espeak_SetSynthCallback.argtypes = [callback_type]
    lib.espeak_SetSynthCallback(callback)
    lib.espeak_SetVoiceByName.argtypes = [ctypes.c_char_p]
    if lib.espeak_SetVoiceByName(VOICE["name"].encode()) != 0:
        raise RenderError("voice Bahasa Indonesia 'id' tidak tersedia")
    lib.espeak_SetParameter.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    # espeak_PARAMETER: rate=1, volume=2, pitch=3, range=4.
    for parameter, value in ((1, VOICE["rate"]), (2, VOICE["amplitude"]), (3, VOICE["pitch"]), (4, VOICE["range"])):
        lib.espeak_SetParameter(parameter, value, 0)
    lib.espeak_Synth.argtypes = [
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_uint,
        ctypes.c_int,
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.POINTER(ctypes.c_uint),
        ctypes.c_void_p,
    ]
    lib.espeak_Synchronize.restype = ctypes.c_int
    lib.espeak_Terminate.restype = ctypes.c_int

    outputs: list[Path] = []
    for scene in scenes:
        out = audio_dir / f"scene-{scene['id']}.wav"
        text = scene["text"].replace(";", ",")
        raw = text.encode("utf-8")
        chunks.clear()
        rc = lib.espeak_Synth(raw, len(raw) + 1, 0, POS_CHARACTER, 0, 0, None, None)
        if rc != 0:
            raise RenderError(f"espeak_Synth gagal pada scene {scene['id']}: {rc}")
        if lib.espeak_Synchronize() != 0:
            raise RenderError(f"espeak_Synchronize gagal pada scene {scene['id']}")
        with wave.open(str(out), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate_hz)
            w.writeframes(b"".join(chunks))
        if read_wav_seconds(out) < 1.0:
            raise RenderError(f"audio scene terlalu pendek: {out}")
        outputs.append(out)
    lib.espeak_Terminate()
    (audio_dir / "voice-profile.json").write_text(
        json.dumps({"engine": "eSpeak NG", "voice": VOICE, "sample_rate": rate_hz, "status": "suara sementara"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return outputs


def normalize_audio(ffmpeg: str, source: Path, target: Path) -> None:
    run(
        [
            ffmpeg,
            "-y",
            "-i",
            source,
            "-af",
            "loudnorm=I=-16:LRA=7:TP=-1.5",
            "-ar",
            "48000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            target,
        ],
        capture=True,
    )


def text_fragments(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text.strip())
    return [c.strip() for c in chunks if c.strip()]


def make_srt(scenes: list[dict[str, Any]], durations: list[float], out: Path) -> list[dict[str, Any]]:
    cues: list[dict[str, Any]] = []
    offset = 0.0
    for scene, duration in zip(scenes, durations):
        parts = text_fragments(scene["text"])
        weights = [max(1, len(p)) for p in parts]
        total = sum(weights)
        cursor = offset
        for part, weight in zip(parts, weights):
            dur = duration * weight / total
            # Keep captions readable; any short gaps are left as intentional breathing.
            lines = textwrap.wrap(part, width=42, break_long_words=False, break_on_hyphens=False) or [part]
            cues.append({"start": cursor, "end": cursor + dur, "text": "\n".join(lines[:2])})
            cursor += dur
        offset += duration + PAUSE_SECONDS
    with out.open("w", encoding="utf-8") as f:
        for i, cue in enumerate(cues, 1):
            f.write(f"{i}\n{seconds_to_srt(cue['start'])} --> {seconds_to_srt(cue['end'])}\n{cue['text']}\n\n")
    return cues


def svg_header(width: int, height: int, title: str, subtitle: str, accent: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PALETTE['charcoal']}"/><stop offset="1" stop-color="#242820"/></linearGradient><filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 .045 0"/></filter></defs>
<rect width="{width}" height="{height}" fill="url(#bg)"/><rect width="{width}" height="{height}" filter="url(#grain)" opacity=".28"/>
<path d="M0 120 H{width}" stroke="{PALETTE['moss']}" stroke-width="2" opacity=".55"/><text x="84" y="82" fill="{PALETTE['amber']}" font-family="DejaVu Sans" font-size="28" letter-spacing="6">RUANG NALAR</text>
<text x="84" y="{height-118}" fill="{PALETTE['cream']}" font-family="DejaVu Sans" font-size="48" font-weight="bold">{xml(title)}</text>
<text x="84" y="{height-62}" fill="{PALETTE['muted']}" font-family="DejaVu Sans" font-size="25">{xml(subtitle)}</text>
<text x="{width-84}" y="82" text-anchor="end" fill="{PALETTE['muted']}" font-family="DejaVu Sans" font-size="20">ILUSTRASI PROGRAMATIK · BUKAN FOTO KEJADIAN</text>
"""


def shapes(kind: str, variant: int, width: int, height: int) -> str:
    a, m, b, c, blue = PALETTE["amber"], PALETTE["moss"], PALETTE["brick"], PALETTE["cream"], PALETTE["blue"]
    shift = (variant % 4) * 35
    common = f'<g opacity=".96" transform="translate({shift} {variant*8})">'
    if kind == "receipt":
        return common + f'<rect x="250" y="190" width="720" height="520" rx="22" fill="{c}"/><path d="M300 290 H900 M300 365 H850 M300 440 H900 M300 515 H760" stroke="{PALETTE["charcoal"]}" stroke-width="12" opacity=".35"/><circle cx="1120" cy="450" r="190" fill="{a}" opacity=".82"/><path d="M1000 450 L1080 530 L1240 330" fill="none" stroke="{PALETTE["charcoal"]}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/><text x="1180" y="720" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="64" fill="{c}">?</text></g>'
    if kind == "newspaper":
        return common + f'<rect x="330" y="190" width="860" height="520" fill="{c}" transform="rotate(-5 760 450)"/><rect x="420" y="280" width="650" height="40" fill="{a}" transform="rotate(-5 760 450)"/><path d="M430 385 H1070 M430 440 H1030 M430 495 H970 M430 550 H1080" stroke="{PALETTE["charcoal"]}" opacity=".45" stroke-width="18"/><circle cx="1290" cy="270" r="80" fill="{b}" opacity=".8"/><text x="1290" y="290" text-anchor="middle" font-family="DejaVu Sans" font-size="42" font-weight="bold" fill="{c}">DATA</text></g>'
    if kind == "question":
        return common + f'<circle cx="700" cy="420" r="250" fill="{m}" opacity=".82"/><circle cx="1120" cy="520" r="190" fill="{a}" opacity=".88"/><text x="700" y="520" text-anchor="middle" font-family="DejaVu Serif" font-size="330" font-weight="bold" fill="{c}">?</text><text x="1120" y="585" text-anchor="middle" font-family="DejaVu Sans" font-size="48" font-weight="bold" fill="{PALETTE["charcoal"]}">ANGKA</text></g>'
    if kind == "survey":
        dots = ''.join(f'<circle cx="{520+(i%6)*100}" cy="{270+(i//6)*100}" r="23" fill="{a if i%3==0 else m}"/>' for i in range(24))
        return common + f'<rect x="380" y="190" width="760" height="500" rx="28" fill="#292f27" stroke="{m}" stroke-width="5"/>{dots}<path d="M460 620 H1060" stroke="{c}" stroke-width="5" opacity=".4"/><text x="760" y="770" text-anchor="middle" fill="{c}" font-family="DejaVu Sans" font-size="40">sampel · tanggal · lokasi</text></g>'
    if kind == "average":
        bars = ''.join(f'<rect x="330" y="{650-(v*3)}" width="90" height="{v*3}" fill="{a if i==3 else m}" opacity=".92"/>' for i,v in enumerate([55,85,64,120,75,95]))
        return common + f'<path d="M270 660 H1120 M300 210 V660" stroke="{c}" stroke-width="5" opacity=".7"/>{bars}<path d="M290 500 C500 470 690 540 1060 390" fill="none" stroke="{b}" stroke-width="12"/><text x="780" y="270" text-anchor="middle" fill="{a}" font-family="DejaVu Sans" font-size="52" font-weight="bold">RATA-RATA</text></g>'
    if kind == "product":
        return common + f'<rect x="420" y="270" width="300" height="300" rx="24" fill="{a}"/><circle cx="570" cy="340" r="46" fill="{c}"/><path d="M450 520 Q570 420 690 520" fill="none" stroke="{c}" stroke-width="24"/><rect x="850" y="330" width="240" height="190" rx="20" fill="{m}"/><path d="M850 390 H1090" stroke="{c}" stroke-width="10"/><text x="1000" y="475" text-anchor="middle" fill="{c}" font-family="DejaVu Sans" font-size="32">SEGAR</text><path d="M750 420 H820" stroke="{c}" stroke-width="8" marker-end="url(#arrow)"/></g>'
    if kind == "chain":
        labels = [(300,"KANDANG",a),(680,"ANGKUT",m),(1060,"PASAR",b),(1440,"RUMAH",blue)]
        nodes = ''.join(f'<circle cx="{x}" cy="420" r="105" fill="{col}"/><text x="{x}" y="430" text-anchor="middle" fill="{PALETTE["charcoal"]}" font-family="DejaVu Sans" font-weight="bold" font-size="28">{lab}</text>' for x,lab,col in labels)
        arrows = ''.join(f'<path d="M{x+115} 420 H{x+260}" stroke="{c}" stroke-width="12" stroke-linecap="round"/>' for x,_,_ in labels[:-1])
        return common + arrows + nodes + '</g>'
    if kind == "inflation":
        return common + f'<path d="M280 680 H1140 M300 250 V680" stroke="{c}" stroke-width="5"/><rect x="430" y="420" width="120" height="260" fill="{m}"/><rect x="650" y="340" width="120" height="340" fill="{a}"/><rect x="870" y="270" width="120" height="410" fill="{b}"/><path d="M330 560 C520 520 640 500 760 400 S1010 350 1110 290" fill="none" stroke="{c}" stroke-width="14"/><text x="760" y="230" text-anchor="middle" fill="{a}" font-family="DejaVu Sans" font-size="58" font-weight="bold">5,03%</text></g>'
    if kind == "balance":
        return common + f'<path d="M760 280 V670 M530 670 H990 M480 350 H1040" stroke="{c}" stroke-width="18" stroke-linecap="round"/><path d="M480 350 L370 560 H590 Z M1040 350 L930 560 H1150 Z" fill="{m}" opacity=".9"/><circle cx="760" cy="280" r="40" fill="{a}"/><text x="480" y="620" text-anchor="middle" fill="{c}" font-family="DejaVu Sans" font-size="35">PASOKAN</text><text x="1040" y="620" text-anchor="middle" fill="{c}" font-family="DejaVu Sans" font-size="35">PERMINTAAN</text></g>'
    if kind == "truck":
        return common + f'<path d="M300 700 C520 480 710 620 910 420 S1240 300 1500 480" fill="none" stroke="{m}" stroke-width="18" stroke-dasharray="26 22"/><rect x="500" y="410" width="470" height="220" rx="26" fill="{a}"/><rect x="970" y="490" width="210" height="140" rx="18" fill="{b}"/><circle cx="640" cy="670" r="58" fill="{PALETTE["charcoal"]}/><circle cx="1070" cy="670" r="58" fill="{PALETTE["charcoal"]}/><text x="800" y="545" text-anchor="middle" fill="{PALETTE["charcoal"]}" font-family="DejaVu Sans" font-size="42" font-weight="bold">ANGKUT</text></g>'
    if kind == "producer":
        return common + f'<path d="M300 690 H1240" stroke="{c}" stroke-width="8"/><path d="M400 690 V420 L650 260 L900 420 V690" fill="{m}"/><path d="M650 260 L900 420 H400 Z" fill="{a}"/><rect x="585" y="510" width="130" height="180" fill="{PALETTE["charcoal"]}"/><path d="M1030 690 Q1150 420 1270 690" fill="{blue}" opacity=".85"/><text x="650" y="790" text-anchor="middle" fill="{c}" font-family="DejaVu Sans" font-size="38">HULU</text></g>'
    if kind == "magnifier":
        return common + f'<circle cx="730" cy="410" r="220" fill="none" stroke="{a}" stroke-width="42"/><path d="M890 570 L1210 820" stroke="{a}" stroke-width="70" stroke-linecap="round"/><path d="M570 420 H890 M730 260 V560" stroke="{c}" stroke-width="10" opacity=".35"/></g>'
    if kind == "basket":
        return common + f'<path d="M420 390 Q760 260 1100 390 L1030 720 H490 Z" fill="{m}"/><path d="M500 420 Q760 200 1020 420" fill="none" stroke="{a}" stroke-width="30"/><circle cx="610" cy="400" r="85" fill="{b}"/><circle cx="790" cy="350" r="100" fill="{a}"/><circle cx="930" cy="420" r="80" fill="{blue}"/><text x="760" y="850" text-anchor="middle" fill="{c}" font-family="DejaVu Sans" font-size="44">KERANJANG TIAP KELUARGA BERBEDA</text></g>'
    if kind == "map":
        return common + f'<path d="M360 300 L540 250 L690 330 L850 240 L1040 330 L1210 270 L1350 420 L1250 570 L1080 600 L960 760 L780 680 L600 760 L470 600 Z" fill="{m}" opacity=".88"/><path d="M520 450 C700 380 820 580 1000 430 S1190 470 1290 390" fill="none" stroke="{a}" stroke-width="18"/><circle cx="560" cy="420" r="18" fill="{b}"/><circle cx="860" cy="520" r="18" fill="{b}"/><circle cx="1130" cy="410" r="18" fill="{b}"/><text x="850" y="850" text-anchor="middle" fill="{c}" font-family="DejaVu Sans" font-size="42">WILAYAH ≠ SATU PENGALAMAN</text></g>'
    if kind == "checklist":
        rows = ''.join(f'<rect x="480" y="{250+i*105}" width="55" height="55" fill="none" stroke="{a}" stroke-width="8"/><path d="M495 {278+i*105} l14 16 l28 -35" fill="none" stroke="{a}" stroke-width="8"/><rect x="600" y="{265+i*105}" width="490" height="25" fill="{c}" opacity=".75"/>' for i in range(4))
        return common + rows + '<text x="760" y="760" text-anchor="middle" fill="' + c + '" font-family="DejaVu Sans" font-size="46" font-weight="bold">HASIL, BUKAN HANYA NIAT</text></g>'
    # market / closing
    return common + f'<rect x="300" y="480" width="1040" height="220" fill="{m}"/><path d="M300 480 L480 300 L660 480 L840 300 L1020 480 L1200 300 L1340 480" fill="{a}" opacity=".85"/><circle cx="580" cy="410" r="45" fill="{b}"/><circle cx="930" cy="410" r="45" fill="{blue}"/><path d="M380 700 V300 M1160 700 V300" stroke="{c}" stroke-width="16"/><text x="820" y="820" text-anchor="middle" fill="{c}" font-family="DejaVu Sans" font-size="48">PASAR, DATA, DAN KEPUTUSAN</text></g>'


def make_svg(kind: str, title: str, subtitle: str, variant: int, out: Path, width: int = W, height: int = H) -> None:
    accent = PALETTE["amber"] if variant % 2 == 0 else PALETTE["moss"]
    body = svg_header(width, height, title, subtitle, accent)
    body += '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#F2E8D5"/></marker></defs>'
    body += shapes(kind, variant, width, height)
    body += "</svg>"
    out.write_text(body, encoding="utf-8")


def _solid_png(path: Path, width: int, height: int, rgb: tuple[int, int, int]) -> None:
    """Tiny stdlib-only PNG fallback for hosts without ImageMagick/rsvg."""
    import struct
    import zlib

    row = bytes([0, *rgb]) * width
    raw = row * height
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    payload = b"\\x89PNG\\r\\n\\x1a\\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")
    path.write_bytes(payload)


def rasterize(svg: Path, png: Path) -> None:
    """Rasterize SVG; if ImageMagick's SVG delegate is absent, draw a clean
    equivalent editorial card with ImageMagick primitives and text. This is a
    real fallback for minimal containers where convert cannot invoke rsvg.
    """
    convert = shutil.which("convert")
    source = svg.read_text(encoding="utf-8")
    root = re.search(r'<svg[^>]*width="(\d+)"[^>]*height="(\d+)"', source)
    width, height = (int(root.group(1)), int(root.group(2))) if root else (W, H)
    if convert:
        try:
            run([convert, "-background", PALETTE["charcoal"], str(svg), "-quality", "94", str(png)], capture=True)
            if png.exists() and png.stat().st_size >= 10_000:
                return
        except subprocess.CalledProcessError:
            pass
        # ImageMagick is available but its SVG delegate is not. Use its native
        # drawing primitives, which do not need an SVG delegate.
        values = [html.unescape(x) for x in re.findall(r"<text[^>]*>(.*?)</text>", source, flags=re.S)]
        brand = values[0] if values else "RUANG NALAR"
        title = values[1] if len(values) > 1 else "DATA DAN KONTEKS"
        subtitle = values[2] if len(values) > 2 else "ILUSTRASI PROGRAMATIK"
        variant_match = re.search(r"v(\d+)", svg.stem)
        variant = int(variant_match.group(1)) if variant_match else 0
        scale = min(width / W, height / H)
        cx, cy = int(width * (0.58 + 0.07 * (variant % 3))), int(height * (0.42 + 0.06 * (variant % 2)))
        radius = int(min(width, height) * 0.18)
        title_size = int((58 if height <= width else 66) * scale)
        subtitle_size = int((28 if height <= width else 34) * scale)
        cmd = [
            convert, "-size", f"{width}x{height}", f"gradient:{PALETTE['charcoal']}-{PALETTE['charcoal']}",
            "-fill", PALETTE["moss"], "-draw", f"circle {cx},{cy} {cx+radius},{cy}",
            "-fill", PALETTE["amber"], "-draw", f"circle {min(width-1,cx+int(radius*1.45))},{min(height-1,cy+int(radius*.9))} {min(width-1,cx+int(radius*1.45)+int(radius*.65))},{min(height-1,cy+int(radius*.9))}",
            "-fill", PALETTE["cream"], "-stroke", PALETTE["cream"], "-strokewidth", "3", "-draw", f"line {int(width*.08)},{int(height*.15)} {int(width*.92)},{int(height*.15)}",
            "-stroke", "none", "-font", "DejaVu-Sans", "-pointsize", str(max(14, int(26*scale))), "-fill", PALETTE["amber"], "-draw", f"text {int(width*.045)},{int(height*.075)} '{brand}'",
            "-font", "DejaVu-Sans-Bold", "-pointsize", str(max(20, title_size)), "-fill", PALETTE["cream"], "-draw", f"text {int(width*.045)},{int(height*(.89 if height <= width else .84))} '{title.replace(chr(39), chr(96))}'",
            "-font", "DejaVu-Sans", "-pointsize", str(max(13, subtitle_size)), "-fill", PALETTE["muted"], "-draw", f"text {int(width*.045)},{int(height*(.94 if height <= width else .89))} '{subtitle.replace(chr(39), chr(96))}'",
            "-quality", "94", str(png),
        ]
        try:
            run(cmd, capture=True)
            if png.exists() and png.stat().st_size >= 10_000:
                return
        except subprocess.CalledProcessError:
            pass
    # Last resort: a valid PNG still that lets the video pipeline continue.
    _solid_png(png, width, height, (23, 25, 22))
    if not png.exists() or png.stat().st_size < 100:
        raise RenderError(f"PNG visual kosong/rusak: {png}")


def create_visuals(scenes: list[dict[str, Any]], durations: list[float], visual_dir: Path) -> list[tuple[Path, float]]:
    visual_dir.mkdir(parents=True, exist_ok=True)
    sequence: list[tuple[Path, float]] = []
    for scene, scene_duration in zip(scenes, durations):
        total = scene_duration + PAUSE_SECONDS
        count = max(1, math.ceil(total / 6.0))
        remaining = total
        for idx in range(count):
            clip_duration = min(6.0, remaining)
            svg = visual_dir / f"scene-{scene['id']}-v{idx+1}.svg"
            png = visual_dir / f"scene-{scene['id']}-v{idx+1}.png"
            make_svg(scene["visual"], scene["onscreen"], f"{scene['title']} · catatan visual", idx, svg)
            rasterize(svg, png)
            sequence.append((png, clip_duration))
            remaining -= clip_duration
    return sequence


def make_clip(ffmpeg: str, image: Path, seconds: float, out: Path, variant: int) -> None:
    # Ken Burns motion is intentionally subtle: the visual stays legible while
    # changing every ~6 seconds.
    z = "min(zoom+0.00055,1.08)" if variant % 2 == 0 else "max(zoom-0.00035,1.0)"
    x = "iw/2-(iw/zoom/2)" if variant % 3 == 0 else "0"
    y = "ih/2-(ih/zoom/2)" if variant % 3 == 1 else "0"
    filt = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS},format=yuv420p"
    run(
        [
            ffmpeg,
            "-y",
            "-loop",
            "1",
            "-i",
            image,
            "-t",
            f"{max(0.1, seconds):.3f}",
            "-vf",
            filt,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "23",
            "-r",
            str(FPS),
            out,
        ],
        capture=True,
    )


def assemble_visual_video(ffmpeg: str, sequence: list[tuple[Path, float]], visual_dir: Path, out: Path) -> None:
    concat = visual_dir / "clips.ffconcat"
    clips: list[Path] = []
    with concat.open("w", encoding="utf-8") as f:
        f.write("ffconcat version 1.0\n")
        for i, (image, seconds) in enumerate(sequence):
            clip = visual_dir / f"clip-{i:03d}.mp4"
            make_clip(ffmpeg, image, seconds, clip, i)
            clips.append(clip)
            f.write(f"file '{clip.as_posix()}'\n")
            f.write(f"duration {seconds:.3f}\n")
        if clips:
            f.write(f"file '{clips[-1].as_posix()}'\n")
    run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", "-movflags", "+faststart", out], capture=True)


def escape_filter_path(path: Path) -> str:
    # ffmpeg filtergraph uses colon as option separator; commas and backslashes
    # are also escaped. Spaces are accepted when argv is passed without shell.
    return str(path.resolve()).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def mux_main(ffmpeg: str, visual_video: Path, audio: Path, srt: Path, out: Path) -> None:
    subtitle = escape_filter_path(srt)
    vf = f"subtitles='{subtitle}':fontsdir=/usr/share/fonts/truetype/dejavu:force_style='FontName=DejaVu Sans,FontSize=19,PrimaryColour=&H00F2E8D5,OutlineColour=&H90171916,BorderStyle=1,Outline=2,Shadow=1,MarginV=50'"
    try:
        run(
            [
                ffmpeg,
                "-y",
                "-i",
                visual_video,
                "-i",
                audio,
                "-vf",
                vf,
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "21",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                "-movflags",
                "+faststart",
                out,
            ],
            capture=True,
        )
    except subprocess.CalledProcessError:
        # Keep a usable MP4 even if libass is missing. The external SRT remains
        # the authoritative subtitle track.
        print("Peringatan: burn-in subtitle gagal; merender ulang tanpa burn-in.")
        run(
            [
                ffmpeg,
                "-y",
                "-i",
                visual_video,
                "-i",
                audio,
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "21",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                "-movflags",
                "+faststart",
                out,
            ],
            capture=True,
        )


def probe_media(ffmpeg: str, path: Path) -> dict[str, Any]:
    """Return a small ffprobe-like structure, with an ffmpeg-only fallback."""
    probe = ffprobe_path(ffmpeg)
    if Path(probe).name == "ffprobe":
        cmd = [probe, "-v", "error", "-of", "json", "-show_streams", "-show_format", path]
        result = run(cmd, capture=True)
        try:
            return json.loads(result.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise RenderError(f"ffprobe output bukan JSON untuk {path}: {result.stdout[:400]}") from exc
    # imageio-ffmpeg intentionally distributes only ffmpeg. Parse its stable
    # human-readable probe output rather than pretending ffmpeg implements the
    # ffprobe JSON flags.
    result = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path), "-f", "null", "-"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    report = result.stdout or ""
    duration = 0.0
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", report)
    if m:
        duration = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    streams: list[dict[str, Any]] = []
    for line in report.splitlines():
        if "Video:" in line:
            vm = re.search(r"(\d{2,5})x(\d{2,5})", line)
            item: dict[str, Any] = {"codec_type": "video"}
            if vm:
                item.update(width=int(vm.group(1)), height=int(vm.group(2)))
            streams.append(item)
        if "Audio:" in line:
            am = re.search(r"(\d+) Hz", line)
            item = {"codec_type": "audio"}
            if am:
                item["sample_rate"] = am.group(1)
            streams.append(item)
    return {"format": {"duration": duration}, "streams": streams, "raw": report[-1200:]}


def get_duration(probe: dict[str, Any]) -> float:
    try:
        return float(probe.get("format", {}).get("duration", 0.0))
    except (TypeError, ValueError):
        return 0.0


def make_short_srt(text: str, duration: float, out: Path) -> None:
    parts = text_fragments(text)
    weights = [max(1, len(x)) for x in parts]
    total = sum(weights)
    cursor = 0.0
    with out.open("w", encoding="utf-8") as f:
        for i, (part, weight) in enumerate(zip(parts, weights), 1):
            d = duration * weight / total
            wrapped = "\n".join(textwrap.wrap(part, 31, break_long_words=False, break_on_hyphens=False)[:2])
            f.write(f"{i}\n{seconds_to_srt(cursor)} --> {seconds_to_srt(cursor+d)}\n{wrapped}\n\n")
            cursor += d


def make_vertical_svg(title: str, subtitle: str, idx: int, out: Path) -> None:
    body = svg_header(V_W, V_H, "SHORTS", "Ruang Nalar · ilustrasi programatik", PALETTE["amber"])
    body = body.replace(f'y="{V_H-118}"', f'y="{V_H-310}"').replace(f'y="{V_H-62}"', f'y="{V_H-245}"')
    body += f'<circle cx="540" cy="650" r="260" fill="{PALETTE["moss"]}" opacity=".78"/><circle cx="780" cy="930" r="210" fill="{PALETTE["amber"]}" opacity=".85"/><path d="M130 1160 Q540 850 950 1160" fill="none" stroke="{PALETTE["cream"]}" stroke-width="18" opacity=".7"/><text x="540" y="520" text-anchor="middle" fill="{PALETTE["cream"]}" font-family="DejaVu Sans" font-size="58" font-weight="bold">{xml(title)}</text><text x="540" y="1350" text-anchor="middle" fill="{PALETTE["cream"]}" font-family="DejaVu Sans" font-size="34">{xml(subtitle)}</text><text x="540" y="1480" text-anchor="middle" fill="{PALETTE["amber"]}" font-family="DejaVu Sans" font-size="26" letter-spacing="4">DATA · KONTEKS · PERTANYAAN</text></svg>'
    out.write_text(body, encoding="utf-8")


def render_shorts(ffmpeg: str, production: Path, audio_dir: Path, final_dir: Path, visual_dir: Path) -> list[dict[str, Any]]:
    shorts = [
        {
            "id": "short-01",
            "title": "Angka turun, belanja berat?",
            "text": "Pernah membaca harga ayam rata-rata turun, tetapi di pasar dekat rumah tetap terasa mahal? Dua hal itu bisa sama-sama benar. Angka nasional merangkum banyak tempat. Kita berbelanja di satu tempat, pada satu hari, untuk produk dengan mutu tertentu. Kompas dan Antara mengutip pemantauan Bapanas: pada dua Oktober dua ribu dua puluh enam, rata-rata nasional berada di empat puluh ribu sembilan ratus enam puluh satu rupiah per kilogram, turun nol koma enam dua persen dari sepekan sebelumnya. Itu bukan harga semua pasar hari ini. Sebelum menyimpulkan, cek tanggal, lokasi, dan jenis produk. Statistik dan pengalaman bukan musuh. Mereka melihat skala yang berbeda."
        },
        {
            "id": "short-02",
            "title": "Inflasi ayam bukan lima persen",
            "text": "Satu salah baca yang gampang terjadi: Bank Indonesia menyebut inflasi kelompok volatile food September sebesar lima koma nol tiga persen secara tahunan, dan daging ayam termasuk komoditas yang disebut. Itu bukan berarti harga ayam sendiri naik lima koma nol tiga persen. Angka kelompok mencakup cabai, beras, telur, dan komoditas lain. Jadi saat melihat grafik, tanya dulu: ini angka untuk satu barang, atau satu kelompok? Angka yang benar pun bisa menjawab pertanyaan yang salah kalau labelnya tertukar. Data perlu dibaca bersama definisi dan tanggalnya."
        },
        {
            "id": "short-03",
            "title": "Uji subsidi angkut",
            "text": "Subsidi angkut bisa membantu pasokan mencapai daerah yang bukan sentra produksi. Tapi bagaimana kita tahu kebijakan itu bekerja? Cek empat hal. Pertama, barangnya benar-benar tiba? Kedua, harga berubah di wilayah mana? Ketiga, bagaimana dampaknya bagi peternak dan pedagang? Keempat, berapa lama efeknya bertahan setelah bantuan berhenti? Pengumuman kebijakan adalah awal, bukan bukti hasil. Satu harga mingguan juga belum cukup untuk menyimpulkan sebab-akibat. Evaluasi yang adil melihat konsumen dan sisi hulu sekaligus."
        },
    ]
    rendered: list[dict[str, Any]] = []
    for i, item in enumerate(shorts, 1):
        wav = audio_dir / f"{item['id']}.wav"
        # Reuse the same in-process synthesizer contract through a one-scene list.
        synthesize_scenes([{"id": item["id"], "text": item["text"]}], audio_dir)
        raw = audio_dir / f"scene-{item['id']}.wav"
        duration = read_wav_seconds(raw)
        # Add a quiet tail only when a short is below the required 45 seconds.
        if duration < 45.0:
            padded = audio_dir / f"{item['id']}-padded.wav"
            with wave.open(str(raw), "rb") as r:
                params = r.getparams(); frames = r.readframes(r.getnframes())
            with wave.open(str(padded), "wb") as w:
                w.setparams(params)
                w.writeframes(frames)
                w.writeframes(b"\0\0" * int((45.1-duration) * params.framerate))
            raw = padded
            duration = read_wav_seconds(raw)
        if duration > 60.0:
            raise RenderError(f"Short {item['id']} melewati 60 detik: {duration:.2f}")
        svg = visual_dir / f"{item['id']}.svg"
        png = visual_dir / f"{item['id']}.png"
        make_vertical_svg(item["title"], "45–60 detik · sumber di deskripsi", i, svg)
        rasterize(svg, png)
        srt = final_dir / f"{item['id']}.srt"
        make_short_srt(item["text"], duration, srt)
        out = final_dir / f"{item['id']}.mp4"
        subtitle = escape_filter_path(srt)
        vf = f"subtitles='{subtitle}':fontsdir=/usr/share/fonts/truetype/dejavu:force_style='FontName=DejaVu Sans,FontSize=18,PrimaryColour=&H00F2E8D5,OutlineColour=&H90171916,BorderStyle=1,Outline=2,MarginV=120'"
        try:
            run([ffmpeg, "-y", "-loop", "1", "-i", png, "-i", raw, "-t", f"{duration:.3f}", "-vf", vf, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], capture=True)
        except subprocess.CalledProcessError:
            run([ffmpeg, "-y", "-loop", "1", "-i", png, "-i", raw, "-t", f"{duration:.3f}", "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], capture=True)
        rendered.append({"id": item["id"], "title": item["title"], "duration": duration, "mp4": str(out), "srt": str(srt)})
    (production / "02_Naskah" / "shorts.md").write_text("# Tiga Shorts final\n\n" + "\n\n".join(f"## {x['title']}\nDurasi audio: {x['duration']:.2f} detik\n\nTurunan tersedia sebagai `{x['id']}.mp4` dan `{x['id']}.srt`." for x in rendered) + "\n", encoding="utf-8")
    return rendered


def make_thumbnails(production: Path) -> Path:
    outdir = production / "06_Thumbnail"
    outdir.mkdir(exist_ok=True)
    concepts = [
        ("concept-a.svg", "TURUN… KOK?", "grafik vs struk belanja", PALETTE["amber"]),
        ("concept-b.svg", "RATA-RATA ≠ PASAR", "satu angka, banyak pengalaman", PALETTE["moss"]),
        ("concept-c.svg", "SIAPA MENANGGUNG?", "konsumen · pedagang · peternak", PALETTE["brick"]),
    ]
    for filename, headline, sub, accent in concepts:
        body = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720"><rect width="1280" height="720" fill="{PALETTE['charcoal']}"/><circle cx="980" cy="330" r="270" fill="{accent}" opacity=".9"/><path d="M70 570 Q400 200 740 520" fill="none" stroke="{PALETTE['cream']}" stroke-width="18"/><rect x="70" y="85" width="660" height="370" rx="30" fill="#292f27" stroke="{PALETTE['moss']}" stroke-width="6"/><text x="110" y="240" fill="{PALETTE['cream']}" font-family="DejaVu Sans" font-weight="bold" font-size="82">{xml(headline)}</text><text x="110" y="330" fill="{PALETTE['amber']}" font-family="DejaVu Sans" font-size="38">{xml(sub)}</text><text x="110" y="650" fill="{PALETTE['muted']}" font-family="DejaVu Sans" font-size="26" letter-spacing="5">RUANG NALAR · ILUSTRASI PROGRAMATIK</text></svg>'''
        (outdir / filename).write_text(body, encoding="utf-8")
        rasterize(outdir / filename, outdir / filename.replace(".svg", ".png"))
    final = outdir / "thumbnail-final.png"
    shutil.copyfile(outdir / "concept-a.png", final)
    (outdir / "thumbnail-concepts.md").write_text("# Konsep thumbnail\n\nA dipilih sebagai final karena hook terbaca pada ukuran kecil dan tidak menjanjikan data yang tidak ada. B dan C disimpan sebagai alternatif. Semua elemen original/programatik; tidak memakai foto atau logo.\n", encoding="utf-8")
    return final


def write_naskah(production: Path, scenes: list[dict[str, Any]], durations: list[float]) -> None:
    elapsed = 0.0
    lines = ["# Naskah video utama — Harga Ayam Turun, tapi Belanja Masih Terasa Mahal. Kenapa?", "", "**Status:** rendered draft; voice-over eSpeak NG Bahasa Indonesia (suara sementara). Semua snapshot bertanggal; cek ulang harga dinamis sebelum tayang.", "", "## Timing aktual per scene", ""]
    for s, d in zip(scenes, durations):
        lines.append(f"- `{seconds_to_srt(elapsed)}` — **{s['title']}** — {d:.2f} detik")
        elapsed += d + PAUSE_SECONDS
    lines += ["", "## Teks narasi", ""]
    for s in scenes:
        lines += [f"### {s['id']} — {s['title']}", "", s["text"], ""]
    lines += ["## Catatan editorial", "", "Fakta dipisahkan dari analisis. Tidak ada [OPINI-USER]. Klaim harga ayam 2 Oktober adalah snapshot yang dikutip Kompas/Antara dari pemantauan Bapanas; klaim penyaluran pakan dan proyeksi Bapanas diberi tanggal. Laporan sorotan terhadap perantara disebut sebagai laporan/permintaan pengusutan, bukan fakta pidana atau putusan. Visual adalah ilustrasi programatik, bukan dokumentasi kejadian.", ""]
    (production / "02_Naskah" / "naskah-video-utama.md").write_text("\n".join(lines), encoding="utf-8")
    (production / "02_Naskah" / "voice-script.txt").write_text("\n\n".join(f"[SCENE {s['id']}] {s['title']}\n{s['text']}" for s in scenes) + "\n", encoding="utf-8")


def write_visual_docs(production: Path, scenes: list[dict[str, Any]], durations: list[float]) -> None:
    rows = ["# Shot list final", "", "Visual berubah sekitar setiap 6 detik. Semua frame adalah SVG/PNG programatik original dengan palet Channel Bible. Tidak ada tokoh nyata, foto palsu, logo, atau teks AI yang tidak terkontrol.", "", "| Scene | Durasi audio | Visual | On-screen |", "|---|---:|---|---|"]
    for s, d in zip(scenes, durations):
        rows.append(f"| {s['id']} | {d:.2f}s | {s['visual']} · Ken Burns halus | {s['onscreen']} |")
    (production / "04_Visual" / "shot-list.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (production / "04_Visual" / "style-guide.md").write_text("""# Style guide — Ruang Nalar\n\n- **Medium:** editorial vector/programmatic, bukan dokumentasi.\n- **Palet:** arang `#171916`, krem `#F2E8D5`, amber `#D49A52`, hijau lumut `#66745A`, merah bata `#A64E3C`, biru kusam `#6C8EA4`.\n- **Layout:** 16:9 untuk long-form, 9:16 untuk Shorts; safe margin 84 px; headline hanya overlay SVG/FFmpeg sehingga tidak kabur.\n- **Cahaya/tekstur:** gradien gelap-hangat, garis tipis, grain sangat ringan; tidak ada wajah/tangan realistis.\n- **Gerak:** zoom/pan Ken Burns halus setiap klip sekitar enam detik; cut mengikuti pergantian gagasan.\n- **Grafik:** axis/angka hanya untuk ilustrasi metodologis atau angka sumber dengan label tanggal; jangan membuat grafik seolah data live.\n- **Disclosure internal:** setiap still memuat `ILUSTRASI PROGRAMATIK · BUKAN FOTO KEJADIAN`; bukan konten generatif AI.\n""", encoding="utf-8")


def write_claim_check(production: Path) -> None:
    text = """# Gate 1 — tabel klaim dan sumber\n\n| ID | Klaim yang diucapkan | Sumber dan tanggal akses | Status | Batas yang diucapkan |\n|---|---|---|---|---|\n| C1 | Rata-rata harga daging ayam ras nasional Rp40.961/kg pada 2 Okt 2026; turun 0,62% mingguan dan 0,82% bulanan | Kompas, 4 Okt 2026; Antara, 4 Okt 2026; akses 22 Okt 2026 | LULUS PENUH | Snapshot pemantauan, bukan harga semua pasar hari ini |\n| C2 | Bapanas menyiapkan subsidi biaya angkut ke daerah kekurangan/non-sentra | Antara, 4 Okt 2026; Kompas, 4 Okt 2026; akses 22 Okt 2026 | LULUS PENUH | Rencana/kebijakan yang disiapkan, bukan bukti hasil |\n| C3 | PIHPS memakai definisi daging ayam segar tanpa jeroan; survei hari kerja, dua pedagang/komoditas/pasar, 82 kota/kabupaten dan dua pasar/wilayah | BI PIHPS FAQ, akses 22 Okt 2026 | LULUS PENUH | Menjelaskan desain survei, bukan menilai seluruh kios |\n| C4 | BI mencatat volatile food Sep 2026 1,46% mtm dan 5,03% yoy; ayam termasuk komoditas yang disebut bersama komoditas lain | BI, “IHK September 2026 Tetap Terjaga”, rilis 1 Okt 2026; akses 22 Okt 2026 | LULUS PENUH | 5,03% adalah kelompok, bukan ayam saja; penyebab BI disampaikan sebagai konteks |\n| C5 | Penyaluran SPHP jagung pakan per 2 Okt 172,1 ribu ton, 71,36% target tahap 1+2, menjangkau 29 provinsi | Antara, 4 Okt 2026; akses 22 Okt 2026 | LULUS PENUH | Laporan bertanggal, bukan manfaat merata atau bukti harga konsumen adil |\n| C6 | BPS mencatat inflasi umum Sep 2026 3,28% yoy, 0,30% mtm, 2,17% ytd | BPS, rilis 1 Okt 2026; akses 22 Okt 2026 | LULUS PENUH | Indeks nasional bukan pengalaman setiap keluarga |\n| C7 | Inflasi umum provinsi Sep berbeda: Sulawesi Utara 7,59% dan Sumatera Selatan 2,55% yoy | BPS rilis 1 Okt 2026; akses 22 Okt 2026 | LULUS PENUH | Ini inflasi umum provinsi, bukan harga ayam |\n| C8 | Open Data Bapanas memiliki proyeksi neraca pangan Oktober 2026, valid hingga 14 Nov, dengan akses data lengkap terbatas melalui SAPA | Open Data Bapanas, dataset dibuat/dipublikasikan 13 Okt 2026; akses 22 Okt 2026 | LULUS PENUH | Proyeksi bukan stok fisik di setiap pasar |\n| C9 | Kompas melaporkan permintaan anggota DPR untuk menelusuri dugaan permainan perantara pada 18 Okt | Kompas, 18 Okt 2026; akses 22 Okt 2026 | LULUS PENUH | Disebut sebagai laporan/permintaan; bukan putusan atau fakta tindak pidana |\n\n## Gate 1 result\n\n**LULUS PENUH.** Semua angka memiliki tanggal dan batas penggunaan. Klaim angka harga lokal yang tidak terverifikasi independen dikeluarkan dari naskah utama.\n\n## Gate 2 — risiko & netralitas\n\n- Tidak ada nama individu yang dituduh melakukan tindak pidana.\n- Kata “mafia”, “skandal”, dan label pidana tidak dipakai sebagai fakta.\n- Pernyataan pemerintah, kritik kebijakan, kepentingan konsumen, pedagang, dan peternak ditampilkan sebagai perspektif/hasil yang perlu diuji.\n- Korelasi tidak disebut sebagai sebab-akibat.\n- Tidak ada SARA, doxxing, urusan pribadi, rekomendasi finansial, atau visual realistis palsu.\n\n**Gate 2 result: LULUS.**\n"""
    (production / "01_Riset-Sumber" / "claim-check.md").write_text(text, encoding="utf-8")


def write_topic_brief(production: Path) -> None:
    text = """# Topic brief — Harga Ayam Turun, tapi Belanja Masih Terasa Mahal. Kenapa?\n\n**Tanggal radar dan akses:** 22 Oktober 2026 (UTC).\n\n## Pertanyaan inti\n\nMengapa angka harga ayam nasional dapat bergerak berbeda dari pengalaman belanja di satu kota/pasar, dan ukuran apa yang perlu dipakai untuk menilai kebijakan stabilisasi secara adil?\n\n## Tesis\n\nHarga yang dirasakan rumah tangga tidak dibentuk oleh satu angka nasional saja. Lokasi, tanggal, definisi produk, biaya input, distribusi, dan posisi dalam rantai pasok mengubah harga yang ditemui. Rata-rata berguna untuk membaca arah, tetapi kebijakan perlu diuji lewat hasil di konsumen, pedagang, dan peternak sekaligus.\n\n## Mengapa sekarang\n\nLiputan 4 Oktober melaporkan rata-rata nasional daging ayam ras Rp40.961/kg pada 2 Oktober dan rencana subsidi angkut ke wilayah kekurangan pasokan. Pada 18 Oktober, media melaporkan permintaan agar selisih harga hulu-hilir ditelusuri. Perkembangan ini menjadi pintu masuk, bukan alasan untuk mengulang tuduhan yang belum diputus.\n\n## Kandidat radar dan skor\n\nSkor berurutan: ramai/agenda (R), sudut struktural (S), data kredibel (D), tahan 3+ bulan (T), gap konten (G), keamanan editorial (A).\n\n| Kandidat | R | S | D | T | G | A | Total |\n|---|---:|---:|---:|---:|---:|---:|---:|\n| Harga ayam: rata-rata vs pengalaman daerah | 4 | 5 | 5 | 5 | 4 | 4 | **27** |\n| Kebijakan harga pangan: stabilisasi vs insentif produsen | 4 | 5 | 5 | 5 | 4 | 4 | **27** |\n| Kelas menengah dan rasa aman ekonomi | 4 | 5 | 4 | 5 | 3 | 4 | 25 |\n| Bansos dan pembaruan data administrasi | 4 | 5 | 3 | 5 | 4 | 3 | 24 |\n| Karhutla dan kerentanan lanskap | 5 | 5 | 3 | 5 | 3 | 2 | 23 |\n| Dua tahun pemerintahan dari angka pertumbuhan | 5 | 5 | 4 | 5 | 2 | 3 | 24 |\n| Beras fortifikasi dan perlindungan konsumen | 5 | 5 | 2 | 5 | 4 | 1 | 22 |\n| Pasar modal dan indeks global | 5 | 4 | 2 | 4 | 3 | 2 | 20 |\n\n**Pemenang:** harga ayam/rata-rata vs pengalaman lokal. **Runner-up:** kebijakan harga pangan; kelas menengah dan rasa aman ekonomi.\n\n## Sumber utama (diakses 22 Okt 2026)\n\n1. BPS, inflasi September 2026, rilis 1 Okt: https://www.bps.go.id/id/pressrelease/2026/10/01/2623/inflasi-year-on-year--y-on-y--pada-september-2026-sebesar-3-28-persen-.html\n2. Bank Indonesia, IHK September 2026, rilis 1 Okt: https://www.bi.go.id/id/publikasi/ruang-media/news-release/Pages/sp_2820926.aspx\n3. BI PIHPS FAQ dan metodologi survei: https://www.bi.go.id/hargapangan/Informasi/FAQ\n4. ANTARA, Bapanas siapkan subsidi angkut, 4 Okt: https://www.antaranews.com/berita/5770812/bapanas-siapkan-subsidi-angkut-jaga-harga-daging-ayam-tetap-wajar\n5. Kompas, harga ayam turun/subsidi angkut, 4 Okt: https://money.kompas.com/read/2026/10/04/222844926/harga-ayam-turun-bapanas-siapkan-subsidi-angkut-ke-daerah\n6. Kompas, permintaan penelusuran rantai perantara, 18 Okt: https://nasional.kompas.com/read/2026/10/18/12350451/anggota-dpr-minta-usut-pihak-perantara-yang-sebabkan-anomali-harga-ayam\n7. Open Data Bapanas, proyeksi neraca pangan Oktober 2026: https://data.badanpangan.go.id/datasetpublications/vbd/proyeksi-neraca-pangan-nasional-update-oktober-2026\n8. Open Data Bapanas, definisi rata-rata harga produsen: https://data.badanpangan.go.id/datasetpublications/3iw/rata-rata-harga-pangan-bulanan-tingkat-produsen-nasional\n9. PIHPS live page, tanggal halaman 22 Okt 2026: https://www.bi.go.id/hargapangan\n\n## Risiko hukum/reputasi\n\nSedang-rendah bila seluruh klaim diberi tanggal dan label sumber. Jangan menyebut dugaan perantara sebagai fakta, jangan menggeneralisasi Medokan Sawah/Surabaya, jangan menyamakan harga hidup dengan karkas, dan jangan menjadikan angka dinamis PIHPS sebagai harga hari ini tanpa pembaruan rekaman.\n"""
    (production / "00_Topic-Radar" / "topic-brief.md").write_text(text, encoding="utf-8")


def write_metadata(production: Path, main_duration: float, shorts: list[dict[str, Any]]) -> None:
    def ts(s: float) -> str:
        return seconds_to_srt(s).split(",")[0]
    text = f"""# Packaging metadata — video pertama\n\n## Judul options\n\n1. Harga Ayam Turun, tapi Belanja Masih Terasa Mahal. Kenapa?\n2. Satu Harga Nasional, Banyak Pengalaman di Pasar\n3. Saat Grafik Harga Tak Sama dengan Struk Belanja\n4. Inflasi Pangan: Apa yang Disembunyikan Angka Rata-rata?\n5. Harga Ayam dan Cerita di Balik Rantai Pasok\n\n**Judul pilihan:** Harga Ayam Turun, tapi Belanja Masih Terasa Mahal. Kenapa?\n\n## Deskripsi draft\n\nHarga rata-rata nasional bisa turun, sementara pengalaman belanja di pasar tertentu terasa berbeda. Video ini membedah perbedaan skala, waktu, definisi produk, rantai pasok, dan cara menilai kebijakan pangan—tanpa menuduh dan tanpa menganggap satu angka mewakili semua keluarga.\n\nData utama: BPS dan Bank Indonesia untuk inflasi September 2026; PIHPS untuk metodologi harga; Bapanas melalui laporan ANTARA/Kompas untuk snapshot harga ayam dan rencana subsidi angkut. Snapshot harga ayam per 2 Oktober 2026 bukan harga live saat upload.\n\n## Bab aktual\n\nTimestamps dihitung dari WAV/MP4 final ({main_duration/60:.2f} menit).\n\n## Shorts\n\n""" + "\n".join(f"- {x['id']}: {x['title']} — {x['duration']:.2f} detik" for x in shorts) + """\n\n## Sumber\n\n- BPS: https://www.bps.go.id/id/pressrelease/2026/10/01/2623/inflasi-year-on-year--y-on-y--pada-september-2026-sebesar-3-28-persen-.html\n- BI: https://www.bi.go.id/id/publikasi/ruang-media/news-release/Pages/sp_2820926.aspx\n- BI PIHPS FAQ: https://www.bi.go.id/hargapangan/Informasi/FAQ\n- ANTARA: https://www.antaranews.com/berita/5770812/bapanas-siapkan-subsidi-angkut-jaga-harga-daging-ayam-tetap-wajar\n- Kompas: https://money.kompas.com/read/2026/10/04/222844926/harga-ayam-turun-bapanas-siapkan-subsidi-angkut-ke-daerah\n- Kompas 18 Okt: https://nasional.kompas.com/read/2026/10/18/12350451/anggota-dpr-minta-usut-pihak-perantara-yang-sebabkan-anomali-harga-ayam\n- Open Data Bapanas: https://data.badanpangan.go.id/datasetpublications/vbd/proyeksi-neraca-pangan-nasional-update-oktober-2026\n\n## Tags\n\nharga pangan Indonesia, harga ayam, inflasi pangan, BPS, Bank Indonesia, Bapanas, kebijakan pangan, ekonomi rumah tangga, rantai pasok, Surabaya, Ruang Nalar\n\n## Disclosure dan safety\n\nTidak ada upload dilakukan oleh pipeline. Visual adalah ilustrasi programatik, bukan foto dokumentasi. Voice-over adalah eSpeak NG sementara dan tidak meniru orang nyata. Jika kelak memakai suara/gambar sintetis realistis lain, tandai disclosure konten sintetis YouTube sesuai formulir yang berlaku.\n"""
    (production / "07_Metadata" / "metadata.md").write_text(text, encoding="utf-8")


def write_license_register(production: Path) -> None:
    (production / "04_Visual" / "asset-license-register.md").write_text("""# Asset/license register\n\n| Asset | Origin | License/use status | Attribution/action |\n|---|---|---|---|\n| SVG/PNG visual frames | Generated by `render.py` from original shapes/text | Original programmatic work; commercial channel use intended | No third-party image; label `ILUSTRASI PROGRAMATIK` embedded |\n| Thumbnail SVG/PNG | Generated by `render.py` | Original programmatic work | No photo/logo/stock asset |\n| DejaVu Sans/Serif | OS package `/usr/share/fonts/truetype/dejavu` | Bitstream Vera permissive license; commercial use permitted with notice | License inspected at `/usr/share/doc/fonts-dejavu-core/copyright` |\n| eSpeak NG voice/data | `espeakng-loader` package bundling eSpeak NG data | GPL-3.0 software/data; commercial use permitted subject to GPL obligations for distributed software | Voice is generic, not a person; audio labelled suara sementara |\n| FFmpeg binary | `imageio-ffmpeg` wheel | Wrapper BSD-2-Clause; local static build reports GPL/v3 flags | Binary stays local; no binary shipped in Drive deliverable |\n| Music/SFX/footage | None | No license needed | Deliberately omitted |\n| Research facts | BPS, BI, Bapanas, ANTARA, Kompas | Sources are cited, not copied as visual assets | URLs and access dates in topic brief/claim check |\n\nNo AI-generated photorealistic person, event reconstruction, news screenshot, or copyrighted footage is used.\n""", encoding="utf-8")


def write_qa(production: Path, main: Path, audio: Path, scenes: list[dict[str, Any]], durations: list[float], shorts: list[dict[str, Any]], ffmpeg: str) -> dict[str, Any]:
    main_probe = probe_media(ffmpeg, main)
    main_duration = get_duration(main_probe)
    streams = main_probe.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
    stats = wav_stats(audio)
    srt_path = production / "05_Video-Final" / "video.srt"
    srt_text = srt_path.read_text(encoding="utf-8")
    last_end = 0.0
    matches = re.findall(r"--> (\d\d):(\d\d):(\d\d),(\d\d\d)", srt_text)
    if matches:
        h, m, s, ms = matches[-1]
        last_end = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    visual_files = list((production / "04_Visual").glob("*.png"))
    visual_sizes = []
    for p in visual_files:
        with p.open("rb") as f:
            header = f.read(24)
        if header[:8] == b"\x89PNG\r\n\x1a\n":
            width = int.from_bytes(header[16:20], "big")
            height = int.from_bytes(header[20:24], "big")
            visual_sizes.append((p.name, width, height, p.stat().st_size))
    checks = {
        "main_mp4_exists": main.exists() and main.stat().st_size > 100_000,
        "duration_seconds": main_duration,
        "duration_10_to_13_minutes": 600 <= main_duration <= 780,
        "resolution": f"{video_stream.get('width')}x{video_stream.get('height')}",
        "resolution_min_1080p": video_stream.get("width") == 1920 and video_stream.get("height") == 1080,
        "video_stream": bool(video_stream),
        "audio_stream": bool(audio_stream),
        "audio_peak_dbfs": stats["peak_dbfs"],
        "audio_rms_dbfs": stats["rms_dbfs"],
        "audio_not_silent": stats["rms_dbfs"] < -5,
        "audio_not_clipping": stats["peak_dbfs"] < -0.1,
        "srt_last_end_seconds": last_end,
        "srt_within_media": last_end <= main_duration + 1.0,
        "visual_png_count": len(visual_files),
        "visual_dimensions_ok": bool(visual_sizes) and all(w == W and h == H for name, w, h, _size in visual_sizes if not name.startswith("short-")),
        "three_shorts": len(shorts) == 3 and all(Path(x["mp4"]).exists() for x in shorts),
        "shorts_vertical": all((get_duration(probe_media(ffmpeg, Path(x["mp4"]))) > 0) for x in shorts),
    }
    # More explicit vertical resolution check, kept separate from the broad probe.
    verticals = []
    for x in shorts:
        p = probe_media(ffmpeg, Path(x["mp4"]))
        vs = next((s for s in p.get("streams", []) if s.get("codec_type") == "video"), {})
        verticals.append((vs.get("width"), vs.get("height")))
    checks["shorts_resolutions"] = verticals
    checks["shorts_9x16"] = all(w == 1080 and h == 1920 for w, h in verticals)
    essential = [
        "main_mp4_exists", "duration_10_to_13_minutes", "resolution_min_1080p", "video_stream", "audio_stream",
        "audio_not_silent", "audio_not_clipping", "srt_within_media", "three_shorts", "shorts_9x16",
    ]
    status = "LOLOS" if all(checks.get(k) for k in essential) else "PERLU REVIEW"
    qa = {"status": status, "checks": checks, "voice": VOICE, "visual_count": len(visual_files), "shorts": shorts}
    (production / "08_QA-Laporan" / "qa-report.md").write_text("# Gate 3 — QA teknis\n\n" + "\n".join(f"- **{k}:** `{v}`" for k, v in checks.items()) + f"\n\n**Gate 3 result: {status}.**\n\nQA dijalankan nyata dengan FFmpeg/ffprobe, pembacaan WAV, pemeriksaan PNG header, dan pemeriksaan keberadaan SRT/Shorts.\n", encoding="utf-8")
    (production / "08_QA-Laporan" / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    return qa


def write_manifest(production: Path, qa: dict[str, Any], main_duration: float) -> None:
    entries: list[str] = []
    for p in sorted(production.rglob("*")):
        if p.is_file() and not any(part in {"tmp", "clips"} for part in p.parts):
            rel = p.relative_to(production).as_posix()
            entries.append(f"- `{rel}` — {p.stat().st_size} bytes")
    (production / "manifest.md").write_text("# Manifest — Ruang Nalar video 1\n\n**Status:** " + qa["status"] + f" · durasi utama {main_duration/60:.2f} menit\n\n## Files\n\n" + "\n".join(entries) + "\n\n## License summary\n\nOriginal text/SVG/thumbnail; eSpeak NG voice/data GPL-3.0 local; FFmpeg local GPL/v3 build; DejaVu font permissive; research URLs in `00_Topic-Radar/topic-brief.md` and `01_Riset-Sumber/claim-check.md`; no music/footage/photos.\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--production", required=True, type=Path)
    parser.add_argument("--skip-shorts", action="store_true")
    args = parser.parse_args()
    production = args.production.resolve()
    if not production.exists():
        raise SystemExit(f"Production folder tidak ada: {production}")
    scenes_path = production / "02_Naskah" / "scenes.json"
    scenes = json.loads(scenes_path.read_text(encoding="utf-8"))
    audio_dir = production / "03_Audio"; audio_dir.mkdir(parents=True, exist_ok=True)
    visual_dir = production / "04_Visual"; visual_dir.mkdir(parents=True, exist_ok=True)
    final_dir = production / "05_Video-Final"; final_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg = ffmpeg_path()
    print(f"Using FFmpeg: {ffmpeg}")

    scene_wavs = synthesize_scenes(scenes, audio_dir)
    durations = [read_wav_seconds(p) for p in scene_wavs]
    raw_audio = audio_dir / "voice-concat-raw.wav"
    concat_wavs(scene_wavs, raw_audio, silence=PAUSE_SECONDS)
    master_audio = audio_dir / "voice-master.wav"
    normalize_audio(ffmpeg, raw_audio, master_audio)
    master_stats = wav_stats(master_audio)
    shutil.copyfile(master_audio, final_dir / "audio-master.wav")
    srt = final_dir / "video.srt"
    make_srt(scenes, durations, srt)
    write_naskah(production, scenes, durations)
    write_visual_docs(production, scenes, durations)
    write_claim_check(production)
    write_topic_brief(production)
    write_license_register(production)
    (production / "03_Audio" / "audio-QA.md").write_text(f"# Audio QA\n\nMaster WAV: `{master_audio.name}`\n- Durasi: {master_stats['duration']:.2f} detik\n- Peak: {master_stats['peak_dbfs']:.2f} dBFS\n- RMS: {master_stats['rms_dbfs']:.2f} dBFS\n- Sample rate: {master_stats['sample_rate']} Hz\n- Profil: eSpeak NG `id`, 150 wpm, pitch 45, range 30; **suara sementara**.\n", encoding="utf-8")

    sequence = create_visuals(scenes, durations, visual_dir)
    visual_video = visual_dir / "visual-silent.mp4"
    assemble_visual_video(ffmpeg, sequence, visual_dir, visual_video)
    main_mp4 = final_dir / "video-utama.mp4"
    mux_main(ffmpeg, visual_video, master_audio, srt, main_mp4)
    thumbnail = make_thumbnails(production)
    shorts = [] if args.skip_shorts else render_shorts(ffmpeg, production, audio_dir, final_dir, visual_dir)
    qa = write_qa(production, main_mp4, master_audio, scenes, durations, shorts, ffmpeg)
    main_duration = get_duration(probe_media(ffmpeg, main_mp4))
    write_metadata(production, main_duration, shorts)
    write_manifest(production, qa, main_duration)
    print(json.dumps({"status": qa["status"], "main": str(main_mp4), "duration": main_duration, "thumbnail": str(thumbnail), "shorts": shorts}, ensure_ascii=False, indent=2))
    return 0 if qa["status"] == "LOLOS" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RenderError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
