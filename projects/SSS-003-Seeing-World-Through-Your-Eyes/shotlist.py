#!/usr/bin/env python3
"""
Verified 36-Shot Non-Repeating 1080p Shotlist for SSS-003 (Seeing the World Through Your Eyes).
100% native 1080p vertical height (1920x1080 & 1080x1080), zero scene/interval overlaps,
covering exact 57.7833s (3,467 frames @ 60.00fps) with physical eye-zoom loop continuity.
"""
import os
import cv2

FOOTAGE_DIR = "/home/user/agents/.cache/library/footage/eyenerf"

# (shot_idx, t_out_start, t_out_end, rel_path, src_t0, beat_id, header_title, telem_tag)
SHOTS = [
    # === BEAT 1 (0.000s -> 7.505s): Hook — Every selfie hides a reflection; AI steps inside your eye ===
    (1,  0.000,  1.650, "videos/dog.mp4",                         0.45, 1, "HIDDEN IN EVERY SELFIE",     "INPUT: PORTRAIT CORNEA ZOOM • 1080P"),
    (2,  1.650,  3.250, "videos/kirby.mp4",                       1.35, 1, "HIDDEN IN EVERY SELFIE",     "SUB-MM CORNEA REFLECTION DETECTED"),
    (3,  3.250,  5.350, "videos/barbershop_interior.mp4",         0.35, 1, "STEPPING INSIDE AN EYE",     "3D RADIANCE FIELD BEYOND CAMERA"),
    (4,  5.350,  7.505, "videos/kirby.mp4",                       4.80, 1, "STEPPING INSIDE AN EYE",     "RECONSTRUCTED OFF-SCREEN OBJECTS"),

    # === BEAT 2 (7.505s -> 15.981s): Cornea Optical Physics — 7.8 mm biological wide-angle mirror ===
    (5,  7.505,  9.250, "videos/poster.mp4",                      0.50, 2, "7.8 MM BIOLOGICAL MIRROR",   "CORNEA RADIUS R = 7.8MM • E = 0.50"),
    (6,  9.250, 11.000, "old_videos/dog_plant.mp4",               7.20, 2, "7.8 MM BIOLOGICAL MIRROR",   "DOME HEIGHT: 2.18MM CURVED OPTICS"),
    (7, 11.000, 12.750, "videos/outdoor.mp4",                     0.40, 2, "WIDE-ANGLE SECURITY LENS",   "SUNLIT OUTDOOR CORNEA CAPTURE"),
    (8, 12.750, 14.400, "old_videos/ukulele.mp4",                 0.40, 2, "WIDE-ANGLE SECURITY LENS",   "MULTI-VIEW EYE ROTATION RAYS"),
    (9, 14.400, 15.981, "old_videos/kirby_dog.mp4",               7.40, 2, "WIDE-ANGLE SECURITY LENS",   "LIMBUS PIXEL DEPTH CALIBRATION"),

    # === BEAT 3 (15.981s -> 22.641s): University of Maryland — Portrait clips -> 3D NeRF ===
    (10, 15.981, 17.650, "videos/plushies.mp4",                   0.45, 3, "UNIV. OF MARYLAND LAB",      "CVPR 2024 ORAL • ARXIV:2306.09348"),
    (11, 17.650, 19.350, "videos/classroom.mp4",                  0.35, 3, "3D NEURAL RADIANCE FIELD",   "RAY BOUNCE OFF CURVED CORNEA"),
    (12, 19.350, 21.000, "videos/kitchen.mp4",                    0.35, 3, "3D NEURAL RADIANCE FIELD",   "SYNTHETIC EYE SCENE: KITCHEN 3D"),
    (13, 21.000, 22.641, "videos/living_room.mp4",                0.35, 3, "3D NEURAL RADIANCE FIELD",   "SYNTHETIC EYE SCENE: LIVING ROOM"),

    # === BEAT 4 (22.641s -> 31.399s): Two Blockers — Micro eye-pose noise & colored iris entanglement ===
    (14, 22.641, 24.450, "videos/ablation/lit_plushies_no_pose.mp4", 0.30, 4, "WHY IT USED TO FAIL",   "NO POSE OPT • BLURRY SMEARED 3D"),
    (15, 24.450, 26.250, "old_videos/lit_plushies_spiral_no_pose.mp4", 1.20, 4, "MICRO-SHIFT POSE DRIFT","SUB-DEGREE EYEBALL MOTION NOISE"),
    (16, 26.250, 28.000, "videos/ablation/ukulele_no_texture.mp4", 0.30, 4, "IRIS TEXTURE COLLISION",  "NO DECOMP • IRIS FIBERS BLEED IN"),
    (17, 28.000, 29.750, "old_videos/kibry_dog_spiral_no_texture.mp4", 0.50, 4, "IRIS TEXTURE COLLISION","ENTANGLED PIGMENT + ROOM LIGHT"),
    (18, 29.750, 31.399, "old_videos/alien.mp4",                  0.45, 4, "FAINT SIGNAL EXTRACTION",  "REFLECTION <5% OF TOTAL PIXELS"),

    # === BEAT 5 (31.399s -> 37.432s): The Solution — Cornea Pose Lock + 2D Iris Texture Peeling ===
    (19, 31.399, 32.950, "videos/ablation/lit_plushies_with_pose.mp4", 0.30, 5, "CORNEA POSE LOCKED",  "LIE-GROUP SE(3) EYE OPTIMIZATION"),
    (20, 32.950, 34.450, "old_videos/lit_plushies_spiral.mp4",    1.20, 5, "CORNEA POSE LOCKED",       "SHARP 3D GEOMETRY RECOVERED"),
    (21, 34.450, 35.950, "videos/ablation/ukulele_with_texture.mp4", 0.30, 5, "2D IRIS PEELING",       "RADIAL PRIOR SEPARATES IRIS MAP"),
    (22, 35.950, 37.432, "old_videos/kibry_dog_spiral.mp4",       0.50, 5, "2D IRIS PEELING",          "CLEAN OBJECT ISOLATED FROM EYE"),

    # === BEAT 6 (37.432s -> 44.953s): Hidden Rooms, Toys, Bystanders + Honest Scientific Limit ===
    (23, 37.432, 38.950, "videos/barbershop_flip.mp4",            0.35, 6, "HIDDEN ROOMS REVEALED",    "FULL 360 CORNEA ROOM FLY-THROUGH"),
    (24, 38.950, 40.400, "old_videos/barbershop_back.mp4",        0.35, 6, "HIDDEN ROOMS REVEALED",    "WALL FRAMES & MIRRORS RECOVERED"),
    (25, 40.400, 41.950, "videos/dog.mp4",                        5.80, 6, "OFF-SCREEN OBJECTS IN 3D", "RECONSTRUCTED CERAMIC DOG & PLANT"),
    (26, 41.950, 43.450, "videos/outdoor.mp4",                    5.50, 6, "OUTDOOR HIDDEN TARGETS",   "PIKACHU RECONSTRUCTED FROM GLAZE"),
    (27, 43.450, 44.953, "videos/failed_1.mp4",                   0.40, 6, "HONEST SCIENTIFIC LIMIT",  "LIMIT: <4 FRAMES OR TINY MOTION"),

    # === BEAT 7 (44.953s -> 49.805s): Public Music Videos Setup + 0.60s Chilling Silence ===
    (28, 44.953, 46.600, "old_videos/Miley_Cyrus.mp4",            0.35, 7, "ARCHIVAL MUSIC VIDEOS",    "TEST 01: MILEY CYRUS PORTRAIT"),
    (29, 46.600, 48.200, "old_videos/Lady_Gaga.mp4",              0.30, 7, "ARCHIVAL MUSIC VIDEOS",    "TEST 02: LADY GAGA CLOSE-UP"),
    (30, 48.200, 49.805, "old_videos/Lady_Gaga.mp4",              2.05, 7, "SCANNING ARCHIVAL CORNEA", "ALERT: EXTRACTING STUDIO RAYS..."),

    # === BEAT 8 (49.805s -> 57.7833s): Phantom Silhouettes Emerge + Voluntary Subscribe Peak + Loop ===
    (31, 49.805, 51.350, "old_videos/Lady_Gaga.mp4",              4.10, 8, "PHANTOM CREW SILHOUETTES", "UNSEEN BYSTANDER SILHOUETTE IN 3D"),
    (32, 51.350, 52.850, "old_videos/Miley_Cyrus.mp4",            4.80, 8, "STUDIO LIGHTS RECOVERED",  "OCTAGONAL SOFTBOX RIG EXTRACTED"),
    (33, 52.850, 54.200, "videos/poster.mp4",                     6.20, 8, "YEARS AFTER RECORDING",    "OFF-CAMERA SCENE RECONSTRUCTION"),
    (34, 54.200, 55.450, "videos/plushies.mp4",                   5.60, 8, "YOUR EYES RECORD IT ALL",  "VOLUMETRIC 3D CORNEA PLAYBACK"),
    (35, 55.450, 56.600, "old_videos/classroom_spiral.mp4",       0.40, 8, "EVERY PIXEL COUNTS",       "BEYOND CAMERA LINE-OF-SIGHT"),
    # Shot 36 zooms back out of the eye in dog.mp4 (t=14.90..16.08s) -> seamlessly loops into Shot 1 (t=0.45s)!
    (36, 56.600, 57.7833,"videos/dog.mp4",                       14.90, 8, "REMEMBER...",              "LOOPING INTO CORNEA • #003"),
]

def validate_shotlist():
    assert len(SHOTS) == 36, f"Expected 36 shots, got {len(SHOTS)}"
    prev_end = 0.0
    by_file = {}
    for s in SHOTS:
        idx, t0, t1, rel, src_t0, beat, hdr, tel = s
        assert abs(t0 - prev_end) < 1e-4, f"Gap/overlap at shot {idx}: {t0} vs {prev_end}"
        dur = t1 - t0
        assert 0.95 <= dur <= 2.30, f"Shot {idx} duration {dur:.3f}s outside [0.95, 2.30]s"
        p = os.path.join(FOOTAGE_DIR, rel)
        assert os.path.exists(p), f"Missing clip: {p}"
        cap = cv2.VideoCapture(p)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        clip_dur = n / fps
        cap.release()
        assert h == 1080, f"Clip {rel} height {h} != 1080"
        src_t1 = src_t0 + dur
        assert src_t1 <= clip_dur - 0.04, f"Shot {idx} ({rel}) src_t1={src_t1:.2f}s exceeds clip_dur={clip_dur:.2f}s"
        for prev_s0, prev_s1, prev_idx in by_file.get(rel, []):
            overlap = min(src_t1, prev_s1) - max(src_t0, prev_s0)
            assert overlap <= -0.10, f"Shot {idx} overlaps Shot {prev_idx} in {rel}: [{src_t0:.2f},{src_t1:.2f}] vs [{prev_s0:.2f},{prev_s1:.2f}]"
        by_file.setdefault(rel, []).append((src_t0, src_t1, idx))
        prev_end = t1
    print(f"VALIDATED ALL {len(SHOTS)} SHOTS: 100% native 1080p height, ZERO scene/interval overlaps, exact {prev_end:.4f}s total!")

if __name__ == "__main__":
    validate_shotlist()
