# 35 Shots — 35 100% Distinct Source Video Files (ZERO repeats across the entire 58.066s Short!)
# Format: (start_frame, end_frame, rel_path, ss_sec, speed, crop_spec, zoom_start, zoom_end, note)
# crop_spec:
#   ("pan", xc_start, xc_end)  -> 9:16 full-height crop with smooth horizontal tracking pan
#   ("box", xc, y0, y1)        -> 9:16 sub-box crop from y0..y1 centered at pixel xc

SHOTS = [
    # Beat 1 (0.02s - 5.13s): "Nobody taught this robot how to jump. No motion capture. Just one nose camera."
    (1,     89,  "robot_parkour/leap_1_1.mp4",                       0.80, 1.00, ("pan", 0.36, 0.62), 1.00, 1.05, "01 Outdoor brick gap leap"),
    (89,   166,  "robot_parkour/leap_indoor_1.mp4",                  1.62, 1.00, ("pan", 0.36, 0.62), 1.00, 1.05, "02 Indoor red-table gap leap"),
    (166,  236,  "extreme_parkour/Outdoor_Gap0.5.mp4",               1.55, 1.00, ("pan", 0.54, 0.62), 1.02, 1.06, "03 Outdoor wooden bench jump"),
    (236,  308,  "vision_locomotion/nsh_downstairs.mov",             3.60, 1.00, ("pan", 0.48, 0.50), 1.00, 1.06, "04 1080p nose depth camera"),

    # Beat 2 (5.13s - 10.18s): "Yet it vaults concrete walls taller than its body, even in pitch darkness."
    (308,  407,  "robot_parkour/climb_1_1.mp4",                      0.80, 1.00, ("pan", 0.68, 0.54), 1.00, 1.05, "05 Plaza concrete plinth vault"),
    (407,  507,  "robot_parkour/climb_1_2.mp4",                      1.25, 1.00, ("pan", 0.44, 0.56), 1.00, 1.05, "06 Wide tall wall climb 1.53x"),
    (507,  611,  "robot_parkour/climb_night_2.mp4",                  0.85, 1.00, ("pan", 0.48, 0.40), 1.00, 1.06, "07 Pitch-black night wall climb"),

    # Beat 3 (10.18s - 17.33s): "It crawls flat under twenty-centimeter gaps, and tilts onto two legs through slits narrower than its shoulders."
    (611,  701,  "robot_parkour/crawl_1_4.mp4",                      1.50, 1.00, ("pan", 0.54, 0.40), 1.00, 1.05, "08 Outdoor grass crawl under cart"),
    (701,  791,  "robot_parkour/crawl_2_2.mp4",                      1.25, 1.00, ("pan", 0.66, 0.46), 1.00, 1.05, "09 Indoor 20cm low barrier crawl"),
    (791,  909,  "robot_parkour/tilt_2.mp4",                         1.35, 1.00, ("pan", 0.48, 0.46), 1.00, 1.06, "10 Corridor 2-leg diagonal tilt"),
    (909, 1040,  "robot_parkour/tilt_1.mp4",                        16.50, 1.00, ("pan", 0.52, 0.50), 1.02, 1.08, "11 Emerging sideways thru 28cm slit"),

    # Beat 4 (17.33s - 22.92s): "Most robots learning stunts like this crash thousands of times, stopped cold by solid walls."
    (1040, 1149, "robot_parkour/failure-leap-low-friction.mp4",      0.95, 1.00, ("pan", 0.56, 0.54), 1.00, 1.05, "12 Low-friction gap slip wipeout"),
    (1149, 1235, "vision_locomotion/failure-curb-compressed.mp4",    1.35, 1.00, ("pan", 0.48, 0.48), 1.02, 1.07, "13 Outdoor brick porch curb crash"),
    (1235, 1305, "extreme_parkour/Ramp.mp4",                         1.10, 1.00, ("pan", 0.54, 0.58), 1.00, 1.05, "14 Steep ramp slide failure"),
    (1305, 1375, "robot_parkour/failure-climb-too-high.mp4",         2.90, 1.00, ("pan", 0.56, 0.50), 1.00, 1.06, "15 Stopped cold slamming crate wall"),

    # Beat 5 (22.92s - 31.10s): "So Stanford and Carnegie Mellon engineers broke physics first. For twelve hours in simulation, they turned walls into ghosts."
    (1375, 1485, "robot_parkour/climb_husky_1.mp4",                  0.60, 1.00, ("pan", 0.66, 0.48), 1.00, 1.05, "16 Robotics lab Husky box vault"),
    (1485, 1594, "robot_parkour/failure-climb-soft-objects.mp4",     2.40, 1.00, ("pan", 0.66, 0.62), 1.00, 1.05, "17 Soft blue cushions lab plunge"),
    (1594, 1660, "extreme_parkour/FullParkourStep_Perfect.mp4",      2.80, 1.00, ("pan", 0.46, 0.48), 1.00, 1.05, "18 CMU lab multi-box step course"),
    (1660, 1725, "extreme_parkour/Ramp1.mp4",                        0.90, 1.00, ("pan", 0.46, 0.54), 1.00, 1.05, "19 Tilted black ramp traversal"),
    (1725, 1866, "robot_parkour/soft-dyanmics.mp4",                  5.10, 1.00, ("box", 945, 366, 710), 1.00, 1.05, "20 Stage-1 Ghost Wall sim phasing"),

    # Beat 6a (31.10s - 36.27s): "It walked straight through barriers, but paid a penalty for every millimeter of overlap."
    (1866, 1983, "robot_parkour/crawl_1_5.mp4",                      0.85, 1.00, ("pan", 0.56, 0.62), 1.00, 1.05, "21 Blue mat low barrier pass"),
    (1983, 2078, "vision_locomotion/stepping-stones-failure-compressed.mp4", 1.50, 1.00, ("pan", 0.50, 0.50), 1.00, 1.06, "22 Stepping-stool foot overlap slip"),
    (2078, 2176, "extreme_parkour/Step0.4-bottom_view.mp4",          1.05, 1.00, ("pan", 0.66, 0.52), 1.00, 1.06, "23 Low-angle paw clearance over edge"),

    # Beat 6b (36.27s - 45.07s): "To escape it, the AI invented climbing, crawling, and tilting on its own, before six hours of real physics locked those instincts in."
    (2176, 2311, "robot_parkour/go1_climb_1.mp4",                    0.20, 1.00, ("pan", 0.46, 0.46), 1.00, 1.05, "24 Go1 dynamic padded block climb"),
    (2311, 2394, "robot_parkour/go1_crawl_1.mp4",                    1.55, 1.00, ("pan", 0.52, 0.56), 1.00, 1.05, "25 Go1 flat belly crawl under sofa"),
    (2394, 2480, "robot_parkour/parkour.mp4",                        5.95, 1.00, ("pan", 0.54, 0.58), 1.00, 1.05, "26 1080p60 full course table vault"),
    (2480, 2591, "robot_parkour/hard-dynamics.mp4",                  5.40, 1.00, ("box", 965, 366, 710), 1.00, 1.05, "27 Stage-2 Solid Physics sim"),
    (2591, 2704, "robot_parkour/go1_leap_1.mp4",                     1.35, 1.00, ("pan", 0.68, 0.42), 1.00, 1.06, "28 Go1 explosive leap over stools"),

    # Beat 7 (45.07s - 58.05s): "Outdoors, something eerie emerged. When a brick wall stops it cold... Nobody coded a retry, yet it shoves off the stone for run-up space, and clears the ledge on the second charge. Remember..."
    (2704, 2762, "vision_locomotion/berkeley-multiple-rocks-compressed.mp4", 6.80, 1.00, ("pan", 0.48, 0.48), 1.00, 1.05, "29 Outdoor granite boulders scramble"),
    (2762, 2819, "vision_locomotion/hard-wild-stairs-compressed-v2.mp4",    22.00, 1.00, ("pan", 0.46, 0.50), 1.00, 1.05, "30 Wild mossy forest stone stairs"),
    (2819, 2876, "vision_locomotion/muddy-slope-compressed-v2.mp4",          5.00, 1.00, ("pan", 0.50, 0.52), 1.00, 1.06, "31 Eerie night amber slope climb"),
    (2876, 3038, "robot_parkour/retry_2.mp4",                                5.35, 1.00, ("box", 390,   0, 602), 1.00, 1.05, "32 Stopped cold at steep wall & drop"),
    (3038, 3141, "vision_locomotion/rock-compressed-v2.mp4",                 1.90, 1.00, ("pan", 0.62, 0.54), 1.00, 1.05, "33 Outdoor rock ledge front-paw probe"),
    (3141, 3434, "robot_parkour/climb_2.mp4",                                4.90, 1.00, ("pan", 0.48, 0.54), 1.00, 1.06, "34 Brick/stone push-back & 2nd charge"),
    (3434, 3483, "robot_parkour/leap_1_2.mp4",                               1.68, 1.00, ("pan", 0.48, 0.48), 1.00, 1.05, "35 Seamless loop brick chasm launch"),
]

if __name__ == "__main__":
    paths = [s[2] for s in SHOTS]
    assert len(paths) == len(set(paths)), f"DUPLICATE: {[p for p in paths if paths.count(p)>1]}"
    assert SHOTS[0][0] == 1 and SHOTS[-1][1] == 3483
    for a, b in zip(SHOTS, SHOTS[1:]):
        assert a[1] == b[0], f"Gap between {a} and {b}"
    print(f"VERIFIED: {len(SHOTS)} contiguous shots (frames 1..3483), {len(set(paths))} 100% UNIQUE source video files! 0 repeats!")
