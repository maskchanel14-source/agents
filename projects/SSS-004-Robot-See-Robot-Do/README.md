# SSS-004 — Robot See Robot Do

An English narrated Short about Kerr et al., *Robot See Robot Do: Imitating Articulated Object Manipulation with Monocular 4D Reconstruction*, CoRL 2024. The method uses a multi-view scan AND one monocular demonstration, not video alone. Source and limitations: <https://robot-see-robot-do.github.io/> and <https://openreview.net/forum?id=2LLu3gavF1>.

## Footage and rights

Research clips are sourced from <https://github.com/robot-see-robot-do/robot-see-robot-do.github.io>. No explicit footage license was found in that repository: clear permission or independently assess rights before publishing. AI-generated cover is an illustration, not research imagery. The original clips are not in Git. Six 2160p clips were downsampled to 1080p, the rest were 1080p. `shotlist.py` validates 36 time-disjoint intervals across 12 research files; that is not a guarantee that different research files contain different scenes. The physical-loop requirement was not verified.

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
```

## Production

`build_audio.py` expects the eight approved narration WAV segments in `/home/user/sss004/audio/`, and writes temporary voice, music and SFX WAV stems plus `master_mix.wav` in `/tmp/sss004_build/`. They are not committed. Narration was independently auditioned in this session; `voice-02` is a session ID and is not a persistent identity. Music and SFX are synthesized from original tones following the creator-approved SSS-003 loud mix as a starting point; subjective balance must still be auditioned.

`render_ultrahd.py` adapts the SSS-003 engine and reads `timings.json`, `shotlist.py`, the temporary master, footage and cover in `/home/user/deliverables/SSS-004/`. Captions split by text proportion are approximate and should be checked against the audio. `publishing-kit.txt` includes attribution, suggested description and manual pinned comment. No claim is made that viewer engagement or music audibility was measured subjectively.
