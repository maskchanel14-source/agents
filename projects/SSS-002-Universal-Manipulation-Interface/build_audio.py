#!/usr/bin/env python3
"""Assemble frame-exact voice-00 narration, synced captions.srt, and -14.0 LUFS stereo documentary mix for SSS-002."""
import json
import os
import subprocess
import wave
import numpy as np

SR = 48000
ATEMPO = 1.078

BEATS = [
    (1, "/tmp/sss002_build/b1.wav", 0.16, [
        "Nobody trained this factory robot\nto throw.",
        "It learned from a $73 plastic claw\nand a GoPro."
    ]),
    (2, "/tmp/sss002_build/b2.wav", 0.16, [
        "Normally, teaching a robot arm means\nbolting a $40,000 machine to one table.",
        "Move it to a real kitchen,\nand it fails."
    ]),
    (3, "/tmp/sss002_build/b3.wav", 0.16, [
        "So Stanford, Columbia & MIT engineers\nditched the robot during training,",
        "carrying this 3D-printed claw\nanywhere."
    ]),
    (4, "/tmp/sss002_build/b4.wav", 0.16, [
        "Beside its fisheye lens, two tiny mirrors\ncreate stereo 3D depth,",
        "while the GoPro's gyroscope tracks\nfast wrist snaps."
    ]),
    (5, "/tmp/sss002_build/b5.wav", 0.16, [
        "Mount that claw on any robot arm,\nmatch millisecond lag,",
        "and skills transfer zero-shot."
    ]),
    (6, "/tmp/sss002_build/b6.wav", 0.15, [
        "Two arms fold a sweater.\nOne hurls apples into bins.",
        "Another turns on a tap\nto scrub ketchup."
    ]),
    (7, "/tmp/sss002_build/b7.wav", 0.64, [  # 0.64s dramatic silence dropout right after this!
        "When researchers squirt extra mustard\nmid-wash..."
    ]),
    (8, "/tmp/sss002_build/b8.wav", 0.36, [
        "Nobody coded a retry, yet it scrubs\nuntil the plate shines,",
        "works in blackouts, and serves espresso\non a water fountain.",
        "Remember..."
    ]),
]

def load_trimmed_beat(wav_path: str) -> np.ndarray:
    tmp_out = wav_path.replace(".wav", "_48k_tempo.wav")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", wav_path,
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
    """Find natural low-energy pause valleys inside a beat to split captions cleanly."""
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
        # Search valley between 32% and 74% of beat
        lo, hi = int(len(rms) * 0.32), int(len(rms) * 0.74)
        best = lo + int(np.argmin(rms[lo:hi]))
        pts.append(best * hop / SR)
    elif n_parts == 3:
        # Beat 8: split1 around 34..54%, split2 right before "Remember..." (last 12..25%)
        lo1, hi1 = int(len(rms) * 0.30), int(len(rms) * 0.54)
        b1 = lo1 + int(np.argmin(rms[lo1:hi1]))
        lo2, hi2 = int(len(rms) * 0.76), int(len(rms) * 0.93)
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

def synthesize_cinema_bed(total_samples: int, silence_window: tuple, beat_starts: list) -> np.ndarray:
    """Create a rich, warm stereo documentary underscore + subtle robotics/impact cues."""
    t = np.arange(total_samples, dtype=np.float32) / SR
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    # Warm D-minor documentary synth progression (D2 -> Bb1 -> F2 -> C2, 8-second cycle)
    prog_freqs = [73.42, 58.27, 87.31, 65.41]
    phase_l = np.zeros_like(t)
    phase_r = np.zeros_like(t)
    idx_chord = ((t / 4.2).astype(int)) % 4
    f_root = np.choose(idx_chord, prog_freqs)
    # Smooth frequency glide
    win_g = int(0.18 * SR)
    kernel = np.ones(win_g, dtype=np.float32) / win_g
    f_smooth = np.convolve(f_root, kernel, mode="same")
    ph = 2.0 * np.pi * np.cumsum(f_smooth) / SR

    # Analog warm pad + fifth harmonic + subtle stereo detune
    pad_l = 0.48 * np.sin(ph) + 0.22 * np.sin(2.001 * ph + 0.3) + 0.12 * np.sin(1.498 * ph + 0.7)
    pad_r = 0.48 * np.sin(ph + 0.18) + 0.22 * np.sin(1.999 * ph + 1.1) + 0.12 * np.sin(1.502 * ph + 0.2)

    # Subtle pulsing 16th-note documentary arpeggio clock (124 BPM -> 4.133 Hz pulse)
    pulse_env = 0.5 + 0.5 * np.sin(2.0 * np.pi * 4.133 * t - np.pi / 2)
    pulse_env = pulse_env ** 3.2
    arp_notes = [293.66, 349.23, 440.00, 523.25]
    arp_idx = ((t * 4.133).astype(int)) % 4
    f_arp = np.choose(arp_idx, arp_notes)
    ph_arp = 2.0 * np.pi * np.cumsum(f_arp) / SR
    arp_l = 0.11 * pulse_env * np.sin(ph_arp) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t))
    arp_r = 0.11 * pulse_env * np.sin(ph_arp + 0.65) * (0.6 + 0.4 * np.cos(2 * np.pi * 0.11 * t))

    left = pad_l + arp_l
    right = pad_r + arp_r

    # Add subtle deep kinematic impact hits on major story beat transitions
    for b_idx, bt in enumerate(beat_starts):
        s_i = int(bt * SR)
        hit_len = int(0.42 * SR)
        if s_i + hit_len < total_samples:
            ht = np.arange(hit_len, dtype=np.float32) / SR
            # Sub-drop sweep 95 Hz -> 38 Hz
            sweep = np.sin(2 * np.pi * (38.0 * ht + 57.0 * 0.12 * (1.0 - np.exp(-ht / 0.12))))
            env = np.exp(-ht / 0.13)
            amp = 0.34 if b_idx in (0, 4, 7) else 0.18
            left[s_i:s_i+hit_len] += amp * sweep * env
            right[s_i:s_i+hit_len] += amp * sweep * env

    # Total dramatic silence dropout right before Beat 8 ("When researchers squirt extra mustard mid-wash... [SILENCE] Nobody coded a retry...")
    sil_s, sil_e = int(silence_window[0] * SR), int(silence_window[1] * SR)
    fade_n = int(0.045 * SR)
    if sil_s > fade_n and sil_e + fade_n < total_samples:
        left[sil_s - fade_n:sil_s] *= np.linspace(1.0, 0.0, fade_n)
        right[sil_s - fade_n:sil_s] *= np.linspace(1.0, 0.0, fade_n)
        left[sil_s:sil_e] = 0.0
        right[sil_s:sil_e] = 0.0
        left[sil_e:sil_e + fade_n] *= np.linspace(0.0, 1.0, fade_n)
        right[sil_e:sil_e + fade_n] *= np.linspace(0.0, 1.0, fade_n)

    # Smooth end fade for seamless loop back into Frame 1
    end_fade = int(0.28 * SR)
    left[-end_fade:] *= np.linspace(1.0, 0.35, end_fade)
    right[-end_fade:] *= np.linspace(1.0, 0.35, end_fade)

    return np.stack([left, right], axis=1)

def main():
    cursor = 0.22  # crisp 220ms intro breath before first word
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
            c0 = b_start + splits[idx_c]
            c1 = b_start + splits[idx_c + 1]
            captions.append({"start": round(c0, 3), "end": round(c1, 3), "text": txt, "beat": b_id})
        beat_meta.append({"beat": b_id, "start": round(b_start, 3), "end": round(b_end, 3), "duration": round(dur, 3)})
        vo_chunks.append(seg)
        if b_id == 7:
            silence_window = (b_end + 0.02, b_end + pause_after - 0.02)
        vo_chunks.append(np.zeros(int(pause_after * SR), dtype=np.float32))
        cursor = b_end + pause_after

    vo_mono = np.concatenate(vo_chunks)
    # Snap total length to exact integer multiple of 1/60s frames
    total_frames = int(round((len(vo_mono) / SR) * 60))
    target_samples = int(round(total_frames / 60.0 * SR))
    if len(vo_mono) < target_samples:
        vo_mono = np.pad(vo_mono, (0, target_samples - len(vo_mono)))
    else:
        vo_mono = vo_mono[:target_samples]

    total_dur = len(vo_mono) / SR
    print(f"Total timeline: {total_dur:.4f}s ({total_frames} frames @ 60fps)")
    print(f"Dramatic silence dropout: {silence_window[0]:.3f}s -> {silence_window[1]:.3f}s ({silence_window[1]-silence_window[0]:.3f}s)")

    # Save clean voiceover-only WAV & MP3
    vo_only_wav = "/tmp/sss002_build/vo_only.wav"
    vo_stereo = np.stack([vo_mono, vo_mono], axis=1)
    vo_pcm = np.clip(vo_stereo * 0.88 * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(vo_only_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(vo_pcm.tobytes())

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", vo_only_wav,
        "-af", "loudnorm=I=-15.0:TP=-1.5:LRA=9",
        "-c:a", "libmp3lame", "-b:a", "256k",
        "/home/user/deliverables/SSS-002/SSS-002_Voiceover_Only.mp3"
    ], check=True)

    # Build stereo documentary score + sidechain ducking under voiceover
    bed = synthesize_cinema_bed(len(vo_mono), silence_window, [b["start"] for b in beat_meta])
    # Envelope follower on voiceover for smooth ducking
    env_win = int(0.08 * SR)
    vo_env = np.convolve(np.abs(vo_mono), np.ones(env_win, dtype=np.float32) / env_win, mode="same")
    duck = np.clip(1.0 - 2.6 * vo_env, 0.30, 1.0)[:, None]
    mix = np.stack([vo_mono, vo_mono], axis=1) * 0.92 + bed * 0.22 * duck
    mix_peak = np.max(np.abs(mix)) + 1e-9
    mix = mix / mix_peak * 0.86

    raw_mix_wav = "/tmp/sss002_build/raw_mix.wav"
    mix_pcm = np.clip(mix * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(raw_mix_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(mix_pcm.tobytes())

    # Two-pass EBU R128 loudness normalization to exact -14.0 LUFS, TP <= -1.2 dBTP
    master_wav = "/tmp/sss002_build/master_mix.wav"
    p1 = subprocess.run([
        "ffmpeg", "-y", "-i", raw_mix_wav,
        "-af", "loudnorm=I=-14.0:TP=-1.2:LRA=9:print_format=json",
        "-f", "null", "-"
    ], capture_output=True, text=True, check=True)
    stderr_txt = p1.stderr
    j_start = stderr_txt.rfind("{")
    j_end = stderr_txt.rfind("}") + 1
    stats = json.loads(stderr_txt[j_start:j_end])
    af_pass2 = (
        f"loudnorm=I=-14.0:TP=-1.2:LRA=9:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true,aresample={SR}"
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", raw_mix_wav,
        "-af", af_pass2, "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", master_wav
    ], check=True)

    # Verify final LUFS
    eb = subprocess.run([
        "ffmpeg", "-nostats", "-i", master_wav, "-filter_complex", "ebur128=peak=true", "-f", "null", "-"
    ], capture_output=True, text=True)
    for line in eb.stderr.splitlines():
        if any(k in line for k in ("I:", "LRA:", "Peak:")):
            print("EBUR128:", line.strip())

    # Write captions.srt
    srt_lines = []
    for i, c in enumerate(captions, 1):
        srt_lines.append(f"{i}\n{fmt_srt_time(c['start'])} --> {fmt_srt_time(c['end'])}\n{c['text']}\n")
    srt_path = "projects/SSS-002-Universal-Manipulation-Interface/captions.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

    meta_path = "projects/SSS-002-Universal-Manipulation-Interface/timings.json"
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
