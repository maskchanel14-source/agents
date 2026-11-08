#!/usr/bin/env python3
"""Assemble frame-exact voice-00 narration, synced captions.srt, and -14.0 LUFS Dark Science stereo mix for SSS-003."""
import json
import shutil
import subprocess
import wave
import numpy as np

def get_ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

FFMPEG = get_ffmpeg()
SR = 48000
ATEMPO = 1.032

BEATS = [
    (1, "/tmp/sss003_build/b1.wav", 0.16, [
        "Every selfie you post hides\na reflection.",
        "Now AI can step inside your eye\nand look around."
    ]),
    (2, "/tmp/sss003_build/b2.wav", 0.16, [
        "Across healthy adults, the human cornea\ncurves like a 7.8 mm dome,",
        "acting as a tiny wide-angle\nsecurity mirror."
    ]),
    (3, "/tmp/sss003_build/b3.wav", 0.16, [
        "At the University of Maryland,\nresearchers fed portrait clips",
        "into a 3D neural radiance field."
    ]),
    (4, "/tmp/sss003_build/b4.wav", 0.16, [
        "Previously, two things blocked this:\nmicro-shifts as eyeballs rotate,",
        "and your colored iris overpowering\nfaint room reflections."
    ]),
    (5, "/tmp/sss003_build/b5.wav", 0.16, [
        "Their algorithm locks onto cornea pose\nwhile peeling away",
        "a 2D map of your iris texture."
    ]),
    (6, "/tmp/sss003_build/b6.wav", 0.16, [
        "Suddenly, hidden rooms, plush toys,\nand bystanders appear in 3D,",
        "given enough head motion."
    ]),
    (7, "/tmp/sss003_build/b7.wav", 0.64, [  # 0.64s chilling silence dropout right after this!
        "Then they tested public music videos\nof Miley Cyrus and Lady Gaga..."
    ]),
    (8, "/tmp/sss003_build/b8.wav", 0.34, [
        "Zooming into single eyes, phantom\nsilhouettes of studio lights",
        "and camera crews emerged years later.",
        "Remember..."
    ]),
]

def load_trimmed_beat(wav_path: str) -> np.ndarray:
    tmp_out = wav_path.replace(".wav", "_48k_tempo.wav")
    subprocess.run([
        FFMPEG, "-y", "-v", "error", "-i", wav_path,
        "-af", f"atempo={ATEMPO},aresample={SR}",
        "-ac", "1", "-c:a", "pcm_s16le", tmp_out
    ], check=True)
    with wave.open(tmp_out, "rb") as wf:
        raw = wf.readframes(wf.getnframes())
    arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    idx = np.where(np.abs(arr) > 0.0075)[0]
    pad = int(0.025 * SR)
    s0 = max(0, idx[0] - pad)
    s1 = min(len(arr), idx[-1] + pad)
    seg = arr[s0:s1].copy()
    fade = min(int(0.018 * SR), len(seg) // 4)
    seg[:fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)
    seg[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)
    return seg

def find_split_points(seg: np.ndarray, n_parts: int) -> list:
    if n_parts == 1:
        return [0.0, len(seg) / SR]
    win = int(0.035 * SR)
    hop = int(0.010 * SR)
    rms = np.array([
        np.sqrt(np.mean(seg[i:i+win]**2) + 1e-12)
        for i in range(0, max(1, len(seg) - win), hop)
    ])
    pts = [0.0]
    dur = len(seg) / SR
    if n_parts == 2:
        lo, hi = int(len(rms) * 0.30), int(len(rms) * 0.76)
        best = lo + int(np.argmin(rms[lo:hi]))
        pts.append(best * hop / SR)
    elif n_parts == 3:
        lo1, hi1 = int(len(rms) * 0.30), int(len(rms) * 0.58)
        b1 = lo1 + int(np.argmin(rms[lo1:hi1]))
        lo2, hi2 = int(len(rms) * 0.75), int(len(rms) * 0.93)
        b2 = lo2 + int(np.argmin(rms[lo2:hi2]))
        pts.extend([b1 * hop / SR, b2 * hop / SR])
    pts.append(dur)
    return pts

def fmt_srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    hh = ms // 3600000
    mm = (ms % 3600000) // 60000
    ss = (ms % 60000) // 1000
    mmm = ms % 1000
    return f"{hh:02d}:{mm:02d}:{ss:02d},{mmm:03d}"

def synthesize_dark_science_bed(total_samples: int, silence_window: tuple, beat_starts: list) -> np.ndarray:
    """Eerie C#-minor Dark Science analog bass drone + crystalline optical shimmer + sub-heartbeat."""
    t = np.arange(total_samples, dtype=np.float32) / SR
    # C#2 (69.30 Hz) -> A1 (55.00 Hz) -> F#1 (46.25 Hz) -> G#1 (51.91 Hz)
    prog_freqs = [69.30, 55.00, 46.25, 51.91]
    idx_chord = ((t / 4.5).astype(int)) % 4
    f_root = np.choose(idx_chord, prog_freqs)
    win_g = int(0.24 * SR)
    f_smooth = np.convolve(f_root, np.ones(win_g, dtype=np.float32) / win_g, mode="same")
    ph = 2.0 * np.pi * np.cumsum(f_smooth) / SR

    # Dark bowed cello/synth sub-pad with minor-second eerie shimmer
    pad_l = 0.50 * np.sin(ph) + 0.20 * np.sin(2.002 * ph + 0.4) + 0.09 * np.sin(2.997 * ph + 1.1)
    pad_r = 0.50 * np.sin(ph + 0.22) + 0.20 * np.sin(1.998 * ph + 1.3) + 0.09 * np.sin(3.003 * ph + 0.2)

    # Crystalline optical ray-pulse (116 BPM -> 3.867 Hz)
    pulse = (0.5 + 0.5 * np.sin(2.0 * np.pi * 3.867 * t - np.pi / 2)) ** 3.8
    shimmer_notes = [277.18, 329.63, 415.30, 440.00]  # C#4, E4, G#4, A4 (eerie minor 6th tension!)
    s_idx = ((t * 3.867).astype(int)) % 4
    f_sh = np.choose(s_idx, shimmer_notes)
    ph_sh = 2.0 * np.pi * np.cumsum(f_sh) / SR
    sh_l = 0.095 * pulse * np.sin(ph_sh) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.09 * t))
    sh_r = 0.095 * pulse * np.sin(ph_sh + 0.85) * (0.55 + 0.45 * np.cos(2 * np.pi * 0.09 * t))

    left = pad_l + sh_l
    right = pad_r + sh_r

    # Deep optical/sub-sonar impacts on beat transitions
    for b_idx, bt in enumerate(beat_starts):
        s_i = int(bt * SR)
        hit_len = int(0.48 * SR)
        if s_i + hit_len < total_samples:
            ht = np.arange(hit_len, dtype=np.float32) / SR
            sweep = np.sin(2 * np.pi * (36.0 * ht + 58.0 * 0.13 * (1.0 - np.exp(-ht / 0.13))))
            ping = 0.18 * np.sin(2 * np.pi * 830.6 * ht) * np.exp(-ht / 0.09)
            env = np.exp(-ht / 0.15)
            amp = 0.36 if b_idx in (0, 4, 7) else 0.19
            left[s_i:s_i+hit_len] += amp * sweep * env + ping
            right[s_i:s_i+hit_len] += amp * sweep * env + ping * 0.85

    # Chilling total silence dropout right before Beat 8 celebrity reveal
    sil_s, sil_e = int(silence_window[0] * SR), int(silence_window[1] * SR)
    fade_n = int(0.045 * SR)
    if sil_s > fade_n and sil_e + fade_n < total_samples:
        left[sil_s - fade_n:sil_s] *= np.linspace(1.0, 0.0, fade_n)
        right[sil_s - fade_n:sil_s] *= np.linspace(1.0, 0.0, fade_n)
        left[sil_s:sil_e] = 0.0
        right[sil_s:sil_e] = 0.0
        left[sil_e:sil_e + fade_n] *= np.linspace(0.0, 1.0, fade_n)
        right[sil_e:sil_e + fade_n] *= np.linspace(0.0, 1.0, fade_n)

    end_fade = int(0.26 * SR)
    left[-end_fade:] *= np.linspace(1.0, 0.35, end_fade)
    right[-end_fade:] *= np.linspace(1.0, 0.35, end_fade)
    return np.stack([left, right], axis=1)

def main():
    cursor = 0.22
    vo_chunks = [np.zeros(int(cursor * SR), dtype=np.float32)]
    captions = []
    beat_meta = []
    silence_window = (0.0, 0.0)

    for b_id, wav_path, pause_after, cap_lines in BEATS:
        seg = load_trimmed_beat(wav_path)
        dur = len(seg) / SR
        b_start = cursor
        b_end = cursor + dur
        splits = find_split_points(seg, len(cap_lines))
        for idx_c, txt in enumerate(cap_lines):
            captions.append({
                "start": round(b_start + splits[idx_c], 3),
                "end": round(b_start + splits[idx_c + 1], 3),
                "text": txt,
                "beat": b_id
            })
        beat_meta.append({"beat": b_id, "start": round(b_start, 3), "end": round(b_end, 3), "duration": round(dur, 3)})
        vo_chunks.append(seg)
        if b_id == 7:
            silence_window = (b_end + 0.02, b_end + pause_after - 0.02)
        vo_chunks.append(np.zeros(int(pause_after * SR), dtype=np.float32))
        cursor = b_end + pause_after

    vo_mono = np.concatenate(vo_chunks)
    total_frames = int(round((len(vo_mono) / SR) * 60))
    target_samples = int(round(total_frames / 60.0 * SR))
    if len(vo_mono) < target_samples:
        vo_mono = np.pad(vo_mono, (0, target_samples - len(vo_mono)))
    else:
        vo_mono = vo_mono[:target_samples]

    total_dur = len(vo_mono) / SR
    print(f"Total timeline: {total_dur:.4f}s ({total_frames} frames @ 60fps)")
    print(f"Dramatic silence dropout: {silence_window[0]:.3f}s -> {silence_window[1]:.3f}s ({silence_window[1]-silence_window[0]:.3f}s)")

    vo_only_wav = "/tmp/sss003_build/vo_only.wav"
    vo_pcm = np.clip(np.stack([vo_mono, vo_mono], axis=1) * 0.88 * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(vo_only_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(vo_pcm.tobytes())

    subprocess.run([
        FFMPEG, "-y", "-v", "error", "-i", vo_only_wav,
        "-af", "loudnorm=I=-15.0:TP=-1.5:LRA=9",
        "-c:a", "libmp3lame", "-b:a", "256k",
        "/home/user/deliverables/SSS-003/SSS-003_Voiceover_Only.mp3"
    ], check=True)

    bed = synthesize_dark_science_bed(len(vo_mono), silence_window, [b["start"] for b in beat_meta])
    env_win = int(0.08 * SR)
    vo_env = np.convolve(np.abs(vo_mono), np.ones(env_win, dtype=np.float32) / env_win, mode="same")
    duck = np.clip(1.0 - 2.6 * vo_env, 0.28, 1.0)[:, None]
    mix = np.stack([vo_mono, vo_mono], axis=1) * 0.92 + bed * 0.23 * duck
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.86

    raw_mix_wav = "/tmp/sss003_build/raw_mix.wav"
    mix_pcm = np.clip(mix * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(raw_mix_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(mix_pcm.tobytes())

    master_wav = "/tmp/sss003_build/master_mix.wav"
    p1 = subprocess.run([
        FFMPEG, "-y", "-i", raw_mix_wav,
        "-af", "loudnorm=I=-14.0:TP=-1.2:LRA=9:print_format=json",
        "-f", "null", "-"
    ], capture_output=True, text=True, check=True)
    j_start = p1.stderr.rfind("{")
    j_end = p1.stderr.rfind("}") + 1
    stats = json.loads(p1.stderr[j_start:j_end])
    af_pass2 = (
        f"loudnorm=I=-14.0:TP=-1.2:LRA=9:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true,aresample={SR}"
    )
    subprocess.run([
        FFMPEG, "-y", "-v", "error", "-i", raw_mix_wav,
        "-af", af_pass2, "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", master_wav
    ], check=True)

    eb = subprocess.run([
        FFMPEG, "-nostats", "-i", master_wav, "-filter_complex", "ebur128=peak=true", "-f", "null", "-"
    ], capture_output=True, text=True)
    for line in eb.stderr.splitlines()[-10:]:
        if any(k in line for k in ("I:", "LRA:", "Peak:")):
            print("EBUR128:", line.strip())

    srt_path = "projects/SSS-003-Seeing-World-Through-Your-Eyes/captions.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(
            f"{i}\n{fmt_srt_time(c['start'])} --> {fmt_srt_time(c['end'])}\n{c['text']}\n"
            for i, c in enumerate(captions, 1)
        ))

    meta_path = "projects/SSS-003-Seeing-World-Through-Your-Eyes/timings.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_duration": round(total_dur, 4),
            "total_frames_60fps": total_frames,
            "silence_window": [round(silence_window[0], 3), round(silence_window[1], 3)],
            "beats": beat_meta,
            "captions": captions,
        }, f, indent=2)
    print(f"Wrote {srt_path} ({len(captions)} captions) & {meta_path}")
    for b in beat_meta:
        print(f"  Beat {b['beat']}: {b['start']:6.3f}s -> {b['end']:6.3f}s ({b['duration']:5.3f}s)")

if __name__ == "__main__":
    main()
