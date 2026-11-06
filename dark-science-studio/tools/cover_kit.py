#!/usr/bin/env python3
"""
cover_kit.py -- clickbait cover frames for the Dark Science channel (1080x1920).

The Standing Rule from the owner: covers must be far MORE clickbait than a
polite frame grab — maximum contrast, huge type, an annotation that points at
the horror, and one number that stops a thumb.

    python tools/cover_kit.py --project projects/DS-005 [--bg path.png]

Background: a Remotion still of one of the episode's own scenes (so the cover
is 100% original) with the scene's HUD hidden behind our own type stack.
Outputs:
    projects/<id>/cover_frame.png        1080x1920 master
    projects/<id>/cover_frame_small.png  320x568 preview (thumbnail-scale check)

Design rules baked in (from the delivered DS-003 pack):
  * one accent + white + red, nothing else saturated
  * shout inside the middle third, never below 20 px at 1080 wide
  * every word is either a number, a threat, or an impossible contrast
"""
from __future__ import annotations

import argparse
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
W, H = 1080, 1920

WHITE = (255, 255, 255)
BLACK = (4, 6, 9)
RED = (255, 42, 42)
AMBER = (255, 197, 61)

SPECS: dict[str, dict] = {
    "DS-005": {
        "scene": "star_wake",
        "scene_props": {"sep": 0.92, "r": 8.4},
        "accent": (255, 138, 61),
        "kicker": "BETELGEUSE / ALPHA ORIONIS",
        "lines": [("THERE IS", WHITE, 132), ("A STAR", WHITE, 190), ("INSIDE", AMBER, 218), ("BETELGEUSE", WHITE, 150)],
        "badge": ("2,100", "DAY CYCLE"),
        "note": "RADIO / 22-485 GHz",
        "circle": (188, 952, 128),
        "ring_label": "SIWARHA ORBIT",
        "ring_label_at": (96, 1100),
    },
    "DS-006": {
        "scene": "neutrino_shower",
        "scene_props": {"impact": 0.30},
        "accent": (34, 211, 238),
        "kicker": "KM3NeT / 3.5 KM DEEP",
        "lines": [("1 PARTICLE", WHITE, 132), ("220", AMBER, 280), ("PeV", WHITE, 150), ("SHOULD NOT", WHITE, 104), ("EXIST", RED, 190)],
        "badge": ("30x", "OLD RECORD"),
        "note": "ICECUBE SAW NOTHING",
        "circle": (566, 980, 240),
    },
    "DS-007": {
        "scene": "nerve_invasion",
        "scene_props": {"invasion": 0.95},
        "accent": (255, 77, 94),
        "kicker": "NAEGLERIA FOWLERI / CDC",
        "lines": [("IT EATS", WHITE, 150), ("YOUR", WHITE, 150), ("BRAIN", RED, 260), ("IN 5 DAYS", AMBER, 130)],
        "badge": ("4 / 167", "SURVIVED"),
        "note": "ENTERED THROUGH THE NOSE",
        "circle": (556, 1020, 250),
    },
}


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def text_w(d: ImageDraw.ImageDraw, s: str, f: ImageFont.FreeTypeFont) -> int:
    l, _, r, _ = d.textbbox((0, 0), s, font=f)
    return r - l


def fit(name: str, s: str, target: int, start: int) -> ImageFont.FreeTypeFont:
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    size = start
    while size > 40:
        f = font(name, size)
        if text_w(probe, s, f) <= target:
            return f
        size -= 4
    return font(name, 40)


def render_bg(spec: dict, out: Path) -> None:
    studio = ROOT / "tools" / "studio"
    props = {"scene": spec["scene"], "props": spec["scene_props"]}
    cmd = [
        "bash", str(studio / "scripts" / "remotion-run.sh"), "npx", "remotion", "still",
        "src/index.ts", "ScenePreview", str(out),
        f"--props={__import__('json').dumps(props)}",
        "--gl=swiftshader",
        f"--browser-executable={ROOT / '.chromium' / 'chrome-wrapper.sh'}",
    ]
    subprocess.run(cmd, cwd=studio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build(proj: Path, video_id: str) -> Path:
    spec = SPECS[video_id]
    bg_path = ROOT / "renders" / "prev" / f"cover_{video_id}.png"
    bg_path.parent.mkdir(parents=True, exist_ok=True)
    render_bg(spec, bg_path)

    base = Image.open(bg_path).convert("RGB").resize((W, H))
    # crush the scene so the type owns the frame
    dark = Image.new("RGB", (W, H), BLACK)
    base = Image.blend(base, dark, 0.26)
    base = base.filter(ImageFilter.GaussianBlur(0.6))
    # accent glow behind the type block
    glow = Image.new("RGB", (W, H), BLACK)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((60, 380, W - 60, 1420), fill=tuple(int(c * 0.22) for c in spec["accent"]))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img = Image.blend(base, glow, 0.42)
    d = ImageDraw.Draw(img)

    # ---------------- kicker bar
    kf = font("JetBrainsMono-Regular.ttf", 34)
    d.rectangle((0, 120, W, 186), fill=(0, 0, 0))
    d.text((56, 138), spec["kicker"], font=kf, fill=spec["accent"])
    d.line((56, 186, W - 56, 186), fill=tuple(int(c * 0.55) for c in spec["accent"]), width=2)

    # ---------------- annotation: circle + arrow behind the type
    cx, cy, rad = spec["circle"]
    for wdt, alpha in ((10, 255), (22, 90)):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), outline=RED + (alpha,), width=wdt)
        img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    if spec.get("ring_label"):
        lf = font("JetBrainsMono-Regular.ttf", 30)
        lx, ly = spec["ring_label_at"]
        d.text((lx, ly), spec["ring_label"], font=lf, fill=RED)

    # ---------------- the shout: stacked, outlined, huge
    # Measure the whole block first and scale it into the safe band (top 470,
    # bottom 1240) so a long word list can never collide with the number badge.
    band_top, band_bottom = 470, 1240
    adv = 0.98
    fonts = []
    for text, colour, size in spec["lines"]:
        fonts.append(fit("Anton-Regular.ttf", text, W - 130, size))
    total = sum(int(f.size * adv) for f in fonts)
    scale = min(1.0, (band_bottom - band_top) / total)
    if scale < 1.0:
        fonts = [font("Anton-Regular.ttf", max(46, int(f.size * scale))) for f in fonts]
        total = sum(int(f.size * adv) for f in fonts)
    y = band_top + ((band_bottom - band_top) - total) // 2
    for (text, colour, _), f in zip(spec["lines"], fonts):
        w = text_w(d, text, f)
        x = (W - w) // 2
        # heavy stroke behind for phone-size legibility
        d.text((x, y), text, font=f, fill=BLACK, stroke_width=16, stroke_fill=BLACK)
        d.text((x, y), text, font=f, fill=BLACK, stroke_width=8, stroke_fill=BLACK)
        d.text((x, y), text, font=f, fill=colour)
        y += int(f.size * adv)

    # ---------------- number badge (the second hook)
    num, cap = spec["badge"]
    nf = font("Anton-Regular.ttf", 150)
    cf = font("JetBrainsMono-Regular.ttf", 32)
    bw = max(text_w(d, num, nf), text_w(d, cap, cf)) + 76
    bx, by = W - bw - 56, 1300
    d.rounded_rectangle((bx, by, bx + bw, by + 262), radius=22, fill=(0, 0, 0), outline=AMBER, width=5)
    d.text((bx + bw // 2 - text_w(d, num, nf) // 2, by + 18), num, font=nf, fill=AMBER)
    d.text((bx + bw // 2 - text_w(d, cap, cf) // 2, by + 200), cap, font=cf, fill=WHITE)

    # ---------------- bottom rail
    d.rectangle((0, H - 150, W, H), fill=(0, 0, 0))
    d.text((56, H - 118), "DARK SCIENCE", font=font("Montserrat-ExtraBold.ttf", 44), fill=WHITE)
    nf2 = font("JetBrainsMono-Regular.ttf", 30)
    d.text((56, H - 62), spec["note"], font=nf2, fill=spec["accent"])

    proj.mkdir(parents=True, exist_ok=True)
    out = proj / "cover_frame.png"
    img.save(out, quality=95)
    img.resize((320, 568), Image.LANCZOS).save(proj / "cover_frame_small.png")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()
    proj = Path(args.project)
    if not proj.is_absolute():
        proj = ROOT / proj
    vid = proj.name
    if vid not in SPECS:
        raise SystemExit(f"no cover spec for {vid}; known: {sorted(SPECS)}")
    out = build(proj, vid)
    print(f"[cover] {out}  {Image.open(out).size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
