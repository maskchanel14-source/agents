#!/usr/bin/env python3
"""
cover_build.py -- DS-003 "MIRROR LIFE" clickbait cover, 1080x1920.

Everything is drawn from primitives so the cover can be re-rendered, re-worded
and A/B tested without a design tool. The only raster input is the background
art in `cover-art-bg.png`.

Three variants are written, sharing the same visual language:
  cover-A-kaget.png   shock face + reaction tag
  cover-B-angka.png   giant "38" numeral, the number is the art
  cover-C-hitam.png   minimal, maximum contrast, no clutter

Usage: cover_build.py [--art cover-art-bg.png] [--out .]
"""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
FONT_DIR = Path("/home/user/.venv-thumb/fonts")

W, H = 1080, 1920

INK = (255, 255, 255)
CYAN = (34, 211, 238)
RED = (255, 32, 32)
AMBER = (255, 197, 61)
BLACK = (5, 7, 10)


# --------------------------------------------------------------------- utils
def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def text_size(draw: ImageDraw.ImageDraw, s: str, f: ImageFont.FreeTypeFont) -> tuple[int, int]:
    l, t, r, b = draw.textbbox((0, 0), s, font=f)
    return r - l, b - t


def fit_font(draw, s: str, name: str, target_w: int, start: int = 400) -> ImageFont.FreeTypeFont:
    """Largest size whose rendered width fits target_w."""
    size = start
    while size > 12:
        f = font(name, size)
        if text_size(draw, s, f)[0] <= target_w:
            return f
        size -= 2
    return font(name, 12)


def layer() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def paste(base: Image.Image, im: Image.Image) -> Image.Image:
    return Image.alpha_composite(base, im)


# ------------------------------------------------------------------ background
def background(art_path: Path, focus: tuple[float, float] = (0.42, 0.50),
               zoom: float = 1.0) -> Image.Image:
    """Crop the square art to 9:16 around `focus`, grade it, add vignette."""
    art = Image.open(art_path).convert("RGB")
    aw, ah = art.size
    # the 9:16 crop of a square: width = h*9/16
    crop_w = ah * 9 / 16
    cx, cy = focus[0] * aw, focus[1] * ah
    left = min(max(0, cx - crop_w / 2), aw - crop_w)
    art = art.crop((int(left), 0, int(left + crop_w), ah))
    art = art.resize((int(W * zoom), int(H * zoom)), Image.LANCZOS)
    if zoom > 1.0:
        ox = int((art.width - W) * focus[0])
        oy = int((art.height - H) * 0.35)
        art = art.crop((ox, oy, ox + W, oy + H))
    else:
        art = art.resize((W, H), Image.LANCZOS)
    return art


def grade(im: Image.Image) -> Image.Image:
    """Push contrast, crush blacks, warm the reds, cool the cyans."""
    a = np.asarray(im, dtype=np.float32) / 255.0
    a = np.clip((a - 0.5) * 1.22 + 0.5, 0, 1)          # contrast
    a = a ** 1.18                                      # deeper blacks
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    a[..., 0] = np.clip(r * 1.10, 0, 1)                # warm highlights
    a[..., 2] = np.clip(b * 1.05, 0, 1)                # lift the cyan
    a[..., 1] = np.clip(g * 1.02, 0, 1)

    # vignette
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H / 2) / (H * 0.72)) ** 2)
    vig = np.clip(1.06 - 0.55 * d ** 2.1, 0, 1)[..., None]
    a = a * vig

    # top + bottom scrims so type always has a dark bed
    top = np.clip((yy - 0) / (H * 0.34), 0, 1)[..., None]
    a = a * (0.25 + 0.75 * top)
    bot = np.clip((H - yy) / (H * 0.30), 0, 1)[..., None]
    a = a * (0.20 + 0.80 * bot)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def grain(im: Image.Image, amount: float = 7.0, seed: int = 4) -> Image.Image:
    rng = np.random.default_rng(seed)
    a = np.asarray(im, dtype=np.float32)
    a += rng.normal(0, amount, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- type helpers
def draw_shout(base: Image.Image, lines: list[tuple[str, tuple[int, int, int], float]],
               centre_y: int, max_w: int, outline_px: int = 10, shadow: bool = True,
               gap: int = 0) -> Image.Image:
    """
    Stack big Anton lines, each (text, colour, relative size).

    All shadows are painted first, then all fills — otherwise the shadow of the
    next line eats the bottom of the line above it.
    """
    im, d = layer()
    sizes = []
    for s, _, _ in lines:
        f = fit_font(d, s, "Anton-Regular.ttf", max_w, start=520)
        sizes.append(f.size)
    metrics = []
    for s, col, rel in lines:
        f = font("Anton-Regular.ttf", math.floor(min(sizes) * rel))
        w, h = text_size(d, s, f)
        metrics.append((s, col, f, w, h))
    gap = 22 if gap == 0 else gap
    total = sum(m[4] for m in metrics) + gap * (len(metrics) - 1)
    y = centre_y - total / 2

    if shadow:
        yy = y
        for s, _, f, w, h in metrics:
            d.text(((W - w) / 2 + 8, yy + 11), s, font=f, fill=(0, 0, 0, 200))
            yy += h + gap
    yy = y
    for s, col, f, w, h in metrics:
        d.text(((W - w) / 2, yy), s, font=f, fill=col + (255,),
               stroke_width=outline_px, stroke_fill=(0, 0, 0, 255))
        yy += h + gap
    return paste(base, im)


def draw_stack(base: Image.Image, lines: list[tuple[str, tuple[int, int, int], float]],
               top: int, max_w: int, outline_px: int = 11, gap: int = 18,
               ref: str = "Anton-Regular.ttf") -> tuple[Image.Image, int]:
    """
    Draw a block of shout lines starting at `top`, all sized from the widest
    line so the block has one consistent scale. Returns (image, bottom_y) so the
    next element can be placed without guessing.
    """
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    base_size = min(fit_font(probe, t, ref, max_w, start=520).size for t, _, _ in lines)
    im, d = layer()
    y = top
    for text, col, rel in lines:
        f = font(ref, max(20, math.floor(base_size * rel)))
        w, h = text_size(d, text, f)
        d.text(((W - w) / 2 + 8, y + 12), text, font=f, fill=(0, 0, 0, 200))
        d.text(((W - w) / 2, y), text, font=f, fill=col + (255,),
               stroke_width=outline_px, stroke_fill=(0, 0, 0, 255))
        y += h + gap
    return paste(base, im), y


def draw_kicker(base: Image.Image, s: str, y: int, colour=CYAN, size=34,
                tracking: float = 0.22) -> Image.Image:
    im, d = layer()
    f = font("JetBrainsMono-ExtraBold.ttf", size)
    # manual tracking
    widths = [d.textlength(ch, font=f) for ch in s]
    total = sum(widths) + tracking * size * (len(s) - 1)
    x = (W - total) / 2
    for ch, w in zip(s, widths):
        d.text((x, y), ch, font=f, fill=colour + (255,))
        x += w + tracking * size
    return paste(base, im)


def draw_badge(base: Image.Image, s: str, cx: int, cy: int, bg=RED,
               size: int = 40, pad_x: int = 26, pad_y: int = 14,
               rot: float = -6.0) -> Image.Image:
    """Rotated sticker label. Drawn on its own canvas then pasted."""
    f = font("Anton-Regular.ttf", size)
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    w, h = text_size(d, s, f)
    bw, bh = int(w + pad_x * 2), int(h + pad_y * 2 + size * 0.18)
    canvas = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    cd = ImageDraw.Draw(canvas)
    cd.rounded_rectangle([20, 20, 20 + bw, 20 + bh], radius=bh * 0.22,
                         fill=bg + (255,), outline=(0, 0, 0, 255), width=7)
    cd.text((20 + pad_x, 20 + pad_y - size * 0.06), s, font=f, fill=INK + (255,))
    canvas = canvas.rotate(rot, expand=True, resample=Image.BICUBIC)
    base.alpha_composite(canvas, (int(cx - canvas.width / 2), int(cy - canvas.height / 2)))
    return base


def draw_arrow(base: Image.Image, x0: int, y0: int, x1: int, y1: int,
               colour=RED, width: int = 22) -> Image.Image:
    im, d = layer()
    d.line([(x0, y0), (x1, y1)], fill=colour + (255,), width=width)
    ang = math.atan2(y1 - y0, x1 - x0)
    head = 62
    for s in (-0.46, 0.46):
        d.line([(x1, y1), (x1 - head * math.cos(ang + s), y1 - head * math.sin(ang + s))],
               fill=colour + (255,), width=width)
    return paste(base, im)


def draw_circle(base: Image.Image, cx: int, cy: int, rx: int, ry: int,
                colour=RED, width: int = 16, wobble: float = 0.02,
                seed: int = 9) -> Image.Image:
    """Hand-drawn-looking ellipse: a wobbly, slightly open loop."""
    im, d = layer()
    rng = random.Random(seed)
    pts = []
    for i in range(181):
        a = -0.10 + (i / 180) * (2 * math.pi * 0.985)
        j = 1 + rng.uniform(-wobble, wobble)
        pts.append((cx + math.cos(a) * rx * j, cy + math.sin(a) * ry * j))
    d.line(pts, fill=colour + (255,), width=width, joint="curve")
    return paste(base, im)


def draw_highlight_box(base: Image.Image, x0, y0, x1, y1, colour=AMBER, width=12):
    im, d = layer()
    d.rounded_rectangle([x0, y0, x1, y1], radius=18, outline=colour + (255,), width=width)
    return paste(base, im)


# ------------------------------------------------------------- silhouette face
def draw_shocked_face(base: Image.Image, cx: int, cy: int, scale: float = 1.0,
                      rim=CYAN) -> Image.Image:
    """
    A rim-lit human head in silhouette — mouth open in shock, eyes wide.
    Drawn as an alpha mask so the background art shows through: it reads as a
    real person lit from behind by the microscope light, which is what makes
    the shock expression land without a photographic model.
    """
    aw, ah = int(560 * scale), int(700 * scale)
    mask = Image.new("L", (aw, ah), 0)
    m = ImageDraw.Draw(mask)

    head_cx, head_cy = aw // 2, int(ah * 0.36)
    head_rx, head_ry = int(aw * 0.30), int(ah * 0.27)
    # skull
    m.ellipse([head_cx - head_rx, head_cy - head_ry,
               head_cx + head_rx, head_cy + head_ry], fill=255)
    # jaw / chin taper
    m.polygon([(head_cx - head_rx * 0.86, head_cy + head_ry * 0.20),
               (head_cx + head_rx * 0.86, head_cy + head_ry * 0.20),
               (head_cx + head_rx * 0.52, head_cy + head_ry * 0.98),
               (head_cx - head_rx * 0.52, head_cy + head_ry * 0.98)], fill=255)
    # neck + shoulders
    neck_w = int(aw * 0.16)
    m.rectangle([head_cx - neck_w, head_cy + head_ry * 0.75,
                 head_cx + neck_w, int(ah * 0.80)], fill=255)
    m.polygon([(head_cx - aw * 0.12, int(ah * 0.76)),
               (head_cx + aw * 0.12, int(ah * 0.76)),
               (head_cx + aw * 0.50, ah),
               (head_cx - aw * 0.50, ah)], fill=255)

    # features are CUT OUT of the silhouette (dark holes) so the face reads
    feat = Image.new("L", (aw, ah), 0)
    fd = ImageDraw.Draw(feat)
    # eyes — wide, asymmetric for alarm
    eye_y = head_cy - head_ry * 0.16
    for ex, er in ((-head_rx * 0.42, 1.10), (head_rx * 0.40, 1.00)):
        w = head_rx * 0.24 * er
        h = head_ry * 0.15 * er
        fd.ellipse([head_cx + ex - w, eye_y - h, head_cx + ex + w, eye_y + h], fill=255)
    # brows raised high
    fd.arc([head_cx - head_rx * 0.72, eye_y - head_ry * 0.34,
            head_cx - head_rx * 0.16, eye_y - head_ry * 0.10],
           start=200, end=340, fill=255, width=int(aw * 0.022))
    fd.arc([head_cx + head_rx * 0.12, eye_y - head_ry * 0.36,
            head_cx + head_rx * 0.70, eye_y - head_ry * 0.12],
           start=200, end=340, fill=255, width=int(aw * 0.022))
    # open mouth
    mw, mh = head_rx * 0.30, head_ry * 0.30
    my = head_cy + head_ry * 0.42
    fd.ellipse([head_cx - mw, my - mh, head_cx + mw, my + mh], fill=255)

    mask = Image.composite(Image.new("L", (aw, ah), 0), mask, feat)

    # build RGBA: near-black body + bright rim
    body = Image.new("RGBA", (aw, ah), (0, 0, 0, 0))
    body.putalpha(mask)
    fill = Image.new("RGBA", (aw, ah), (6, 8, 12, 255))
    body = Image.composite(fill, Image.new("RGBA", (aw, ah), (0, 0, 0, 0)), mask)

    # rim light: offset the mask a few px and subtract
    off = int(aw * 0.028)
    shifted = Image.new("L", (aw, ah), 0)
    shifted.paste(mask, (off, int(-off * 0.4)))
    rim_mask = Image.fromarray(np.clip(np.asarray(mask, np.int16) -
                                       np.asarray(Image.fromarray(np.asarray(shifted) * 0), np.int16), 0, 255).astype(np.uint8))
    # simpler + more controllable: rim = mask minus eroded mask
    from PIL import ImageFilter
    eroded = mask.filter(ImageFilter.MinFilter(2 * off + 1))
    rim_mask = Image.fromarray(np.clip(np.asarray(mask, np.int16) - np.asarray(eroded, np.int16), 0, 60).astype(np.uint8))
    rim_mask = rim_mask.point(lambda v: min(255, int(v * 6)))
    rim_layer = Image.new("RGBA", (aw, ah), rim + (255,))
    rim_layer.putalpha(rim_mask)

    out = Image.new("RGBA", (aw, ah), (0, 0, 0, 0))
    out = Image.alpha_composite(out, body)
    # glow behind the rim
    from PIL import ImageFilter as IF
    glow = rim_layer.filter(IF.GaussianBlur(aw * 0.02))
    out = Image.alpha_composite(out, glow)
    out = Image.alpha_composite(out, rim_layer)

    out = out.rotate(-5, expand=True, resample=Image.BICUBIC)
    base.alpha_composite(out, (int(cx - out.width / 2), int(cy - out.height / 2)))
    return base



# ---------------------------------------------------------------- photo layer
def overlay_photo(base: Image.Image, photo: Path, x: int, y: int, width: int,
                  blend: str = "lighter", opacity: float = 1.0) -> Image.Image:
    """
    Dodge the photo onto the plate: black in the photo means "let the art
    through", so a studio portrait on a black background can sit over the
    microscope art without a visible cut-out edge.
    """
    # knock the plate back under the portrait so nothing ghosts through skin
    hole = Image.new("L", (base.width, base.height), 0)
    hd = ImageDraw.Draw(hole)
    ph0 = Image.open(photo)
    hh = int(width * ph0.height / ph0.width)
    hd.ellipse([x + width * 0.24, y + hh * 0.02, x + width * 1.04, y + hh * 0.98], fill=255)
    hole = hole.filter(ImageFilter.GaussianBlur(width * 0.09))
    dark = Image.new("RGBA", base.size, (2, 3, 6, 255))
    base = Image.composite(dark, base, hole.point(lambda v: int(v * 0.82)))

    ph = Image.open(photo).convert("RGB")
    ph = ph.resize((width, int(width * ph.height / ph.width)), Image.LANCZOS)
    ph = ph.point(lambda v: v * opacity)
    rgb = base.convert("RGB")
    box = (x, y, x + ph.width, y + ph.height)
    region = rgb.crop(box)
    if blend == "lighter":
        out = ImageChops.lighter(region, ph)
    elif blend == "multiply":
        out = ImageChops.multiply(region, ph)
    else:
        out = ImageChops.screen(region, ph)
    rgb.paste(out, (x, y))
    return rgb.convert("RGBA")


def glow_text(base: Image.Image, s: str, cy: int, fname: str, size: int,
              colour, glow_rgb=(255, 40, 40), spread: int = 60) -> tuple[Image.Image, int]:
    """Draw big type with a coloured bloom behind it. Returns (image, height)."""
    lay, d = layer()
    f = font(fname, size)
    w, h = text_size(d, s, f)
    x, y = (W - w) / 2, cy - h / 2
    bloom = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bloom)
    bd.text((x, y), s, font=f, fill=glow_rgb + (230,), stroke_width=spread // 3,
            stroke_fill=glow_rgb + (200,))
    bloom = bloom.filter(ImageFilter.GaussianBlur(spread))
    d.text((x + 8, y + 10), s, font=f, fill=(0, 0, 0, 190), stroke_width=10,
           stroke_fill=(0, 0, 0, 190))
    d.text((x, y), s, font=f, fill=colour + (255,), stroke_width=10,
           stroke_fill=(0, 0, 0, 255))
    out = paste(base, bloom)
    out = paste(out, lay)
    return out, h


def badge_fit(base: Image.Image, s: str, cx: int, cy: int, max_w: int,
              bg=RED, size: int = 44, rot: float = -6.0) -> Image.Image:
    """Sticker label whose width never exceeds max_w."""
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    f = fit_font(d, s, "Anton-Regular.ttf", max_w - 60, start=size)
    w, h = text_size(d, s, f)
    bw, bh = int(w + 52), int(h + 34)
    canvas = Image.new("RGBA", (bw + 60, bh + 60), (0, 0, 0, 0))
    cd = ImageDraw.Draw(canvas)
    cd.rounded_rectangle([30, 30, 30 + bw, 30 + bh], radius=bh * 0.24,
                         fill=bg + (255,), outline=(0, 0, 0, 255), width=8)
    cd.text((30 + 26, 30 + 13), s, font=f, fill=INK + (255,))
    canvas = canvas.rotate(rot, expand=True, resample=Image.BICUBIC)
    base.alpha_composite(canvas, (int(cx - canvas.width / 2), int(cy - canvas.height / 2)))
    return base


# ------------------------------------------------------------------ variants
def base_plate(art: Path, focus=(0.42, 0.50), zoom=1.0) -> Image.Image:
    im = grade(background(art, focus, zoom)).convert("RGBA")
    return im


def variant_shock(art: Path, out: Path) -> Path:
    """The full clickbait stack: shout, shock face, sticker, arrow."""
    im = base_plate(art, focus=(0.40, 0.52), zoom=1.12)
    im = draw_kicker(im, "SCIENCE, DEC 2024", 96, CYAN, 40, 0.20)

    im, bottom = draw_stack(im, [("THEY WARNED US", INK, 0.92)], top=176, max_w=960, outline_px=11)
    im, bottom = draw_stack(im, [("NOT TO BUILD", INK, 0.92)], top=bottom - 12, max_w=960, outline_px=11)
    im, _ = glow_text(im, "THIS", cy=bottom + 96, fname="Anton-Regular.ttf", size=290,
                      colour=RED, spread=52)

    # the shock face, dodged over the art so there is no cut-out edge
    im = overlay_photo(im, ROOT / "reaction-face.png", x=250, y=640, width=880)

    # sticker pinned to the bacterium, arrow through it
    im = draw_arrow(im, 235, 1235, 360, 1180, RED, 18)
    im = badge_fit(im, "IT DOESN'T EXIST. YET.", 470, 1300, max_w=840, bg=RED, size=64, rot=-6)
    im = badge_fit(im, "38 SCIENTISTS", 320, 1620, max_w=700, bg=CYAN, size=68, rot=-3)
    im = draw_kicker(im, "DARK SCIENCE · AI ILLUSTRATION", 1830, (170, 180, 190), 24, 0.20)
    return grain(im.convert("RGB")).save(out, quality=95)


def variant_number(art: Path, out: Path) -> Path:
    """The number IS the art: a giant ghosted 38 the type sits inside."""
    im = base_plate(art, focus=(0.42, 0.50), zoom=1.06)

    lay, d = layer()
    f = fit_font(d, "38", "Anton-Regular.ttf", 940, start=1200)
    w, h = text_size(d, "38", f)
    x, y = (W - w) / 2, 330
    d.text((x + 14, y + 16), "38", font=f, fill=(0, 0, 0, 110),
           stroke_width=16, stroke_fill=(0, 0, 0, 110))
    d.text((x, y), "38", font=f, fill=(232, 238, 245, 74), stroke_width=12,
           stroke_fill=(8, 12, 18, 110))
    im = paste(im, lay)

    im = draw_kicker(im, "SCIENCE, DEC 2024", 108, CYAN, 38, 0.20)
    im = draw_kicker(im, "SCIENTISTS BEGGED US", y + 56, INK, 54, 0.08)
    im, bottom = draw_stack(im, [("DON'T BUILD", INK, 1.0)], top=y + 150,
                            max_w=980, outline_px=11)
    im, _ = glow_text(im, "THIS", cy=bottom + 130, fname="Anton-Regular.ttf",
                      size=300, colour=RED, spread=44)

    # one short arrow from the label to the cell -- no circle, no clutter,
    # because at 270 px nothing else survives
    im = draw_arrow(im, 480, 1395, 310, 1225, AMBER, 16)
    im = badge_fit(im, "A BACTERIUM", 660, 1450, max_w=580, bg=AMBER, size=62, rot=3)
    im = badge_fit(im, "NOT A BOMB", 300, 1610, max_w=480, bg=RED, size=54, rot=-6)
    im = draw_kicker(im, "DARK SCIENCE · AI ILLUSTRATION", 1830, (170, 180, 190), 24, 0.20)
    return grain(im.convert("RGB")).save(out, quality=95)


def variant_minimal(art: Path, out: Path) -> Path:
    """Minimal, maximum contrast: three lines, one number, no clutter."""
    im = base_plate(art, focus=(0.40, 0.46), zoom=1.20)
    im = draw_kicker(im, "IT DOESN'T EXIST", 130, RED, 46, 0.20)
    im, bottom = draw_stack(im, [("NOTHING ON", INK, 0.88), ("EARTH CAN", INK, 0.88)],
                            top=210, max_w=940, outline_px=11, gap=16)
    im, bottom = draw_stack(im, [("STOP IT", RED, 1.0)], top=bottom + 10, max_w=960, outline_px=14)
    im = draw_kicker(im, "38 SCIENTISTS · SCIENCE, DEC 2024", 1650, INK, 34, 0.14)
    im = draw_kicker(im, "DARK SCIENCE · AI ILLUSTRATION", 1810, (170, 180, 190), 24, 0.20)
    return grain(im.convert("RGB")).save(out, quality=95)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--art", default="cover-art-bg.png")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    art = ROOT / args.art if not Path(args.art).is_absolute() else Path(args.art)
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.mkdir(parents=True, exist_ok=True)

    for name, fn in (("cover-A-kaget", variant_shock),
                     ("cover-B-angka", variant_number),
                     ("cover-C-hitam", variant_minimal)):
        p = out / f"{name}.png"
        fn(art, p)
        print("wrote", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
