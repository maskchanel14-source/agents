#!/usr/bin/env python3
"""Generate viral, dramatic, 100% honest Dark Science 9:16 Cover & 16:9 Thumbnail for SSS-003."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def load_font(size: int):
    return ImageFont.truetype(FONT_BOLD, size)

def draw_stroked_text(draw, pos, text, font, fill, stroke_fill=(0, 0, 0, 255), stroke_width=8, shadow_offset=(0, 8)):
    x, y = pos
    if shadow_offset:
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font,
                  fill=(0, 0, 0, 220), stroke_width=stroke_width + 4, stroke_fill=(0, 0, 0, 220))
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)

def draw_centered_stroked(draw, canvas_w, y, text, font, fill, stroke_width=10):
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    tw = bbox[2] - bbox[0]
    x = (canvas_w - tw) // 2
    draw_stroked_text(draw, (x, y), text, font, fill, stroke_width=stroke_width)
    return x, tw

def build_9x16_cover(raw_path: str, out_path: str):
    W, H = 1080, 1920
    raw = Image.open(raw_path).convert("RGB")
    rw, rh = raw.size
    # Crop active eye photography zone (y: 22%..78.5%) and feather top/bottom seamlessly
    y0, y1 = int(rh * 0.22), int(rh * 0.785)
    core = raw.crop((0, y0, rw, y1))
    ch = int(W * (core.height / core.width))
    core = core.resize((W, ch), Image.Resampling.LANCZOS)
    core = ImageEnhance.Contrast(core).enhance(1.16)
    core = ImageEnhance.Color(core).enhance(1.15)
    core = ImageEnhance.Sharpness(core).enhance(1.25)

    yy, xx = np.mgrid[0:H, 0:W]
    glow_c = np.exp(-((xx - 540)**2 + (yy - 880)**2) / (2 * 410**2))
    arr_bg = np.zeros((H, W, 3), dtype=np.float32)
    arr_bg[:, :, 0] = 4 + 18 * glow_c
    arr_bg[:, :, 1] = 8 + 38 * glow_c
    arr_bg[:, :, 2] = 15 + 55 * glow_c
    canvas = Image.fromarray(np.clip(arr_bg, 0, 255).astype(np.uint8))

    paste_y = 405
    mask = np.ones((ch, W), dtype=np.float32)
    feather = 145
    mask[:feather, :] = np.linspace(0.0, 1.0, feather)[:, None] ** 1.45
    mask[-feather:, :] = np.linspace(1.0, 0.0, feather)[:, None] ** 1.45
    canvas.paste(core, (0, paste_y), Image.fromarray((mask * 255).astype(np.uint8)))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Top crimson/gold Dark Science alert pill (auto-sized)
    f_badge = load_font(32)
    badge_txt = "DARK SCIENCE  •  CVPR 2024 ORAL"
    bb = d.textbbox((0, 0), badge_txt, font=f_badge)
    bw = (bb[2] - bb[0]) + 58
    bx = (W - bw) // 2
    by = 76
    d.rounded_rectangle([bx, by, bx + bw, by + 56], radius=28, fill=(210, 24, 42, 246), outline=(255, 216, 75, 255), width=3)
    d.text((bx + 29, by + 10), badge_txt, font=f_badge, fill=(255, 255, 255, 255))

    # Giant 3-line explosive headline
    draw_centered_stroked(d, W, 148, "ZOOM INTO", load_font(96), (255, 220, 55, 255), stroke_width=11)
    draw_centered_stroked(d, W, 252, "ANY SELFIE?!", load_font(92), (255, 255, 255, 255), stroke_width=11)
    draw_centered_stroked(d, W, 352, "SEE THE ROOM!", load_font(86), (64, 224, 255, 255), stroke_width=10)

    # Callout badge pointing into the 3D reflection inside the cornea
    f_call = load_font(28)
    call_txt = "7.8mm CORNEA = SECURITY MIRROR"
    cbb = d.textbbox((0, 0), call_txt, font=f_call)
    cbw = (cbb[2] - cbb[0]) + 46
    cbx = (W - cbw) // 2
    cby = 1208
    d.rounded_rectangle([cbx, cby, cbx + cbw, cby + 56], radius=16, fill=(7, 18, 30, 240), outline=(64, 224, 255, 255), width=3)
    d.text((cbx + 23, cby + 11), call_txt, font=f_call, fill=(120, 240, 255, 255))
    d.line([(W // 2, cby), (540, 920)], fill=(64, 224, 255, 235), width=5)
    d.ellipse([529, 909, 551, 931], fill=(255, 220, 55, 255), outline=(0, 0, 0, 255), width=3)

    # Bottom dramatic shock box (safely above Shorts UI y=1540)
    d.rounded_rectangle([54, 1295, W - 54, 1482], radius=24, fill=(10, 13, 22, 240), outline=(255, 200, 58, 255), width=4)
    draw_centered_stroked(d, W, 1318, "3D AI REBUILDS WHO STOOD", load_font(42), (255, 255, 255, 255), stroke_width=6)
    draw_centered_stroked(d, W, 1384, "BEHIND YOUR CAMERA!", load_font(52), (255, 214, 62, 255), stroke_width=7)

    draw_centered_stroked(d, W, 1515, "SMALL SIGNAL STUDIO  •  ARXIV:2306.09348", load_font(26), (201, 162, 91, 242), stroke_width=4)

    out = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    out.save(out_path, quality=96, subsampling=0)
    print(f"Saved 9:16 cover -> {out_path} ({out.size})")

def build_16x9_thumb(raw_path: str, out_path: str):
    W, H = 1920, 1080
    raw = Image.open(raw_path).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    # Crop right side (x: 41.8%..100%) where the macro eye lives and feather its left edge smoothly into dark obsidian canvas!
    eye_x0 = int(W * 0.418)
    eye_crop = raw.crop((eye_x0, 0, W, H))
    # Stretch slightly to cover right 66% (x=650..1920) so there is zero hard seam
    ew = W - 640
    eye_part = eye_crop.resize((ew, H), Image.Resampling.LANCZOS)
    eye_part = ImageEnhance.Contrast(eye_part).enhance(1.16)
    eye_part = ImageEnhance.Color(eye_part).enhance(1.16)
    eye_part = ImageEnhance.Sharpness(eye_part).enhance(1.22)

    canvas = Image.new("RGB", (W, H), (5, 8, 15))
    mask = np.ones((H, ew), dtype=np.float32)
    feather_x = 260
    mask[:, :feather_x] = (np.linspace(0.0, 1.0, feather_x)[None, :]) ** 1.5
    canvas.paste(eye_part, (640, 0), Image.fromarray((mask * 255).astype(np.uint8)))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Top crimson alert pill (auto-sized)
    f_pill = load_font(34)
    pill_txt = "UNIV. OF MARYLAND  •  DARK TECH"
    pbb = d.textbbox((0, 0), pill_txt, font=f_pill)
    pw = (pbb[2] - pbb[0]) + 56
    d.rounded_rectangle([64, 66, 64 + pw, 130], radius=18, fill=(212, 24, 42, 248), outline=(255, 218, 75, 255), width=3)
    d.text((92, 78), pill_txt, font=f_pill, fill=(255, 255, 255, 255))

    # Huge viral left-aligned headline stack
    draw_stroked_text(d, (64, 162), "YOUR EYES", load_font(118), (255, 220, 55, 255), stroke_width=13, shadow_offset=(0, 10))
    draw_stroked_text(d, (64, 298), "BETRAY THE", load_font(102), (255, 255, 255, 255), stroke_width=11, shadow_offset=(0, 9))
    draw_stroked_text(d, (64, 418), "HIDDEN ROOM", load_font(100), (64, 224, 255, 255), stroke_width=11, shadow_offset=(0, 9))

    # Fact sub-box on bottom-left
    d.rounded_rectangle([64, 595, 815, 792], radius=22, fill=(9, 15, 26, 236), outline=(255, 200, 60, 255), width=4)
    draw_stroked_text(d, (94, 622), "7.8mm Cornea + 3D NeRF AI", load_font(42), (115, 238, 255, 255), stroke_width=6, shadow_offset=(0, 4))
    draw_stroked_text(d, (94, 692), "= Sees Behind Every Selfie!", load_font(41), (255, 216, 75, 255), stroke_width=6, shadow_offset=(0, 4))

    # Pointer line to the glowing 3D cameraman inside the eye reflection
    d.line([(815, 685), (1145, 560)], fill=(64, 224, 255, 240), width=6)
    d.ellipse([1133, 548, 1157, 572], fill=(255, 220, 55, 255), outline=(0, 0, 0, 255), width=3)

    draw_stroked_text(d, (68, 995), "SMALL SIGNAL STUDIO  •  CVPR 2024 ORAL (ARXIV:2306.09348)", load_font(29), (201, 162, 91, 245), stroke_width=5, shadow_offset=(0, 3))

    out = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    out.save(out_path, optimize=True)
    print(f"Saved 16:9 thumbnail -> {out_path} ({out.size})")

if __name__ == "__main__":
    build_9x16_cover("/tmp/sss003_build/cover_9x16_raw.png", "/home/user/deliverables/SSS-003/SSS-003_Viral_Cover_9x16.jpg")
    build_16x9_thumb("/tmp/sss003_build/thumb_16x9_raw.png", "/home/user/deliverables/SSS-003/SSS-003_Viral_Thumbnail_16x9.png")
