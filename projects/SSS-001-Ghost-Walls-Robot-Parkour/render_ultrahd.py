#!/usr/bin/env python3
"""True Native-Pixel 1080p60 Documentary Cinema Renderer for SSS-001.

Presents every research clip inside a 1:1 native-pixel cinema viewport (1036x780 / 1036x583)
over a live ambient dark-glass studio canvas with pure 1080x1920 vector chapter headers and
Montserrat Black captions — zero 480p clips, zero 400% vertical blow-ups, and zero `minterpolate`
warping artifacts.
"""
from __future__ import annotations

import math
import os
import subprocess
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from shotlist import CHAPTERS, SHOTS, TOTAL_FRAMES, verify_manifest

W, H = 1080, 1920
FPS = 60.0

BASE_FOOTAGE = ".cache/library/footage"
COVER_PATH = ".cache/deliverables/SSS-001/SSS-001_Viral_Cover_9x16.jpg"
AUDIO_PATH = "/tmp/prod_v3/master_audio.wav"
OUT_MP4 = ".cache/deliverables/SSS-001/SSS-001_Ghost_Walls_Robot_Parkour_UltraHD_1080p60.mp4"
TMP_MP4 = "/tmp/prod_v3/out_cinema_1080p60.mp4"

FONT_BLACK = os.path.expanduser("~/.local/share/fonts/montserrat-latin-900-normal.ttf")
FONT_BOLD = os.path.expanduser("~/.local/share/fonts/montserrat-latin-700-normal.ttf")

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


def rgba_to_bgra(pil_img: Image.Image) -> np.ndarray:
    arr = np.array(pil_img)
    return arr[:, :, [2, 1, 0, 3]].copy()


def build_header_card(eyebrow_tag: str, title_str: str, badge_str: str) -> np.ndarray:
    cw, ch = W, 220
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_eye = ImageFont.truetype(FONT_BOLD, 21)
    f_tit = ImageFont.truetype(FONT_BLACK, 38)
    f_bad = ImageFont.truetype(FONT_BOLD, 19)

    GOLD = (201, 162, 91, 255)
    eye_full = f"SMALL SIGNAL STUDIO  •  {eyebrow_tag}"
    ew = draw.textlength(eye_full, font=f_eye)
    draw.text(((cw - ew) / 2.0, 18), eye_full, font=f_eye, fill=GOLD)

    tw = draw.textlength(title_str, font=f_tit)
    draw.text(((cw - tw) / 2.0, 54), title_str, font=f_tit, fill=(247, 249, 253, 255))

    bw = draw.textlength(badge_str, font=f_bad) + 40
    bx = (cw - bw) / 2.0
    by = 114
    draw.rounded_rectangle([bx, by, bx + bw, by + 36], radius=18, fill=(18, 23, 33, 235), outline=(201, 162, 91, 145), width=1)
    draw.text((bx + 20, by + 7), badge_str, font=f_bad, fill=(216, 224, 238, 255))
    return rgba_to_bgra(img)


def build_caption_card(lines: list[str], gold_words: set[str]) -> np.ndarray:
    cw, ch = 1000, 230
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    fs = 52 if max(len(l) for l in lines) <= 22 else 45
    font = ImageFont.truetype(FONT_BLACK, fs)
    ds = ImageDraw.Draw(sh)
    dm = ImageDraw.Draw(img)

    lh = int(fs * 1.25)
    y0 = (ch - lh * len(lines)) // 2
    GOLD = (201, 162, 91, 255)
    WHITE = (255, 255, 255, 255)
    STROKE = (8, 10, 16, 255)

    for li, line in enumerate(lines):
        words = line.split(" ")
        sp = dm.textlength(" ", font=font)
        wws = [dm.textlength(w, font=font) for w in words]
        lw = sum(wws) + sp * max(0, len(words) - 1)
        x = (cw - lw) / 2.0
        y = y0 + li * lh
        for w_s, ww in zip(words, wws):
            col = GOLD if w_s in gold_words else WHITE
            ds.text((x + 3, y + 5), w_s, font=font, fill=(0, 0, 0, 210), stroke_width=8, stroke_fill=(0, 0, 0, 210))
            dm.text((x, y), w_s, font=font, fill=col, stroke_width=6, stroke_fill=STROKE)
            x += ww + sp

    sh = sh.filter(ImageFilter.GaussianBlur(radius=5))
    return rgba_to_bgra(Image.alpha_composite(sh, img))


def build_stage_frame(vw: int, vh: int, vy: int) -> tuple[int, int, np.ndarray, np.ndarray]:
    """Precomputes rounded mask (vh, vw, 1) float32 and full-width bezel+shadow BGRA strip."""
    vx = (W - vw) // 2
    mask_pil = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(mask_pil).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=22, fill=255)
    mask_f = (np.array(mask_pil, dtype=np.float32) / 255.0)[:, :, None]

    pad_y = 40
    ow, oh = W, vh + pad_y * 2
    sh = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([vx - 3, pad_y + 10, vx + vw + 3, pad_y + vh + 18], radius=24, fill=(0, 0, 0, 220))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=16))
    cut = Image.new("L", (ow, oh), 255)
    ImageDraw.Draw(cut).rounded_rectangle([vx, pad_y, vx + vw - 1, pad_y + vh - 1], radius=22, fill=0)
    sh.putalpha(Image.composite(sh.split()[3], Image.new("L", (ow, oh), 0), cut))

    bezel = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bezel)
    bd.rounded_rectangle([vx, pad_y, vx + vw - 1, pad_y + vh - 1], radius=22, outline=(76, 88, 110, 215), width=2)
    overlay = rgba_to_bgra(Image.alpha_composite(sh, bezel))
    return vx, vy, mask_f, overlay


def alpha_blit(dst: np.ndarray, src_bgra: np.ndarray, x0: int, y0: int, alpha_mul: float = 1.0) -> None:
    sh_h, sh_w = src_bgra.shape[:2]
    roi = dst[y0:y0 + sh_h, x0:x0 + sh_w]
    a = (src_bgra[:, :, 3:4].astype(np.float32) / 255.0) * alpha_mul
    dst[y0:y0 + sh_h, x0:x0 + sh_w] = (roi.astype(np.float32) * (1.0 - a) + src_bgra[:, :, :3].astype(np.float32) * a).astype(np.uint8)


def main() -> None:
    verify_manifest(BASE_FOOTAGE)
    os.makedirs(os.path.dirname(TMP_MP4), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_MP4), exist_ok=True)

    print("Pre-rendering vector 1080p headers, cinema bezels, and caption cards...")
    headers = [build_header_card(*c) for c in CHAPTERS]
    captions = [(s, e, build_caption_card(lines, golds)) for s, e, lines, golds in CAPTIONS]

    stage43_vx, stage43_vy = (W - 1036) // 2, 382
    _, _, mask43, bezel43 = build_stage_frame(1036, 780, stage43_vy)

    stage169_vx, stage169_vy = (W - 1036) // 2, 478
    _, _, mask169, bezel169 = build_stage_frame(1036, 583, stage169_vy)

    # Precompute subtle studio dot-grid mask
    dot_grid = np.zeros((H, W, 3), dtype=np.uint8)
    for gy in range(72, H - 72, 36):
        dot_grid[gy:gy + 2, 54:W - 54:36, :] = 12

    chroma_lut = np.clip((np.arange(256, dtype=np.float32) - 128.0) * 1.05 + 128.0, 0, 255).astype(np.uint8)

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
        "-x264-params", "rc-lookahead=10:aq-mode=3:aq-strength=1.05:deblock=-1,-1:keyint=120:min-keyint=60",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart",
        TMP_MP4,
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    # Frame 0: Viral 9:16 Cover for YouTube Mobile's Shorts picker
    cover_bgr = cv2.imread(COVER_PATH)
    assert cover_bgr is not None and cover_bgr.shape[:2] == (H, W), f"Missing cover {COVER_PATH}"
    proc.stdin.write(cover_bgr.tobytes())
    written = 1

    for idx_shot, (sf, ef, rel, ss, spd, spec, zs, ze, chap_idx, scene_id) in enumerate(SHOTS, 1):
        cap = cv2.VideoCapture(os.path.join(BASE_FOOTAGE, rel))
        src_fps = cap.get(cv2.CAP_PROP_FPS) or 60.0
        src_n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        start_f_src = min(max(0, int(round(ss * src_fps))), max(0, src_n - 1))
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
            assert last_good is not None, f"Decode failure on {rel}"

            # 1. Live ambient dark-glass studio canvas
            amb_small = cv2.GaussianBlur(cv2.resize(last_good, (180, 320), interpolation=cv2.INTER_AREA), (35, 35), 14)
            amb = cv2.resize(amb_small, (W, H), interpolation=cv2.INTER_LINEAR)
            canvas = cv2.convertScaleAbs(amb, alpha=0.16, beta=11)
            canvas = cv2.add(canvas, dot_grid)

            # 2. Native-pixel Cinema Stage extraction + clean fine-radius optical sharpen
            prog = k / float(max(1, n_out - 1))
            ease = 0.5 - 0.5 * math.cos(math.pi * prog)
            z = zs + (ze - zs) * ease

            fh_full, fw = last_good.shape[:2]
            if spec[0] == "grid169":
                vw, vh, vx, vy = 1036, 583, stage169_vx, stage169_vy
                mask_use, bezel_use = mask169, bezel169
                cw = fw / z
                ch = fh_full / z
                x0 = int(round((fw - cw) * 0.5))
                y0 = int(round((fh_full - ch) * 0.5))
                sub = last_good[y0:y0 + int(round(ch)), x0:x0 + int(round(cw))]
            else:
                _, xcs, xce, ymax_f = spec
                vw, vh, vx, vy = 1036, 780, stage43_vx, stage43_vy
                mask_use, bezel_use = mask43, bezel43
                fh = int(round(fh_full * ymax_f))
                raw_sub = last_good[:fh, :]
                base_w = min(float(fw), fh * (vw / float(vh)))
                base_h = base_w * (vh / float(vw))
                cw = base_w / z
                ch = base_h / z
                xc = (xcs + (xce - xcs) * ease) * fw
                yc = fh * 0.50
                x0 = int(round(max(0.0, min(fw - cw, xc - cw * 0.5))))
                y0 = int(round(max(0.0, min(fh - ch, yc - ch * 0.5))))
                sub = raw_sub[y0:y0 + max(16, int(round(ch))), x0:x0 + max(16, int(round(cw)))]

            vid = cv2.resize(sub, (vw, vh), interpolation=cv2.INTER_LANCZOS4)
            lab = cv2.cvtColor(vid, cv2.COLOR_BGR2LAB)
            l_ch, a_ch, b_ch = cv2.split(lab)
            l_sh = cv2.addWeighted(l_ch, 1.24, cv2.GaussianBlur(l_ch, (0, 0), 0.90), -0.24, 0)
            vid = cv2.cvtColor(cv2.merge((l_sh, cv2.LUT(a_ch, chroma_lut), cv2.LUT(b_ch, chroma_lut))), cv2.COLOR_LAB2BGR)

            # Composite shadow/bezel + rounded video stage
            alpha_blit(canvas, bezel_use, 0, vy - 40)
            roi_v = canvas[vy:vy + vh, vx:vx + vw]
            canvas[vy:vy + vh, vx:vx + vw] = (roi_v.astype(np.float32) * (1.0 - mask_use) + vid.astype(np.float32) * mask_use).astype(np.uint8)
            # Re-draw crisp 2px border on top of rounded edge
            alpha_blit(canvas, bezel_use, 0, vy - 40, 0.55)

            # Subtle 2px gold progress bar along bottom edge of cinema stage
            prog_w = max(4, int(round((vw - 36) * (g_frame / float(TOTAL_FRAMES)))))
            canvas[vy + vh - 3:vy + vh - 1, vx + 18:vx + 18 + prog_w] = (91, 162, 201)

            # 3. Crisp 1080p Vector Chapter Header
            alpha_blit(canvas, headers[chap_idx], 0, 145)

            # 4. Crisp 1080p Vector Caption Deck (below cinema stage, never blocking robot!)
            cap_y = 1235 if spec[0] != "grid169" else 1145
            for s_t, e_t, card in captions:
                if s_t <= t_sec <= e_t:
                    dt = t_sec - s_t
                    rem = e_t - t_sec
                    am = 1.0
                    if dt < 0.07:
                        am = dt / 0.07
                    elif rem < 0.05:
                        am = max(0.0, rem / 0.05)
                    alpha_blit(canvas, card, (W - card.shape[1]) // 2, cap_y, am)
                    break

            proc.stdin.write(canvas.tobytes())
            written += 1

        cap.release()
        if idx_shot % 5 == 0 or idx_shot == len(SHOTS):
            print(f"Rendered Shot {idx_shot:02d}/{len(SHOTS)} -> frame {written}/{TOTAL_FRAMES} ({scene_id})")

    proc.stdin.close()
    stderr_b = proc.stderr.read()
    rc = proc.wait()
    if rc != 0:
        print(stderr_b.decode("utf-8", errors="replace")[-2000:])
        sys.exit(rc)

    os.replace(TMP_MP4, OUT_MP4)
    print(f"SUCCESS! Wrote {written} native-pixel 1080p60 frames -> {OUT_MP4} ({os.path.getsize(OUT_MP4):,} bytes)")


if __name__ == "__main__":
    main()
