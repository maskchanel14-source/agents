# SSS-001 — Quality Control & Provenance Report

## 1. Stream & Audio Mastering Audit (`ffprobe` + `ebur128`)

- **File:** `SSS-001_Ghost_Walls_Robot_Parkour_UltraHD_1080p60.mp4`
- **Size:** `97,896,003` bytes (`93.36 MiB`, within `< 100 MB` Google Drive upload threshold)
- **Video Stream:** H.264 (`High@L4.2`), `yuv420p`, `1080×1920` (`9:16`), `60/1` fps, `3,484` frames (`58.066667 s`), `13,218,814 bps` (`13.22 Mbps`)
- **Audio Stream:** AAC LC, `48,000 Hz`, `2` channels (stereo), `255,586 bps` (`256 kbps`), `58.066292 s`
- **Container Bitrate:** `13,487,394 bps` (`13.49 Mbps`)
- **EBU R128 Loudness:**
  - Integrated Loudness: `-14.0 LUFS`
  - Loudness Range (`LRA`): `10.9 LU`
  - True Peak: `-1.3 dBFS`

## 2. Zero-Repetition 35-Shot Provenance Audit

All **35 motion shots** (`frames 1..3484`) draw from **35 distinct `.mp4` / `.mov` source files** (`0` repeated clips across the entire Short):

- **22 clips** from `robot-parkour/robot-parkour.github.io` (*Robot Parkour Learning*, Stanford / CMU / ShanghaiTech, CoRL 2023 Oral)
- **6 clips** from `extreme-parkour/extreme-parkour.github.io` (*Extreme Parkour with Legged Robots*, CMU, ICRA 2024 — same black Unitree A1 + front Intel RealSense D435 depth camera)
- **7 clips** from `vision-locomotion/vision-locomotion.github.io` (*Legged Locomotion in Challenging Terrains using Egocentric Vision*, CMU / UC Berkeley, CoRL 2022 — same black Unitree A1 + front Intel RealSense D435 depth camera)

| Shot | Frames | Time (s) | Source Clip | Scene Description |
| :--- | :--- | :--- | :--- | :--- |
| Cover | `0..1` | `0.00–0.02` | `cover-9x16.jpg` | Custom `9:16` viral Shorts cover (`GHOST WALLS?!`) |
| 01 | `1..89` | `0.02–1.48` | `robot_parkour/leap_1_1.mp4` | Outdoor brick gap leap (side profile) |
| 02 | `89..166` | `1.48–2.77` | `robot_parkour/leap_indoor_1.mp4` | Indoor elevated red-table gap leap |
| 03 | `166..236` | `2.77–3.93` | `extreme_parkour/Outdoor_Gap0.5.mp4` | Outdoor wooden park-bench jump |
| 04 | `236..308` | `3.93–5.13` | `vision_locomotion/nsh_downstairs.mov` | 1080p close-up of nose-mounted depth camera |
| 05 | `308..407` | `5.13–6.78` | `robot_parkour/climb_1_1.mp4` | Plaza 0.40 m concrete plinth vault (close-up) |
| 06 | `407..507` | `6.78–8.45` | `robot_parkour/climb_1_2.mp4` | Wide wall climb (`1.53×` robot height) |
| 07 | `507..611` | `8.45–10.18` | `robot_parkour/climb_night_2.mp4` | Pitch-darkness outdoor night wall climb |
| 08 | `611..701` | `10.18–11.68` | `robot_parkour/crawl_1_4.mp4` | Outdoor grass belly-crawl under utility cart |
| 09 | `701..791` | `11.68–13.18` | `robot_parkour/crawl_2_2.mp4` | Indoor 20 cm acoustic barrier belly-crawl |
| 10 | `791..909` | `13.18–15.15` | `robot_parkour/tilt_2.mp4` | Corridor two-leg diagonal tilt |
| 11 | `909..1040` | `15.15–17.33` | `robot_parkour/tilt_1.mp4` | Emerging sideways on two legs through 28 cm slit |
| 12 | `1040..1149` | `17.33–19.15` | `robot_parkour/failure-leap-low-friction.mp4` | Low-friction table gap slip failure |
| 13 | `1149..1235` | `19.15–20.58` | `vision_locomotion/failure-curb-compressed.mp4` | Outdoor brick-porch curb tumble failure |
| 14 | `1235..1305` | `20.58–21.75` | `extreme_parkour/Ramp.mp4` | Steep tilted ramp slide failure |
| 15 | `1305..1375` | `21.75–22.92` | `robot_parkour/failure-climb-too-high.mp4` | Stopped cold slamming solid wooden wall |
| 16 | `1375..1485` | `22.92–24.75` | `robot_parkour/climb_husky_1.mp4` | Robotics lab vault beside Husky mobile base |
| 17 | `1485..1594` | `24.75–26.57` | `robot_parkour/failure-climb-soft-objects.mp4` | Plunging into soft lab sofa cushions |
| 18 | `1594..1660` | `26.57–27.67` | `extreme_parkour/FullParkourStep_Perfect.mp4` | CMU lab multi-box step course |
| 19 | `1660..1725` | `27.67–28.75` | `extreme_parkour/Ramp1.mp4` | Steep black ramp traversal |
| 20 | `1725..1866` | `28.75–31.10` | `robot_parkour/soft-dyanmics.mp4` | Stage-1 Isaac Gym "Ghost Wall" penetration sim |
| 21 | `1866..1983` | `31.10–33.05` | `robot_parkour/crawl_1_5.mp4` | Low-angle blue gym-mat barrier pass |
| 22 | `1983..2078` | `33.05–34.63` | `vision_locomotion/stepping-stones-failure-compressed.mp4` | Stepping-stool foot overlap slip |
| 23 | `2078..2176` | `34.63–36.27` | `extreme_parkour/Step0.4-bottom_view.mp4` | Low-angle upward view of front-paw edge clearance |
| 24 | `2176..2311` | `36.27–38.52` | `robot_parkour/go1_climb_1.mp4` | Unitree Go1 dynamic padded-block climb |
| 25 | `2311..2394` | `38.52–39.90` | `robot_parkour/go1_crawl_1.mp4` | Unitree Go1 flat crawl under red sofa |
| 26 | `2394..2480` | `39.90–41.33` | `robot_parkour/parkour.mp4` | 1080p60 full indoor course table vault |
| 27 | `2480..2591` | `41.33–43.18` | `robot_parkour/hard-dynamics.mp4` | Stage-2 Isaac Gym solid-wall hard physics sim |
| 28 | `2591..2704` | `43.18–45.07` | `robot_parkour/go1_leap_1.mp4` | Unitree Go1 explosive leap over yellow stools |
| 29 | `2704..2762` | `45.07–46.03` | `vision_locomotion/berkeley-multiple-rocks-compressed.mp4` | Outdoor granite boulder scramble |
| 30 | `2762..2819` | `46.03–46.98` | `vision_locomotion/hard-wild-stairs-compressed-v2.mp4` | Wild mossy forest stone stairs |
| 31 | `2819..2876` | `46.98–47.93` | `vision_locomotion/muddy-slope-compressed-v2.mp4` | Night amber-lit outdoor slope climb |
| 32 | `2876..3038` | `47.93–50.63` | `robot_parkour/retry_2.mp4` | Stopped cold at steep barrier wall & drop-back |
| 33 | `3038..3141` | `50.63–52.35` | `vision_locomotion/rock-compressed-v2.mp4` | Outdoor boulder ledge front-paw probe |
| 34 | `3141..3434` | `52.35–57.23` | `robot_parkour/climb_2.mp4` | Unbroken brick/stone wall push-back & 2nd charge summit |
| 35 | `3434..3484` | `57.23–58.07` | `robot_parkour/leap_1_2.mp4` | Seamless-loop brick chasm launch into Shot 01 |
