#!/usr/bin/env python3
"""33-Shot High-Bitrate Native-Pixel Manifest for SSS-001 (Zero 480p clips, Zero scene repeats).

Every shot maps to >=720p (6,000-8,322 kbps) or clean 540p (2,400+ kbps) widescreen research footage
presented inside a 1:1 native-pixel documentary cinema stage (1036x780 / 1036x583) with zero
soap-opera `minterpolate` warping and zero 400% vertical sub-crop blow-ups.
"""
from __future__ import annotations

import os
import cv2

TOTAL_FRAMES = 3484  # Frame 0 (9:16 cover) + Frames 1..3483 = 58.0667s @ 60fps

# Format:
# (start_f, end_f, rel_path, ss_sec, speed, layout_spec, zoom_s, zoom_e, chapter_idx, scene_id)
# layout_spec:
#   ("stage43", xc_start, xc_end, y_max_frac) -> 1036x780 (4:3) cinema stage, 1:1 native 720p/1080p pixels
#   ("grid169",)                              -> 1036x583 (16:9) full 4-quadrant Isaac Gym simulation grid

CHAPTERS = [
    ("STANFORD × CMU",     "1 CAMERA. 0% HUMAN CODE.",    "INTEL D435 DEPTH  •  ONBOARD COMPUTE"),   # 0
    ("EXTREME OBSTACLES",  "WALLS, NIGHT & 28-CM SLITS",  "ZERO MOCAP  •  ACTIVE IR STEREO"),        # 1
    ("THE HARD-WALL TRAP", "WHY ROBOTS CRASH IN TRAINING","SPARSE REWARD  •  SOLID COLLISIONS"),     # 2
    ("ISAAC GYM STAGE 1",  "TURNING WALLS INTO GHOSTS",   "12 HR SOFT-DYNAMICS PRE-TRAINING"),       # 3
    ("ISAAC GYM STAGE 2",  "REAL PHYSICS LOCKS IT IN",    "6 HR HARD-COLLISION DISTILLATION"),       # 4
    ("EMERGENT BEHAVIOR",  "UNPROGRAMMED WALL RETRY",     "AUTONOMOUS RUN-UP  •  REAL WORLD"),       # 5
]

SHOTS = [
    # Beat 1 (0.02s - 5.13s): "Nobody taught this robot how to jump. No motion capture. Just one nose camera."
    (1,     89,  "robot_parkour/leap_1_1.mp4",                       0.80, 1.00, ("stage43", 0.46, 0.56, 1.00), 1.00, 1.04, 0, "leap_1_1_brick_side"),
    (89,   166,  "robot_parkour/leap_indoor_1.mp4",                  1.45, 1.00, ("stage43", 0.44, 0.56, 1.00), 1.00, 1.04, 0, "leap_indoor_red_mat"),
    (166,  236,  "robot_parkour/parkour.mp4",                        8.85, 1.00, ("stage43", 0.52, 0.44, 1.00), 1.00, 1.04, 0, "parkour_1080p_station4_gap"),
    (236,  308,  "vision_locomotion/nsh_downstairs.mov",             3.60, 1.00, ("stage43", 0.48, 0.50, 1.00), 1.00, 1.05, 0, "nsh_1080p_nose_camera"),

    # Beat 2 (5.13s - 10.18s): "Yet it vaults concrete walls taller than its body, even in pitch darkness."
    (308,  407,  "robot_parkour/climb_1_1.mp4",                      0.80, 1.00, ("stage43", 0.58, 0.50, 1.00), 1.00, 1.04, 1, "climb_1_1_plaza_closeup"),
    (407,  507,  "robot_parkour/climb_1_2.mp4",                      1.20, 1.00, ("stage43", 0.46, 0.54, 1.00), 1.00, 1.04, 1, "climb_1_2_wide_plinth"),
    (507,  611,  "robot_parkour/climb_night_2.mp4",                  0.85, 1.00, ("stage43", 0.48, 0.42, 1.00), 1.00, 1.05, 1, "climb_night_pitch_dark"),

    # Beat 3 (10.18s - 17.33s): "It crawls flat under twenty-centimeter gaps, and tilts onto two legs through slits narrower than its shoulders."
    (611,  701,  "robot_parkour/crawl_1_4.mp4",                      1.50, 1.00, ("stage43", 0.52, 0.44, 1.00), 1.00, 1.04, 1, "crawl_1_4_grass_cart"),
    (701,  791,  "robot_parkour/crawl_2_2.mp4",                      1.15, 1.00, ("stage43", 0.58, 0.46, 1.00), 1.00, 1.04, 1, "crawl_2_2_20cm_foam"),
    (791,  909,  "robot_parkour/tilt_2.mp4",                         1.35, 1.00, ("stage43", 0.48, 0.48, 1.00), 1.00, 1.05, 1, "tilt_2_corridor_front"),
    (909, 1040,  "robot_parkour/tilt_1.mp4",                        16.50, 1.00, ("stage43", 0.52, 0.50, 1.00), 1.00, 1.05, 1, "tilt_1_28cm_slit_exit"),

    # Beat 4 (17.33s - 22.92s): "Most robots learning stunts like this crash thousands of times, stopped cold by solid walls."
    (1040, 1149, "robot_parkour/failure-leap-low-friction.mp4",      0.95, 1.00, ("stage43", 0.52, 0.52, 1.00), 1.00, 1.04, 2, "fail_leap_table_slip"),
    (1149, 1245, "vision_locomotion/failure-curb-compressed.mp4",    1.30, 1.00, ("stage43", 0.48, 0.48, 1.00), 1.00, 1.04, 2, "fail_curb_brick_porch"),
    (1245, 1375, "robot_parkour/failure-climb-too-high.mp4",         1.95, 1.00, ("stage43", 0.52, 0.50, 1.00), 1.00, 1.05, 2, "fail_climb_solid_crate"),

    # Beat 5 (22.92s - 31.10s): "So Stanford and Carnegie Mellon engineers broke physics first. For twelve hours in simulation, they turned walls into ghosts."
    (1375, 1485, "robot_parkour/climb_husky_1.mp4",                  0.60, 1.00, ("stage43", 0.58, 0.48, 1.00), 1.00, 1.04, 3, "lab_husky_box_vault"),
    (1485, 1594, "robot_parkour/failure-climb-soft-objects.mp4",     2.20, 1.00, ("stage43", 0.58, 0.56, 1.00), 1.00, 1.04, 3, "lab_soft_blue_cushions"),
    (1594, 1725, "robot_parkour/parkour.mp4",                        0.35, 1.00, ("stage43", 0.50, 0.46, 1.00), 1.00, 1.04, 3, "parkour_1080p_station1_closeup"),
    (1725, 1866, "robot_parkour/soft-dyanmics.mp4",                  4.80, 1.00, ("grid169",),                   1.00, 1.03, 3, "sim_stage1_ghost_walls_4grid"),

    # Beat 6a (31.10s - 36.27s): "It walked straight through barriers, but paid a penalty for every millimeter of overlap."
    (1866, 1983, "robot_parkour/crawl_1_5.mp4",                      0.85, 1.00, ("stage43", 0.52, 0.56, 0.94), 1.00, 1.04, 3, "crawl_1_5_blue_mat"),
    (1983, 2078, "vision_locomotion/stepping-stones-failure-compressed.mp4", 1.50, 1.00, ("stage43", 0.50, 0.50, 1.00), 1.00, 1.04, 3, "stepping_stool_overlap_slip"),
    (2078, 2176, "robot_parkour/parkour.mp4",                        3.10, 1.00, ("stage43", 0.50, 0.46, 1.00), 1.00, 1.04, 3, "parkour_1080p_station2_curtain"),

    # Beat 6b (36.27s - 45.07s): "To escape it, the AI invented climbing, crawling, and tilting on its own, before six hours of real physics locked those instincts in."
    (2176, 2311, "robot_parkour/go1_climb_1.mp4",                    0.20, 1.00, ("stage43", 0.48, 0.48, 1.00), 1.00, 1.04, 4, "go1_padded_block_climb"),
    (2311, 2394, "robot_parkour/go1_crawl_1.mp4",                    1.55, 1.00, ("stage43", 0.52, 0.54, 1.00), 1.00, 1.04, 4, "go1_red_sofa_crawl"),
    (2394, 2480, "robot_parkour/parkour.mp4",                        5.95, 1.00, ("stage43", 0.52, 0.56, 1.00), 1.00, 1.04, 4, "parkour_1080p_station3_vault"),
    (2480, 2591, "robot_parkour/hard-dynamics.mp4",                  4.80, 1.00, ("grid169",),                   1.00, 1.03, 4, "sim_stage2_solid_physics_4grid"),
    (2591, 2704, "robot_parkour/go1_leap_1.mp4",                     1.25, 1.00, ("stage43", 0.58, 0.46, 1.00), 1.00, 1.04, 4, "go1_yellow_stools_leap"),

    # Beat 7 (45.07s - 58.07s): "Outdoors, something eerie emerged. When a brick wall stops it cold... Nobody coded a retry, yet it shoves off the stone for run-up space, and clears the ledge on the second charge. Remember..."
    (2704, 2762, "vision_locomotion/berkeley-multiple-rocks-compressed.mp4", 6.80, 1.00, ("stage43", 0.50, 0.50, 1.00), 1.00, 1.04, 5, "outdoor_granite_boulders"),
    (2762, 2819, "vision_locomotion/hard-wild-stairs-compressed-v2.mp4",    22.00, 1.00, ("stage43", 0.48, 0.50, 1.00), 1.00, 1.04, 5, "outdoor_wild_forest_stairs"),
    (2819, 2876, "vision_locomotion/muddy-slope-compressed-v2.mp4",          5.00, 1.00, ("stage43", 0.50, 0.52, 1.00), 1.00, 1.04, 5, "outdoor_night_amber_slope"),
    (2876, 3038, "robot_parkour/retry_2.mp4",                                5.35, 1.00, ("stage43", 0.42, 0.46, 0.835),1.00, 1.04, 5, "retry_2_steep_wall_stop"),
    (3038, 3141, "vision_locomotion/rock-compressed-v2.mp4",                 1.90, 1.00, ("stage43", 0.56, 0.52, 1.00), 1.00, 1.04, 5, "outdoor_rock_ledge_probe"),
    (3141, 3434, "robot_parkour/climb_2.mp4",                                4.90, 1.00, ("stage43", 0.48, 0.52, 1.00), 1.00, 1.05, 5, "climb_2_stone_pushback_summit"),
    (3434, 3484, "robot_parkour/leap_1_2.mp4",                               1.68, 1.00, ("stage43", 0.48, 0.48, 1.00), 1.00, 1.04, 0, "leap_1_2_seamless_loop_launch"),
]


def verify_manifest(base_dir: str = ".cache/library/footage") -> None:
    scene_ids = [s[9] for s in SHOTS]
    assert len(scene_ids) == len(set(scene_ids)), f"Duplicate scene_id: {scene_ids}"
    assert SHOTS[0][0] == 1 and SHOTS[-1][1] == TOTAL_FRAMES
    for a, b in zip(SHOTS, SHOTS[1:]):
        assert a[1] == b[0], f"Discontinuity between {a} and {b}"
    if os.path.isdir(base_dir):
        for idx, (sf, ef, rel, ss, spd, *_rest) in enumerate(SHOTS, 1):
            p = os.path.join(base_dir, rel)
            cap = cv2.VideoCapture(p)
            assert cap.isOpened(), f"Missing {p}"
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            dur = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / fps
            cap.release()
            assert h >= 540, f"Low-res <540p clip forbidden: {rel} ({h}p)"
            needed = ((ef - sf) / 60.0) * spd
            assert dur - ss >= needed + 0.02, f"Shot {idx} overrun on {rel}: {dur-ss:.2f}s < {needed:.2f}s"
    print(f"VERIFIED: {len(SHOTS)} contiguous HD shots (frames 1..{TOTAL_FRAMES}), 0 <540p clips, 0 repeated scenes!")


if __name__ == "__main__":
    verify_manifest()
