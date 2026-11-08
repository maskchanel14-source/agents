#!/usr/bin/env python3
"""
SSS-002 Ultra-HD 1:1 Native-Pixel 1080p60 Documentary Cinema Renderer (v4).
Renders 3,485 frames (58.0833s @ 60.00fps) at 1080x1920, muxed with -14.0 LUFS stereo mix.
Zero scene repeats across 36 native-1080p shots, zero minterpolate, Frame 0 viral 9:16 cover.
Uses fast uint16 ROI alpha-blending and streaming decode for low-memory, high-speed rendering.
"""
import json
import os
import subprocess
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from shotlist import FOOTAGE_DIR, SHOTS, validate_shotlist

W, H = 1080, 1920
FPS = 60
STAGE_W = 1036
STAGE_X = (W - STAGE_W) // 2  # 22

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

HIGHLIGHT_TOKENS = {
    "$73", "$40,000", "GoPro.", "GoPro's", "GoPro", "3D-printed", "3D",
    "zero-shot.", "mirrors", "millisecond", "mustard", "blackouts,", "fountain.", "Remember..."
}

def fnt(path: str, size: int):
    return ImageFont.truetype(path, size)

F_BRAND = fnt(FONT_MONO, 21)
F_HDR = fnt(FONT_BOLD, 50)
F_SUBHDR = fnt(FONT_MONO, 22)
F_TELEM = fnt(FONT_MONO, 21)
F_CAP = fnt(FONT_BOLD, 39)
F_ALERT = fnt(FONT_MONO, 25)

def unsharp_luma(bgr: np.ndarray, sigma: float = 0.88, amount: float = 0.25) -> np.ndarray:
    """Fine-radius luma micro-polish at native stage resolution (zero haloing)."""
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    y = ycrcb[:, :, 0].astype(np.float32)
    blur = cv2.GaussianBlur(y, (0, 0), sigmaX=sigma, sigmaY=sigma)
    ycrcb[:, :, 0] = np.clip(y + amount * (y - blur), 0, 255).astype(np.uint8)
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

def blend_roi_inplace(dst_bgr: np.ndarray, y0: int, fg_bgr: np.ndarray, alpha_u16: np.ndarray):
    """Fast integer alpha blend of an (h, W, 3) strip onto dst_bgr[y0:y0+h] in-place."""
    h = fg_bgr.shape[0]
    roi = dst_bgr[y0:y0 + h].astype(np.uint16)
    out = (roi * (255 - alpha_u16) + fg_bgr * alpha_u16 + 127) // 255
    dst_bgr[y0:y0 + h] = out.astype(np.uint8)

def rgba_to_u16(pil_img: Image.Image) -> tuple:
    arr = np.array(pil_img, dtype=np.uint16)
    bgr = arr[:, :, :3][:, :, ::-1].copy()
    alpha = arr[:, :, 3:4].copy()
    return bgr, alpha

def build_hud_strips(shot_tuple, stage_y: int, stage_h: int) -> dict:
    """Pre-render crisp RGBA HUD bands as compact uint16 strips for blazing-fast compositing."""
    idx, t0, t1, fn, src_t0, crop_b, beat, hdr_title, telem_tag = shot_tuple
    hud = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(hud)

    # 1. Top Small Signal Studio pill (y=118..162)
    pill_txt = "SMALL SIGNAL STUDIO  •  STANFORD × COLUMBIA × MIT"
    pbb = d.textbbox((0, 0), pill_txt, font=F_BRAND)
    pw = (pbb[2] - pbb[0]) + 62
    px = (W - pw) // 2
    py = 118
    d.rounded_rectangle([px, py, px + pw, py + 44], radius=22, fill=(10, 15, 26, 228), outline=(201, 162, 91, 195), width=2)
    dot_col = (235, 59, 90, 255) if beat == 7 else (56, 222, 255, 255)
    d.ellipse([px + 18, py + 15, px + 32, py + 29], fill=dot_col)
    d.text((px + 42, py + 10), pill_txt, font=F_BRAND, fill=(226, 232, 240, 245))

    # 2. Bold Beat Headline (y=182)
    hbb = d.textbbox((0, 0), hdr_title, font=F_HDR)
    hw = hbb[2] - hbb[0]
    hx = (W - hw) // 2
    hy = 182
    d.text((hx + 3, hy + 4), hdr_title, font=F_HDR, fill=(0, 0, 0, 215))
    hdr_col = (255, 214, 70, 255) if beat in (1, 4, 8) else ((255, 107, 107, 255) if beat in (2, 7) else (248, 250, 252, 255))
    d.text((hx, hy), hdr_title, font=F_HDR, fill=hdr_col)

    # 3. Segmented 8-Beat Story Progress Rail (y=258)
    rail_w = 760
    rail_x = (W - rail_w) // 2
    seg_gap = 8
    seg_w = (rail_w - seg_gap * 7) // 8
    for b_i in range(1, 9):
        sx = rail_x + (b_i - 1) * (seg_w + seg_gap)
        if b_i < beat:
            col = (201, 162, 91, 220)
        elif b_i == beat:
            col = (56, 222, 255, 255) if beat != 7 else (235, 59, 90, 255)
        else:
            col = (42, 54, 72, 175)
        d.rounded_rectangle([sx, 258, sx + seg_w, 266], radius=4, fill=col)

    # 4. Telemetry Header Strip directly above Cinema Stage
    bar_y = stage_y - 44
    d.rounded_rectangle([STAGE_X, bar_y, STAGE_X + STAGE_W, stage_y + 6], radius=12,
                        fill=(10, 15, 26, 238), outline=(52, 68, 92, 210), width=2)
    left_tag = f"SHOT {idx:02d}/36  •  1080P NATIVE"
    d.text((STAGE_X + 18, bar_y + 10), left_tag, font=F_TELEM, fill=(201, 162, 91, 245))
    tbb = d.textbbox((0, 0), telem_tag, font=F_TELEM)
    tw = tbb[2] - tbb[0]
    r_col = (255, 120, 120, 255) if beat == 7 else (105, 232, 255, 245)
    d.text((STAGE_X + STAGE_W - tw - 18, bar_y + 10), telem_tag, font=F_TELEM, fill=r_col)

    # 5. Precision Brushed-Gold & Slate Bezel around Cinema Stage + Corner L-Ticks
    border_col = (235, 59, 90, 235) if beat == 7 else (201, 162, 91, 220)
    d.rectangle([STAGE_X - 2, stage_y - 2, STAGE_X + STAGE_W + 1, stage_y + stage_h + 1],
                outline=border_col, width=2)
    tick = 22
    t_col = (255, 220, 75, 255) if beat != 7 else (255, 95, 95, 255)
    for cx, cy, dx, dy in [
        (STAGE_X - 4, stage_y - 4, 1, 1),
        (STAGE_X + STAGE_W + 3, stage_y - 4, -1, 1),
        (STAGE_X - 4, stage_y + stage_h + 3, 1, -1),
        (STAGE_X + STAGE_W + 3, stage_y + stage_h + 3, -1, -1),
    ]:
        d.line([(cx, cy), (cx + dx * tick, cy)], fill=t_col, width=4)
        d.line([(cx, cy), (cx, cy + dy * tick)], fill=t_col, width=4)

    # 6. Bottom citation watermark safely above Shorts UI (y=1472)
    cit_txt = "SOURCE: CHI ET AL., RSS 2024 FINALIST  •  ARXIV:2402.10329"
    cbb = d.textbbox((0, 0), cit_txt, font=F_BRAND)
    cw = cbb[2] - cbb[0]
    d.text(((W - cw) // 2, 1472), cit_txt, font=F_BRAND, fill=(148, 163, 184, 185))

    top_bgr, top_a = rgba_to_u16(hud.crop((0, 110, W, 276)))
    st_y0, st_y1 = bar_y - 4, stage_y + stage_h + 10
    st_bgr, st_a = rgba_to_u16(hud.crop((0, st_y0, W, st_y1)))
    cit_bgr, cit_a = rgba_to_u16(hud.crop((0, 1466, W, 1506)))
    return {
        "top": (110, top_bgr, top_a),
        "stage": (st_y0, st_bgr, st_a),
        "cit": (1466, cit_bgr, cit_a),
    }

def render_caption_box(cap_text: str, progress: float, is_alert: bool = False) -> tuple:
    strip_h = 210
    img = Image.new("RGBA", (W, strip_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bx0, bx1 = 40, W - 40
    by0, by1 = 8, 196
    outline_col = (235, 59, 90, 235) if is_alert else (201, 162, 91, 210)
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=22, fill=(8, 12, 22, 232), outline=outline_col, width=2)

    lines = cap_text.split("\n")
    line_h = 54
    total_th = len(lines) * line_h
    start_y = by0 + (by1 - by0 - 12 - total_th) // 2

    for l_i, line in enumerate(lines):
        words = line.split(" ")
        space_w = d.textbbox((0, 0), " ", font=F_CAP)[2]
        w_widths = [d.textbbox((0, 0), w, font=F_CAP)[2] for w in words]
        line_w = sum(w_widths) + space_w * max(0, len(words) - 1)
        cur_x = (W - line_w) // 2
        cur_y = start_y + l_i * line_h
        for w_str, ww in zip(words, w_widths):
            clean = w_str.strip(",.?!:")
            if w_str in HIGHLIGHT_TOKENS or clean in ("$73", "$40,000", "GoPro", "3D-printed", "3D", "zero-shot", "mirrors", "millisecond", "mustard", "blackouts", "fountain", "Remember"):
                w_col = (255, 216, 68, 255) if "$" in w_str or clean in ("mustard", "Remember", "zero-shot") else (86, 226, 255, 255)
            else:
                w_col = (248, 250, 252, 255)
            d.text((cur_x + 2, cur_y + 3), w_str, font=F_CAP, fill=(0, 0, 0, 220))
            d.text((cur_x, cur_y), w_str, font=F_CAP, fill=w_col)
            cur_x += ww + space_w

    p_x0, p_x1 = bx0 + 24, bx1 - 24
    p_w = int((p_x1 - p_x0) * np.clip(progress, 0.02, 1.0))
    d.rounded_rectangle([p_x0, by1 - 12, p_x1, by1 - 6], radius=3, fill=(38, 48, 66, 200))
    bar_col = (235, 59, 90, 255) if is_alert else (201, 162, 91, 255)
    d.rounded_rectangle([p_x0, by1 - 12, p_x0 + max(8, p_w), by1 - 6], radius=3, fill=bar_col)
    return rgba_to_u16(img)

def render_silence_banner() -> tuple:
    strip_h = 210
    img = Image.new("RGBA", (W, strip_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([58, 28, W - 58, 156], radius=20, fill=(28, 8, 14, 238), outline=(245, 75, 95, 255), width=3)
    txt1 = "[ UNSCRIPTED HUMAN SABOTAGE ]"
    txt2 = "ZERO RETRY CODE IN SYSTEM..."
    bb1 = d.textbbox((0, 0), txt1, font=F_ALERT)
    bb2 = d.textbbox((0, 0), txt2, font=F_SUBHDR)
    d.text(((W - (bb1[2] - bb1[0])) // 2, 48), txt1, font=F_ALERT, fill=(255, 110, 120, 255))
    d.text(((W - (bb2[2] - bb2[0])) // 2, 100), txt2, font=F_SUBHDR, fill=(255, 220, 95, 255))
    return rgba_to_u16(img)

class StreamShotDecoder:
    """Lightweight sequential OpenCV decoder keeping only 2 frames in RAM at any instant."""
    def __init__(self, path: str, start_sec: float):
        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        start_idx = max(0, int(round(start_sec * self.fps)))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_idx)
        self.cur_idx = start_idx
        ok, fr = self.cap.read()
        if not ok:
            raise RuntimeError(f"Cannot decode {path} at {start_sec}s")
        self.cur_frame = fr

    def get_at(self, src_t: float) -> np.ndarray:
        target_idx = max(self.cur_idx, int(round(src_t * self.fps)))
        while self.cur_idx < target_idx:
            ok, fr = self.cap.read()
            if not ok:
                break
            self.cur_frame = fr
            self.cur_idx += 1
        return self.cur_frame

    def close(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

def main():
    validate_shotlist()
    t_start_wall = time.time()

    with open("projects/SSS-002-Universal-Manipulation-Interface/timings.json", "r", encoding="utf-8") as f:
        timings = json.load(f)
    total_frames = timings["total_frames_60fps"]
    sil_s, sil_e = timings["silence_window"]
    captions = timings["captions"]

    cover_bgr = cv2.imread("/home/user/deliverables/SSS-002/SSS-002_Viral_Cover_9x16.jpg")
    assert cover_bgr is not None and cover_bgr.shape == (H, W, 3), "Invalid 9:16 cover!"

    out_mp4 = "/home/user/deliverables/SSS-002/SSS-002_Universal_Manipulation_Interface_UltraHD_1080p60.mp4"
    audio_wav = "/tmp/sss002_build/master_mix.wav"
    ff_log = open("/tmp/sss002_build/ffmpeg_render.log", "w")

    cmd = [
        "ffmpeg", "-y", "-v", "warning",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", audio_wav,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "fast", "-profile:v", "high", "-level:v", "4.2",
        "-threads", "4",
        "-pix_fmt", "yuv420p", "-crf", "17", "-maxrate", "13M", "-bufsize", "26M",
        "-g", "60", "-bf", "2",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-movflags", "+faststart", "-shortest",
        out_mp4
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=ff_log)

    # Pre-build dark obsidian studio base canvas once (uint8)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = np.clip(1.0 - 0.34 * (((xx - W * 0.5) / (W * 0.65))**2 + ((yy - H * 0.5) / (H * 0.65))**2), 0.55, 1.0)
    base_studio = np.zeros((H, W, 3), dtype=np.uint8)
    base_studio[:, :, 0] = (17 * vig).astype(np.uint8)
    base_studio[:, :, 1] = (10 * vig).astype(np.uint8)
    base_studio[:, :, 2] = (7 * vig).astype(np.uint8)

    sil_bgr, sil_alpha = render_silence_banner()

    cur_shot_idx = -1
    decoder = None
    hud_strips = None
    stage_y, stage_h = 540, 583
    cap_cache = {}

    for f_i in range(total_frames):
        if f_i == 0:
            proc.stdin.write(cover_bgr.tobytes())
            continue

        t = f_i / float(FPS)
        shot = SHOTS[-1]
        for s in SHOTS:
            if s[1] <= t < s[2]:
                shot = s
                break

        if shot[0] != cur_shot_idx:
            if decoder is not None:
                decoder.close()
            cur_shot_idx = shot[0]
            _, s_t0, s_t1, fn, src_t0, crop_b, beat, _, _ = shot
            decoder = StreamShotDecoder(os.path.join(FOOTAGE_DIR, fn), src_t0)
            if decoder.w <= 1400:
                stage_h = 660
            else:
                eff_h = decoder.h - crop_b
                stage_h = int(round(STAGE_W * (eff_h / float(decoder.w))))
            stage_y = 356 + (790 - stage_h) // 2
            hud_strips = build_hud_strips(shot, stage_y, stage_h)

        _, s_t0, s_t1, fn, src_t0, crop_b, beat, _, _ = shot
        local_t = t - s_t0
        prog_shot = np.clip(local_t / max(0.01, s_t1 - s_t0), 0.0, 1.0)

        raw = decoder.get_at(src_t0 + local_t)
        if crop_b > 0:
            raw = raw[:raw.shape[0] - crop_b, :]

        rh, rw = raw.shape[:2]
        if rw <= 1400:
            target_rh = int(round(rw * (stage_h / float(STAGE_W))))
            y_off = max(0, int((rh - target_rh) * 0.54))
            crop = raw[y_off:y_off + target_rh, :]
        else:
            zoom = 1.0 + 0.036 * prog_shot
            cw = int(round(rw / zoom))
            ch = int(round(rh / zoom))
            cx0 = (rw - cw) // 2
            cy0 = (rh - ch) // 2
            crop = raw[cy0:cy0 + ch, cx0:cx0 + cw]

        stage_bgr = cv2.resize(crop, (STAGE_W, stage_h), interpolation=cv2.INTER_AREA)
        stage_bgr = unsharp_luma(stage_bgr, sigma=0.88, amount=0.25)

        # Ambient live color glow + dark obsidian studio base in uint8 (fast OpenCV C++ ops!)
        tiny = cv2.resize(stage_bgr, (27, 48), interpolation=cv2.INTER_AREA)
        amb = cv2.GaussianBlur(tiny, (15, 15), 6.0)
        amb_full = cv2.resize(amb, (W, H), interpolation=cv2.INTER_LINEAR)
        frame = cv2.addWeighted(amb_full, 0.14, base_studio, 1.0, 0)

        # Soft dark recess behind Cinema Stage
        sh_y0 = max(0, stage_y - 10)
        sh_y1 = min(H, stage_y + stage_h + 24)
        frame[sh_y0:sh_y1, STAGE_X - 8:STAGE_X + STAGE_W + 8] = (
            frame[sh_y0:sh_y1, STAGE_X - 8:STAGE_X + STAGE_W + 8] // 3
        )

        # Paste 1:1 supersampled Cinema Stage
        frame[stage_y:stage_y + stage_h, STAGE_X:STAGE_X + STAGE_W] = stage_bgr

        # Composite pre-rendered HUD strips (top masthead, stage bezel/telemetry, citation)
        for k in ("top", "stage", "cit"):
            y_pos, fg_b, fg_a = hud_strips[k]
            blend_roi_inplace(frame, y_pos, fg_b, fg_a)

        # Composite synced caption card OR dramatic silence banner (y=1220..1430)
        cap_y = 1220
        if sil_s <= t <= sil_e:
            blend_roi_inplace(frame, cap_y, sil_bgr, sil_alpha)
        else:
            active_c = None
            active_idx = -1
            for c_i, c in enumerate(captions):
                if c["start"] - 0.04 <= t <= c["end"] + 0.08:
                    active_c = c
                    active_idx = c_i
                    break
            if active_c is not None:
                c_prog = (t - active_c["start"]) / max(0.1, active_c["end"] - active_c["start"])
                bucket = int(np.clip(round(c_prog * 20), 0, 20))
                key = (active_idx, bucket)
                if key not in cap_cache:
                    if len(cap_cache) > 45:
                        cap_cache.clear()
                    cap_cache[key] = render_caption_box(active_c["text"], bucket / 20.0, is_alert=(active_c["beat"] == 7))
                c_bgr, c_alpha = cap_cache[key]
                blend_roi_inplace(frame, cap_y, c_bgr, c_alpha)

        proc.stdin.write(frame.tobytes())

        if f_i % 600 == 0 or f_i == total_frames - 1:
            el = time.time() - t_start_wall
            print(f"Rendered {f_i+1}/{total_frames} frames ({(f_i+1)/total_frames*100:5.1f}%) in {el:.1f}s")

    if decoder is not None:
        decoder.close()
    proc.stdin.close()
    rc = proc.wait()
    ff_log.close()
    if rc != 0:
        with open("/tmp/sss002_build/ffmpeg_render.log") as f:
            print("FFMPEG STDERR:", f.read())
        raise RuntimeError(f"ffmpeg exited with {rc}")
    sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"SUCCESS -> {out_mp4} ({sz_mb:.2f} MiB) in {time.time() - t_start_wall:.1f}s")

if __name__ == "__main__":
    main()
