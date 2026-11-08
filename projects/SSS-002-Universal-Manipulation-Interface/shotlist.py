#!/usr/bin/env python3
"""
Verified 36-Shot Non-Repeating 1080p Shotlist for SSS-002 (Universal Manipulation Interface).
Every single clip is native 1080p vertical height (1920x1080 or 1320x1080), strictly non-overlapping,
and mapped beat-for-beat to the 58.0833s (3,485 frames @ 60fps) documentary narration.
"""
import os
import subprocess

FOOTAGE_DIR = "/home/user/agents/.cache/library/footage/umi"

# Tuple schema:
# (shot_idx, t_out_start, t_out_end, filename, src_t0, crop_bottom_px, beat_id, header_title, telem_tag)
SHOTS = [
    # === BEAT 1 (0.000s -> 7.167s): Hook — Factory robot throwing + $73 plastic claw & GoPro ===
    (1,  0.000,  1.650, "task_dynamic_tossing.mp4",               1.52,  0, 1, "THE $73 ROBOT SECRET",      "TASK: DYNAMIC MID-AIR TOSS • 60FPS"),
    (2,  1.650,  3.150, "task_dynamic_tossing.mp4",               7.35,  0, 1, "THE $73 ROBOT SECRET",      "OBJECT 02: BASEBALL TRAJECTORY"),
    (3,  3.150,  5.100, "teaser_data_collection_dish.mp4",        4.55,  0, 1, "$73 CLAW + 1 GOPRO",        "3D-PRINTED GRIPPER BOM: $73 • 780G"),
    (4,  5.100,  7.167, "in_the_wild_cup_data_collection.mp4",    0.35,  0, 1, "$73 CLAW + 1 GOPRO",        "PORTABLE RIG • DEPLOY IN <2 MIN"),

    # === BEAT 2 (7.167s -> 15.235s): The Old Way — Bolted $40K lab teleop vs real-world failure ===
    (5,  7.167,  9.250, "throughput_cup_teleop_crop.mp4",         4.00,  0, 2, "$40,000 BOLTED LAB ARM",    "SPACEMOUSE TELEOP • 35 DEMOS/HR"),
    (6,  9.250, 11.150, "throughput_cup_teleop_crop.mp4",        26.00,  0, 2, "$40,000 BOLTED LAB ARM",    "FIXED TABLETOP • SLOW JOYSTICK"),
    (7, 11.150, 13.050, "comparison_cloth_no_rel.mp4",            5.20,  0, 2, "RIGID PIPELINES FAIL",      "NO RELATIVE POSE • DRIFT FAILURE"),
    (8, 13.050, 15.235, "comparison_dish_resnet.mp4",             8.50,  0, 2, "BLIND OUTSIDE THE LAB",     "BASELINE POLICY • KITCHEN FAILURE"),

    # === BEAT 3 (15.235s -> 23.003s): Stanford, Columbia & MIT ditch the robot during training ===
    (9,  15.235, 16.950, "in_the_wild_cup_data_collection.mp4",   3.10,  0, 3, "ZERO ROBOTS IN TRAINING",   "STANFORD × COLUMBIA × MIT × TRI"),
    (10, 16.950, 18.650, "throughput_cup_umi_crop.mp4",           5.20,  0, 3, "3.2× FASTER THAN TELEOP",   "UMI THROUGHPUT: 111 DEMOS/HR"),
    (11, 18.650, 20.300, "throughput_dish_crop.mp4",              4.50,  0, 3, "TEACHING AT HUMAN SPEED",   "BIMANUAL KITCHEN COLLECTION"),
    (12, 20.300, 21.650, "in_the_wild_cup_data_collection.mp4",   8.90,  0, 3, "ANY CAFE OR APARTMENT",     "IN-THE-WILD MULTI-SITE DEMOS"),
    (13, 21.650, 23.003, "throughput_tossing_crop.mp4",           3.80,  0, 3, "TEACHING DYNAMIC THROWS",   "HANDHELD TOSS DEMO • 80MM STROKE"),

    # === BEAT 4 (23.003s -> 31.880s): Optical & IMU Physics — 155° Fisheye + 2 Side Mirrors + Gyro SLAM ===
    (14, 23.003, 25.250, "teaser_data_collection_dish.mp4",       8.75,  0, 4, "2 MIRRORS = 3D STEREO",     "IMPLICIT STEREO DEPTH • 1 CAMERA"),
    (15, 25.250, 27.150, "in_the_wild_cup_data_overview.mp4",     0.40,  0, 4, "155° ULTRA-WIDE FISHEYE",   "VIRTUAL STEREO REFLECTIONS (L/R)"),
    (16, 27.150, 28.850, "teaser_data_collection_dish.mp4",      14.20, 66, 4, "SHARED OPTICAL REALITY",    "IDENTICAL HUMAN & ROBOT VIEW"),
    (17, 28.850, 30.400, "throughput_cloth_crop.mp4",             3.20,  0, 4, "GOPRO IMU GYRO TRACKING",   "VISUAL-INERTIAL 6-DOF POSE SLAM"),
    (18, 30.400, 31.880, "in_the_wild_cup_data_overview.mp4",     5.35,  0, 4, "MASSIVE DIVERSE DATASET",   "ZERO EXTERNAL MOTION CAPTURE"),

    # === BEAT 5 (31.880s -> 37.963s): Cross-Robot Transfer + Millisecond Latency Matching ===
    (19, 31.880, 33.450, "comparison_cup_franka.mp4",             1.10,  0, 5, "CROSS-ROBOT HARDWARE",      "ROBOT 01: 7-DOF FRANKA PANDA"),
    (20, 33.450, 34.950, "comparison_cup_ur5.mp4",                3.40,  0, 5, "CROSS-ROBOT HARDWARE",      "ROBOT 02: 6-DOF UR5E INDUSTRIAL"),
    (21, 34.950, 36.450, "comparison_tossing_no_latency_matching.mp4", 5.85, 0, 5, "WITHOUT LATENCY MATCH", "UNMATCHED LAG • OVERSHOOT MISS"),
    (22, 36.450, 37.963, "robustness_move_base.mp4",              0.45,  0, 5, "ZERO-SHOT CALIBRATION",     "MOVING WHEELED BASE • LIVE TRACK"),

    # === BEAT 6 (37.963s -> 45.036s): Rapid-Fire Dexterity Showcase — Sweater, Apple Toss, Ketchup Sink ===
    (23, 37.963, 39.350, "task_cloth_folding.mp4",                2.20,  0, 6, "BIMANUAL SWEATER FOLD",     "DUAL-ARM SYNC • SLEEVES INWARD"),
    (24, 39.350, 40.650, "task_cloth_folding.mp4",                9.80,  0, 6, "BIMANUAL SWEATER FOLD",     "INTER-GRIPPER RELATIVE POSE"),
    (25, 40.650, 42.333, "task_dynamic_tossing.mp4",             12.85,  0, 6, "PRECISION APPLE TOSS",      "LATENCY MATCHED • BULLSEYE HIT"),
    (26, 42.333, 43.650, "task_dish_washing.mp4",                 0.45,  0, 6, "7-STEP DISHWASHING",        "STEP 01: OPEN KITCHEN FAUCET"),
    (27, 43.650, 45.036, "task_dish_washing.mp4",                 4.90,  0, 6, "7-STEP DISHWASHING",        "STEP 03: SPONGE SCRUB UNDER TAP"),

    # === BEAT 7 (45.036s -> 48.600s): Mid-Wash Sabotage + 0.60s Dramatic Silence Cliffhanger ===
    (28, 45.036, 46.850, "task_dish_washing.mp4",                 7.35,  0, 7, "UNSCRIPTED SABOTAGE",       "HUMAN ADDS EXTRA SAUCE MID-WASH"),
    (29, 46.850, 48.600, "robustness_sauce.mp4",                 30.20,  0, 7, "EXTRA MUSTARD SQUIRTED!",   "ALERT: UNSEEN DISTURBANCE TEST"),

    # === BEAT 8 (48.600s -> 58.0833s): Emergent Retry, Blackouts, Water Fountain + Seamless Loop ===
    (30, 48.600, 50.250, "robustness_sauce.mp4",                 36.80,  0, 8, "ZERO RETRY CODE WRITTEN",   "VISION-CLOSED LOOP • SCRUBS ON"),
    (31, 50.250, 51.800, "task_dish_washing.mp4",                13.35,  0, 8, "UNTIL PORCELAIN SHINES",    "CLEAN VERIFIED • RACK PLACEMENT"),
    (32, 51.800, 53.170, "task_dish_washing.mp4",                17.10,  0, 8, "AUTONOMOUS TAP SHUTOFF",    "7/7 STEPS COMPLETE • ZERO RESET"),
    (33, 53.170, 54.650, "robustness_light_with_gopro.mp4",       5.80,  0, 8, "WORKS IN BLACKOUTS",        "LIGHTS OUT • GOPRO FISHEYE LOCK"),
    (34, 54.650, 55.850, "in_the_wild_cup_eval.mp4",             24.00,  0, 8, "70% ZERO-SHOT IN WILD",     "6 UNSEEN REAL-WORLD LOCATIONS"),
    (35, 55.850, 57.050, "task_cup_arrangement.mp4",              7.10,  0, 8, "FLOWING WATER FOUNTAIN",    "ESPRESSO SERVED ON LIVE WATER"),
    # Shot 36 winds up at t=0.14..1.17s of task_dynamic_tossing.mp4 -> physically continuous into Shot 1 (t=1.52s)!
    (36, 57.050, 58.0833,"task_dynamic_tossing.mp4",              0.35,  0, 8, "REMEMBER...",               "LOOPING TO LAUNCH • ARXIV:2402.10329"),
]

def validate_shotlist():
    assert len(SHOTS) == 36, f"Expected 36 shots, got {len(SHOTS)}"
    prev_end = 0.0
    by_file = {}
    for s in SHOTS:
        idx, t0, t1, fn, src_t0, crop_b, beat, hdr, tel = s
        assert abs(t0 - prev_end) < 1e-4, f"Gap/overlap at shot {idx}: {t0} vs {prev_end}"
        dur = t1 - t0
        assert 0.95 <= dur <= 2.30, f"Shot {idx} duration {dur:.3f}s outside [0.95, 2.30]s"
        p = os.path.join(FOOTAGE_DIR, fn)
        assert os.path.exists(p), f"Missing clip: {p}"
        out = subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height:format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", p
        ]).decode().strip().splitlines()
        w, h, clip_dur = int(out[0]), int(out[1]), float(out[2])
        assert h == 1080, f"Clip {fn} height {h} != 1080"
        src_t1 = src_t0 + dur
        assert src_t1 <= clip_dur - 0.05, f"Shot {idx} ({fn}) src_t1={src_t1:.2f}s exceeds clip_dur={clip_dur:.2f}s"
        for prev_s0, prev_s1, prev_idx in by_file.get(fn, []):
            overlap = min(src_t1, prev_s1) - max(src_t0, prev_s0)
            assert overlap <= -0.10, f"Shot {idx} overlaps/touches Shot {prev_idx} in {fn}: [{src_t0:.2f},{src_t1:.2f}] vs [{prev_s0:.2f},{prev_s1:.2f}]"
        by_file.setdefault(fn, []).append((src_t0, src_t1, idx))
        prev_end = t1
    print(f"VALIDATED ALL {len(SHOTS)} SHOTS: 100% native 1080p height, ZERO scene/interval overlaps, exact {prev_end:.4f}s total!")

if __name__ == "__main__":
    validate_shotlist()
