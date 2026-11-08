#!/usr/bin/env python3
"""Animate ten AI-generated stills with camera moves, not object-level 3D animation.

Inputs: /home/user/sss004/visuals/visual00.png through visual09.png
Outputs: .cache/library/footage/rsrd/cinematic00.mp4 through cinematic09.mp4
The stills are session assets and must be retained or separately archived.
"""
import subprocess
from pathlib import Path
import imageio_ffmpeg

source=Path('/home/user/sss004/visuals')
target=Path('/home/user/agents/.cache/library/footage/rsrd')
target.mkdir(parents=True,exist_ok=True)
ff=imageio_ffmpeg.get_ffmpeg_exe()
for i in range(10):
    src=source/f'visual{i:02}.png'
    if not src.exists(): raise FileNotFoundError(src)
    direction=1 if i%2 == 0 else -1
    # 1376x768 is larger than the 1036-pixel cinema stage; no native image upscale.
    x = f"iw/2-iw/zoom/2+({direction})*0.025*iw*sin(on/150)"
    zoom = "1.035+0.00022*on"
    vf=f"zoompan=z='{zoom}':x='{x}':y='ih/2-ih/zoom/2':d=1:s=1376x768:fps=30,format=yuv420p"
    subprocess.run([ff,'-y','-v','error','-loop','1','-i',str(src),'-t','5.5','-vf',vf,
                    '-an','-c:v','libx264','-preset','veryfast','-crf','17','-threads','3',
                    str(target/f'cinematic{i:02}.mp4')],check=True)
    print('created',i,flush=True)
