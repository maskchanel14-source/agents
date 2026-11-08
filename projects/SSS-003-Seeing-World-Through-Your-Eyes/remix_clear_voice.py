#!/usr/bin/env python3
"""Remux an existing SSS-003 video with its synced voiceover brought forward.

Usage: python remix_clear_voice.py ORIGINAL.mp4 VOICEOVER.mp3 OUTPUT.mp4
The original mix is retained quietly underneath; its narration is also present,
so both inputs must be the matching, time-aligned SSS-003 deliverables.
"""
import subprocess
import sys
from build_audio import FFMPEG

if len(sys.argv) != 4:
    raise SystemExit(__doc__)
original, voice, output = sys.argv[1:]
if output in (original, voice):
    raise SystemExit('Output must differ from both inputs')
filters = (
    '[0:a]volume=0.08[background];'
    '[1:a]highpass=f=80,equalizer=f=2800:t=q:w=1:g=3[voice];'
    '[voice][background]amix=inputs=2:duration=first:normalize=0,'
    'alimiter=limit=0.87:level=0,aresample=48000[a]'
)
subprocess.run([FFMPEG, '-y', '-v', 'error', '-i', original, '-i', voice,
                '-filter_complex', filters, '-map', '0:v:0', '-map', '[a]',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k',
                '-movflags', '+faststart', '-shortest', output], check=True)
