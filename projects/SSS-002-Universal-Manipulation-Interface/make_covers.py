#!/usr/bin/env python3
"""Generate viral, dramatic, 100% honest 9:16 Shorts Cover & 16:9 YouTube Thumbnail for SSS-002."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def load_font(size: int):
    return ImageFont.truetype(FONT_BOLD, size)

def draw_stroked_text(draw, pos, text, font, fill, stroke_fill=(0, 0, 0, 255), stroke_width=8, shadow_offset=(0, 8)):
    x, y = pos
    if shadow_offset:
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font,
                  fill=(0, 0, 0, 215), stroke_width=stroke_width + 4, stroke_fill=(0, 0, 0, 215))
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)

def draw_centered_stroked(draw, canvas_w, y, text, font, fill, stroke_width=9):
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    tw = bbox[2] - bbox[0]
    x = (canvas_w - tw) // 2
    draw_stroked_text(draw, (x, y), text, font, fill, stroke_width=stroke_width)
    return x, tw, bbox[3] - bbox[1]

def build_9x16_cover(raw_path: str, out_path: str):
    W, H = 1080, 1920
    raw = Image.open(raw_path).convert("RGB")
    rw, rh = raw.size
    # Crop out the letterboxed top/bottom bands of raw_path (middle square-ish photography zone y: 20%..80%)
    y0, y1 = int(rh * 0.195), int(rh * 0.805)
    core = raw.crop((0, y0, rw, y1))
    # Resize core to width=1080
    ch = int(W * (core.height / core.width))
    core = core.resize((W, ch), Image.Resampling.LANCZOS)
    core = ImageEnhance.Contrast(core).enhance(1.16)
    core = ImageEnhance.Color(core).enhance(1.18)
    core = ImageEnhance.Sharpness(core).enhance(1.25)

    # Place core centered around y=370..370+ch on deep dark studio canvas and feather top/bottom edges seamlessly
    canvas = Image.new("RGB", (W, H), (5, 8, 14))
    arr_bg = np.zeros((H, W, 3), dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    # Subtle radial cyan/amber studio glow in background
    glow_c = np.exp(-((xx - 340)**2 + (yy - 760)**2) / (2 * 360**2))
    glow_a = np.exp(-((xx - 760)**2 + (yy - 1080)**2) / (2 * 400**2))
    arr_bg[:, :, 0] = 5 + 32 * glow_a
    arr_bg[:, :, 1] = 8 + 38 * glow_c + 16 * glow_a
    arr_bg[:, :, 2] = 15 + 62 * glow_c + 8 * glow_a
    canvas = Image.fromarray(np.clip(arr_bg, 0, 255).astype(np.uint8))

    paste_y = 365
    # Create smooth alpha feather mask at top & bottom 120px of core so zero seam line ever shows
    mask = np.ones((ch, W), dtype=np.float32)
    feather = 135
    mask[:feather, :] = np.linspace(0.0, 1.0, feather)[:, None] ** 1.4
    mask[-feather:, :] = np.linspace(1.0, 0.0, feather)[:, None] ** 1.4
    mask_img = Image.fromarray((mask * 255).astype(np.uint8))
    canvas.paste(core, (0, paste_y), mask_img)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Top dramatic crimson/gold badge
    f_badge = load_font(33)
    badge_txt = "STANFORD × MIT ROBOTICS SHOCK"
    bb = d.textbbox((0, 0), badge_txt, font=f_badge)
    bw = bb[2] - bb[0] + 56
    bx = (W - bw) // 2
    by = 78
    d.rounded_rectangle([bx, by, bx + bw, by + 58], radius=29, fill=(215, 28, 38, 245), outline=(255, 215, 90, 255), width=3)
    d.text((bx + 28, by + 10), badge_txt, font=f_badge, fill=(255, 255, 255, 255))

    # Giant 3-line explosive honest-clickbait headline
    f_h1 = load_font(94)
    f_h2 = load_font(86)
    f_h3 = load_font(90)
    draw_centered_stroked(d, W, 152, "$73 CLAW?!", f_h1, (255, 220, 55, 255), stroke_width=11)
    draw_centered_stroked(d, W, 256, "TAUGHT ROBOTS", f_h2, (255, 255, 255, 255), stroke_width=10)
    draw_centered_stroked(d, W, 350, "HUMAN HANDS!", f_h3, (56, 220, 255, 255), stroke_width=10)

    # Honest hardware callout pill pointing to the dual mirrors on the left claw
    f_call = load_font(28)
    call_txt = "1 GOPRO + 2 TINY MIRRORS"
    cbb = d.textbbox((0, 0), call_txt, font=f_call)
    cbw = (cbb[2] - cbb[0]) + 44
    d.rounded_rectangle([36, 1188, 36 + cbw, 1246], radius=16, fill=(8, 20, 34, 238), outline=(56, 220, 255, 255), width=3)
    d.text((58, 1200), call_txt, font=f_call, fill=(115, 238, 255, 255))
    # Pointer line up to mirror glass
    d.line([(210, 1188), (144, 772)], fill=(56, 220, 255, 235), width=5)
    d.ellipse([133, 761, 155, 783], fill=(255, 220, 55, 255), outline=(0, 0, 0, 255), width=3)

    # Bottom dramatic comparison banner (safely above Shorts bottom UI y=1560)
    d.rounded_rectangle([58, 1300, W - 58, 1485], radius=24, fill=(12, 14, 22, 238), outline=(255, 196, 54, 255), width=4)
    f_b1 = load_font(44)
    f_b2 = load_font(52)
    draw_centered_stroked(d, W, 1322, "ZERO ROBOTS IN TRAINING", f_b1, (255, 255, 255, 255), stroke_width=6)
    draw_centered_stroked(d, W, 1388, "$40,000 LAB ARM BEATEN!", f_b2, (255, 212, 59, 255), stroke_width=7)

    # Subtle brand signature above bottom edge
    f_sig = load_font(26)
    draw_centered_stroked(d, W, 1520, "SMALL SIGNAL STUDIO  •  ARXIV:2402.10329", f_sig, (201, 162, 91, 240), stroke_width=4)

    out = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    out.save(out_path, quality=96, subsampling=0)
    print(f"Saved 9:16 cover -> {out_path} ({out.size})")

def build_16x9_thumb(raw_path: str, out_path: str):
    W, H = 1920, 1080
    base = Image.open(raw_path).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    base = ImageEnhance.Contrast(base).enhance(1.15)
    base = ImageEnhance.Color(base).enhance(1.18)
    base = ImageEnhance.Sharpness(base).enhance(1.22)

    # Add smooth left-side dark gradient vignette for crystal-clear typography contrast
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad = np.zeros((H, W, 4), dtype=np.uint8)
    xx = np.linspace(0, 1, W)
    alpha = np.clip((0.52 - xx) / 0.52, 0.0, 1.0) ** 1.25 * 225
    grad[:, :, 0] = 4
    grad[:, :, 1] = 8
    grad[:, :, 2] = 16
    grad[:, :, 3] = alpha[None, :].astype(np.uint8)
    overlay = Image.alpha_composite(overlay, Image.fromarray(grad))

    d = ImageDraw.Draw(overlay)
    # Top red alert pill (auto-sized from textbbox)
    f_pill = load_font(36)
    pill_txt = "STANFORD × MIT BREAKTHROUGH"
    pbb = d.textbbox((0, 0), pill_txt, font=f_pill)
    pw = (pbb[2] - pbb[0]) + 56
    d.rounded_rectangle([68, 68, 68 + pw, 134], radius=18, fill=(218, 28, 38, 248), outline=(255, 220, 75, 255), width=3)
    d.text((96, 80), pill_txt, font=f_pill, fill=(255, 255, 255, 255))

    # Huge viral left-aligned headline stack
    f_big = load_font(126)
    f_mid = load_font(102)
    f_bot = load_font(108)
    draw_stroked_text(d, (68, 165), "$73 CLAW", f_big, (255, 220, 55, 255), stroke_width=13, shadow_offset=(0, 10))
    draw_stroked_text(d, (68, 308), "ZERO ROBOT", f_mid, (255, 255, 255, 255), stroke_width=11, shadow_offset=(0, 9))
    draw_stroked_text(d, (68, 428), "TRAINING?!", f_bot, (56, 222, 255, 255), stroke_width=12, shadow_offset=(0, 9))

    # Fact sub-box on bottom-left
    d.rounded_rectangle([68, 600, 825, 795], radius=22, fill=(10, 16, 28, 232), outline=(255, 200, 60, 255), width=4)
    f_s1 = load_font(44)
    f_s2 = load_font(40)
    draw_stroked_text(d, (98, 626), "1 GoPro + 2 Tiny Mirrors", f_s1, (115, 238, 255, 255), stroke_width=6, shadow_offset=(0, 4))
    draw_stroked_text(d, (98, 696), "= Instant Human Dexterity!", f_s2, (255, 216, 75, 255), stroke_width=6, shadow_offset=(0, 4))

    # Pointer arrow from sub-box toward the glowing cyan mirror on the handheld UMI claw (around x=1425, y=585)
    d.line([(825, 680), (1385, 595)], fill=(56, 222, 255, 240), width=6)
    d.ellipse([1373, 583, 1397, 607], fill=(255, 220, 55, 255), outline=(0, 0, 0, 255), width=3)

    # Bottom brand strip
    f_brand = load_font(30)
    draw_stroked_text(d, (72, 995), "SMALL SIGNAL STUDIO  •  RSS 2024 FINALIST (UMI)", f_brand, (201, 162, 91, 245), stroke_width=5, shadow_offset=(0, 3))

    out = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    out.save(out_path, optimize=True)
    print(f"Saved 16:9 thumbnail -> {out_path} ({out.size})")

if __name__ == "__main__":
    build_9x16_cover("/tmp/sss002_build/cover_9x16_raw.png", "/home/user/deliverables/SSS-002/SSS-002_Viral_Cover_9x16.jpg")
    build_16x9_thumb("/tmp/sss002_build/thumb_16x9_raw.png", "/home/user/deliverables/SSS-002/SSS-002_Viral_Thumbnail_16x9.png")
