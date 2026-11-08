import os, sys, math, subprocess
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, "/tmp/prod_v2")
from shotlist import SHOTS

W, H = 1080, 1920
FPS = 60.0
TOTAL_FRAMES = 3484  # Frame 0 (cover) + Frames 1..3483 = 58.0667s

BASE_FOOTAGE = ".cache/library/footage"
CLIPS60_DIR = "/tmp/prod_v2/clips60"
COVER_PATH = ".cache/deliverables/SSS-001/SSS-001_Viral_Cover_9x16.jpg"
AUDIO_PATH = "/tmp/prod_v2/master_audio.wav"
OUT_MP4 = ".cache/deliverables/SSS-001/SSS-001_Ghost_Walls_Robot_Parkour_UltraHD_1080p60.mp4"
TMP_MP4 = "/tmp/prod_v2/out_ultrahd_v2.mp4"

FONT_BLACK = os.path.expanduser("~/.local/share/fonts/montserrat-latin-900-normal.ttf")
FONT_EXTRABOLD = os.path.expanduser("~/.local/share/fonts/montserrat-latin-800-normal.ttf")

# Exact 21 synced captions (timestamps in seconds, text lines, gold-highlighted words)
CAPTIONS = [
    (0.080,  2.255, ["NOBODY TAUGHT THIS", "ROBOT HOW TO JUMP."], {"NOBODY", "JUMP."}),
    (2.395,  3.523, ["NO MOTION CAPTURE."], {"NO", "MOTION", "CAPTURE."}),
    (3.663,  4.973, ["JUST ONE NOSE CAMERA."], {"ONE", "NOSE", "CAMERA."}),
    (5.133,  8.325, ["YET IT VAULTS CONCRETE WALLS", "TALLER THAN ITS BODY,"], {"VAULTS", "TALLER"}),
    (8.445,  9.994, ["EVEN IN PITCH DARKNESS."], {"PITCH", "DARKNESS."}),
    (10.174, 13.053, ["IT CRAWLS FLAT UNDER", "20-CM GAPS,"], {"CRAWLS", "20-CM", "GAPS,"}),
    (13.173, 17.124, ["AND TILTS ONTO TWO LEGS", "THROUGH NARROW SLITS."], {"TWO", "LEGS", "NARROW", "SLITS."}),
    (17.324, 19.913, ["MOST ROBOTS CRASH", "THOUSANDS OF TIMES,"], {"CRASH", "THOUSANDS"}),
    (20.033, 22.748, ["STOPPED COLD", "BY SOLID WALLS."], {"STOPPED", "COLD"}),
    (22.908, 26.360, ["SO STANFORD & CMU", "BROKE PHYSICS FIRST."], {"BROKE", "PHYSICS"}),
    (26.559, 30.932, ["FOR 12 HOURS IN SIM,", "WALLS BECAME GHOSTS."], {"12", "HOURS", "GHOSTS."}),
    (31.092, 32.935, ["IT WALKED STRAIGHT", "THROUGH BARRIERS,"], {"STRAIGHT", "THROUGH"}),
    (33.055, 36.059, ["PAYING A PENALTY FOR", "EVERY MM OF OVERLAP."], {"PENALTY", "OVERLAP."}),
    (36.259, 41.177, ["TO ESCAPE IT, THE AI", "INVENTED PARKOUR ALONE,"], {"INVENTED", "PARKOUR", "ALONE,"}),
    (41.317, 44.841, ["BEFORE 6 HOURS OF REAL", "PHYSICS LOCKED IT IN."], {"REAL", "PHYSICS", "LOCKED"}),
    (45.061, 47.780, ["OUTDOORS, SOMETHING", "EERIE EMERGED."], {"EERIE", "EMERGED."}),
    (47.930, 50.053, ["WHEN A BRICK WALL", "STOPS IT COLD..."], {"BRICK", "WALL", "COLD..."}),
    (50.633, 52.290, ["NOBODY CODED A RETRY,"], {"NOBODY", "RETRY,"}),
    (52.410, 55.006, ["YET IT SHOVES OFF STONE", "FOR RUN-UP SPACE,"], {"SHOVES", "RUN-UP", "SPACE,"}),
    (55.126, 57.170, ["AND CLEARS THE LEDGE", "ON THE SECOND CHARGE."], {"CLEARS", "SECOND", "CHARGE."}),
    (57.390, 58.040, ["REMEMBER..."], {"REMEMBER..."}),
]

def render_caption_card(lines, gold_words):
    cw, ch = 980, 260
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    font_size = 54 if max(len(l) for l in lines) <= 22 else 46
    font = ImageFont.truetype(FONT_BLACK, font_size)
    draw_s = ImageDraw.Draw(shadow)
    draw_m = ImageDraw.Draw(img)

    line_h = int(font_size * 1.24)
    total_h = line_h * len(lines)
    y_start = (ch - total_h) // 2

    GOLD = (201, 162, 91, 255)   # #C9A25B warm documentary gold (RGB for PIL)
    WHITE = (255, 255, 255, 255)
    STROKE = (10, 12, 18, 255)

    for li, line in enumerate(lines):
        words = line.split(" ")
        space_w = draw_m.textlength(" ", font=font)
        word_widths = [draw_m.textlength(w, font=font) for w in words]
        line_w = sum(word_widths) + space_w * max(0, len(words) - 1)
        x = (cw - line_w) / 2.0
        y = y_start + li * line_h
        for w_str, ww in zip(words, word_widths):
            color = GOLD if w_str in gold_words else WHITE
            draw_s.text((x + 4, y + 6), w_str, font=font, fill=(0, 0, 0, 210), stroke_width=8, stroke_fill=(0, 0, 0, 210))
            draw_m.text((x, y), w_str, font=font, fill=color, stroke_width=6, stroke_fill=STROKE)
            x += ww + space_w

    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=6))
    combined = Image.alpha_composite(shadow, img)
    arr = np.array(combined)
    # Convert RGBA -> BGRA
    bgra = arr[:, :, [2, 1, 0, 3]].copy()
    return bgra

print("Pre-rendering 21 crisp Montserrat Black caption cards...")
CAPTION_CARDS = []
for s_t, e_t, lines, golds in CAPTIONS:
    CAPTION_CARDS.append((s_t, e_t, render_caption_card(lines, golds)))

# Precompute Ultra-HD optical enhancement helpers
clahe = cv2.createCLAHE(clipLimit=1.65, tileGridSize=(8, 8))
chroma_lut = np.clip((np.arange(256, dtype=np.float32) - 128.0) * 1.06 + 128.0, 0, 255).astype(np.uint8)
luma_lut = np.clip(((np.arange(256, dtype=np.float32) / 255.0) ** 0.97) * 255.0, 0, 255).astype(np.uint8)

# Precompute subtle bottom & top cinema vignette mask (1920, 1, 1) float32
vig = np.ones((H, 1, 1), dtype=np.float32)
for y in range(1260, H):
    t = (y - 1260) / float(H - 1260)
    vig[y, 0, 0] = 1.0 - 0.38 * (t ** 1.35)
for y in range(0, 220):
    t = (220 - y) / 220.0
    vig[y, 0, 0] = 1.0 - 0.16 * (t ** 1.4)

def enhance_ultrahd(bgr):
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l_cl = clahe.apply(l)
    l_mix = cv2.addWeighted(l, 0.56, l_cl, 0.44, 0)
    l_blur = cv2.GaussianBlur(l_mix, (0, 0), 1.22)
    l_sharp = cv2.addWeighted(l_mix, 1.46, l_blur, -0.46, 0)
    l_out = cv2.LUT(l_sharp, luma_lut)
    a_out = cv2.LUT(a, chroma_lut)
    b_out = cv2.LUT(b, chroma_lut)
    out = cv2.cvtColor(cv2.merge((l_out, a_out, b_out)), cv2.COLOR_LAB2BGR)
    # Apply subtle vertical vignette cleanly
    out = (out.astype(np.float32) * vig).astype(np.uint8)
    return out

def crop_and_zoom_9x16(frame, spec, prog, zs, ze):
    fh, fw = frame.shape[:2]
    ease = 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, prog)))
    z = zs + (ze - zs) * ease

    if spec[0] == "pan":
        _, xcs, xce = spec
        xc_frac = xcs + (xce - xcs) * ease
        base_h = fh
        base_w = fh * 9.0 / 16.0
        if base_w > fw:
            base_w = float(fw)
            base_h = fw * 16.0 / 9.0
        cw = base_w / z
        ch = base_h / z
        xc = xc_frac * fw
        yc = fh * 0.50
    else:
        _, xc_px, y0, y1 = spec
        base_h = float(y1 - y0)
        base_w = base_h * 9.0 / 16.0
        cw = base_w / z
        ch = base_h / z
        xc = float(xc_px)
        yc = (y0 + y1) * 0.50

    x0 = int(round(max(0.0, min(fw - cw, xc - cw * 0.5))))
    y0_i = int(round(max(0.0, min(fh - ch, yc - ch * 0.5))))
    x1 = min(fw, x0 + max(16, int(round(cw))))
    y1_i = min(fh, y0_i + max(16, int(round(ch))))
    sub = frame[y0_i:y1_i, x0:x1]
    return cv2.resize(sub, (W, H), interpolation=cv2.INTER_LANCZOS4)

def overlay_caption(frame, t_sec):
    for s_t, e_t, card in CAPTION_CARDS:
        if s_t <= t_sec <= e_t:
            dt = t_sec - s_t
            rem = e_t - t_sec
            alpha_mul = 1.0
            scale = 1.0
            if dt < 0.08:
                p = dt / 0.08
                alpha_mul = p
                scale = 0.94 + 0.06 * p
            elif rem < 0.06:
                alpha_mul = max(0.0, rem / 0.06)

            ch_c, cw_c = card.shape[:2]
            if abs(scale - 1.0) > 1e-3:
                nw = int(round(cw_c * scale))
                nh = int(round(ch_c * scale))
                c_use = cv2.resize(card, (nw, nh), interpolation=cv2.INTER_LINEAR)
            else:
                c_use = card
            uh, uw = c_use.shape[:2]
            x0 = (W - uw) // 2
            y0 = 1365 + (ch_c - uh) // 2
            roi = frame[y0:y0+uh, x0:x0+uw]
            a = (c_use[:, :, 3:4].astype(np.float32) / 255.0) * alpha_mul
            blended = roi.astype(np.float32) * (1.0 - a) + c_use[:, :, :3].astype(np.float32) * a
            frame[y0:y0+uh, x0:x0+uw] = blended.astype(np.uint8)
            break

# Adjust Shot 35 end frame to 3484 so total frames = 3484 (58.0667s)
shots_adj = list(SHOTS)
sf_last, _, rel_last, ss_last, spd_last, spec_last, zs_last, ze_last, note_last = shots_adj[-1]
shots_adj[-1] = (sf_last, TOTAL_FRAMES, rel_last, ss_last, spd_last, spec_last, zs_last, ze_last, note_last)

ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "bgr24",
    "-s", f"{W}x{H}", "-r", "60", "-i", "-",
    "-i", AUDIO_PATH,
    "-map", "0:v:0", "-map", "1:a:0",
    "-c:v", "libx264", "-preset", "veryfast", "-tune", "film",
    "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
    "-b:v", "13.05M", "-maxrate", "14.2M", "-bufsize", "26M",
    "-threads", "3",
    "-x264-params", "rc-lookahead=10:aq-mode=3:aq-strength=1.08:deblock=-1,-1:keyint=120:min-keyint=60",
    "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
    "-movflags", "+faststart",
    TMP_MP4
]

print("Starting FFmpeg Ultra-HD encoder pipe...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

# Write Frame 0 = Viral 9:16 Cover
cover_bgr = cv2.imread(COVER_PATH)
assert cover_bgr is not None and cover_bgr.shape[:2] == (H, W), f"Bad cover: {COVER_PATH}"
proc.stdin.write(cover_bgr.tobytes())

written = 1
for idx_shot, (sf, ef, rel, ss, spd, spec, zs, ze, note) in enumerate(shots_adj, 1):
    interp_p = os.path.join(CLIPS60_DIR, f"shot_{idx_shot:02d}.mp4")
    if os.path.exists(interp_p):
        cap = cv2.VideoCapture(interp_p)
        start_sec = 0.05
    else:
        cap = cv2.VideoCapture(os.path.join(BASE_FOOTAGE, rel))
        start_sec = ss

    src_fps = cap.get(cv2.CAP_PROP_FPS) or 60.0
    src_n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    start_f_src = min(max(0, int(round(start_sec * src_fps))), max(0, src_n - 1))
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_f_src)

    n_out = ef - sf
    last_good = None
    src_pos = start_f_src
    for k in range(n_out):
        g_frame = sf + k
        t_sec = g_frame / FPS
        target_src_f = start_f_src + int(round((k / FPS) * spd * src_fps))
        while src_pos <= target_src_f:
            ok, frm = cap.read()
            if ok and frm is not None:
                last_good = frm
                src_pos += 1
            else:
                break
        assert last_good is not None, f"Failed reading shot {idx_shot} ({rel})"
        prog = k / float(max(1, n_out - 1))
        out_frm = crop_and_zoom_9x16(last_good, spec, prog, zs, ze)
        out_frm = enhance_ultrahd(out_frm)
        # Subtle 2-frame optical flash/contrast micro-pop at hard action cuts
        if k == 0 and idx_shot > 1:
            out_frm = cv2.convertScaleAbs(out_frm, alpha=1.04, beta=3)
        overlay_caption(out_frm, t_sec)
        proc.stdin.write(out_frm.tobytes())
        written += 1

    cap.release()
    if idx_shot % 5 == 0 or idx_shot == len(shots_adj):
        print(f"Rendered Shot {idx_shot:02d}/{len(shots_adj)} -> frame {written}/{TOTAL_FRAMES} ({note})")

proc.stdin.close()
stderr_bytes = proc.stderr.read()
rc = proc.wait()
if rc != 0:
    print(stderr_bytes.decode("utf-8", errors="replace")[-2000:])
    sys.exit(rc)

os.replace(TMP_MP4, OUT_MP4)
print(f"DONE! Wrote {written} frames to {OUT_MP4}, size={os.path.getsize(OUT_MP4):,} bytes")
