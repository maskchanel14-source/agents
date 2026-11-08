#!/usr/bin/env python3
"""Make ten camera-move clips from AI illustrations and prepare the CC BY simulation.

AI stills: /home/user/sss005/visuals/scene00.png ... scene09.png.
Scientific map: /tmp/sss005_frb/full-sky-tng/Konietzka2025_full_sky_evolution.mp4.
Neither AI art nor simulation is real footage; both are identified on screen.
"""
from pathlib import Path
import imageio_ffmpeg,subprocess
ff=imageio_ffmpeg.get_ffmpeg_exe(); src=Path('/home/user/sss005/visuals'); out=Path('/home/user/agents/.cache/library/footage/frb');out.mkdir(parents=True,exist_ok=True)
for i in range(10):
 inp=src/f'scene{i:02}.png';direction=1 if i%2==0 else -1
 x=f'iw/2-iw/zoom/2+({direction})*0.025*iw*sin(on/210)'
 vf=f"zoompan=z='1.035+0.00020*on':x='{x}':y='ih/2-ih/zoom/2':d=1:s=1376x768:fps=30,format=yuv420p"
 subprocess.run([ff,'-y','-v','error','-loop','1','-i',str(inp),'-t','6.5','-vf',vf,'-an','-c:v','libx264','-preset','veryfast','-crf','17','-threads','3',str(out/f'scene{i:02}.mp4')],check=True)
 print('AI illustration',i,flush=True)
sim='/tmp/sss005_frb/full-sky-tng/Konietzka2025_full_sky_evolution.mp4'
subprocess.run([ff,'-y','-v','error','-i',sim,'-vf','scale=-2:1080,format=yuv420p','-an','-c:v','libx264','-preset','veryfast','-crf','17','-threads','3',str(out/'simulation.mp4')],check=True)
print('CC BY 4.0 simulation prepared')
