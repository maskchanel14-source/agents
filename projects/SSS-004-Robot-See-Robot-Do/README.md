# SSS-004 — Robot See Robot Do

An English narrated Short about Kerr et al., *Robot See Robot Do: Imitating Articulated Object Manipulation with Monocular 4D Reconstruction*, CoRL 2024. The method uses a multi-view scan AND one monocular demonstration, not video alone. Source and limitations: <https://robot-see-robot-do.github.io/> and <https://openreview.net/forum?id=2LLu3gavF1>.

## Footage and rights

Research clips are sourced from <https://github.com/robot-see-robot-do/robot-see-robot-do.github.io>. No explicit footage license was found in that repository: clear permission or independently assess rights before publishing. AI-generated cover is an illustration, not research imagery. The original clips are not in Git. The cinematic revision uses 22 distinct sources: 12 separate research clips (including simulated visualizations) and 10 AI-generated illustrative stills, each used once. Some research clips depict the same objects or lab; source uniqueness does not prove scene uniqueness. Original 2160p and larger square research sources are downsampled or cropped to 1080p; lower-resolution research clips are not used. The generated stills are 1376x768 and downsampled into the 1036-pixel display stage. This revision uses 22 cuts instead of the 36-cut SOP template to reduce repetition. The physical-loop requirement was not verified.

File mapping under `data/` in the source repository, to `.cache/library/footage/rsrd/clipNN.mp4`:

```
00 bear_robot_1_trimmed.mp4
01 bear_robot_2_trimmed.mp4
02 nerfgun_robot_1_trimmed.mp4
03 nerfgun_robot_2_trimmed.mp4
04 rsrd_teaser.mp4
05 demo_vids/usb_plug_unplug3.mp4
06 nerfgun_half_turned.mp4
07 nerfgun_straight.mp4
08 red_box.mp4
09 scissors_red.mp4
10 scissors_white.mp4
11 sunglasses.mp4
12 bear_mp_crop.mp4
13 bear_posevary.mp4
14 nerfgun_graspsearch.mp4
15 nerfgun_mp_crop.mp4
16 nerfgun_posevary.mp4
17 scissors_posevary.mp4
```

The prior `diagram00` through `diagram11` illustrations are no longer used. The ten new cinematic images are AI-generated illustrations, not research footage: an on-screen label identifies them. `make_cinematic_visuals.py` adds a camera pan/zoom to each still; this is **not** true 3D geometry or object animation. Input stills live in `/home/user/sss004/visuals/` and are separately archived on Drive; they are not committed to Git.

## Production

`build_audio.py` expects the eight approved narration WAV segments in `/home/user/sss004/audio/`, and writes temporary voice, music and SFX WAV stems plus `master_mix.wav` in `/tmp/sss004_build/`. They are not committed. Narration was independently auditioned in this session; `voice-02` is a session ID and is not a persistent identity. Music and SFX are synthesized from original tones following the creator-approved SSS-003 loud mix as a starting point; subjective balance must still be auditioned.

`render_ultrahd.py` adapts the SSS-003 engine and reads `timings.json`, `shotlist.py`, the temporary master, footage and cover in `/home/user/deliverables/SSS-004/`. Captions split by text proportion are approximate and should be checked against the audio. `publishing-kit.txt` includes attribution, suggested description and manual pinned comment. No claim is made that viewer engagement or music audibility was measured subjectively.

## Music revision

The first render had a music-envelope bug: after roughly 8 seconds most of the chord pad disappeared. `build_audio.py` now calculates each chord end using the actual chord start (`k*8`), keeping the music present throughout. The new mix was measured at 2-second windows across the full timeline but has not been independently auditioned. The user must review music and voice balance on their device. `SSS-004_Music_Only.mp3` provides the music stem for comparison.
