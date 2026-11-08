#!/usr/bin/env python3
"""Render 10 60fps Parallax3D clips using manually art-directed depth layers.

Requires MIT-licensed Parallax3D checked out at the documented revision in
/tmp/parallax3d. No model prediction or physical 3D reconstruction is implied.
"""
import os, sys, subprocess
from pathlib import Path
import cv2, numpy as np, imageio_ffmpeg
sys.path.insert(0, '/tmp/parallax3d/parallax_3d')
from pipeline.segmenter import segment_layers
from pipeline.layer_extractor import extract_layers
from pipeline.inpainter import inpaint_background
from pipeline.motion_sim import simulate_motion, compute_frame_transforms
from pipeline.frame_gen import _apply_affine, _alpha_composite

cv2.setNumThreads(3)
source=Path('/home/user/sss005/visuals')
out=Path('/home/user/agents/.cache/library/footage/frb_parallax')
out.mkdir(parents=True,exist_ok=True)
w,h=1376,768
# Art-directed elliptical depth layers: center, axes, rotation. Neither derived
# from a model nor scientifically meaningful; values chosen for each artwork.
shapes=[(.50,.51,.27,.22,32),(.18,.28,.16,.25,0),(.50,.82,.48,.21,0),(.40,.50,.22,.34,0),(.37,.53,.20,.35,0),(.52,.50,.42,.13,0),(.60,.49,.18,.25,0),(.53,.52,.16,.24,0),(.60,.54,.20,.36,0),(.37,.52,.16,.20,0)]
nframes=324 # 5.4 seconds, enough for every 5.218-second shot and offset
ff=imageio_ffmpeg.get_ffmpeg_exe()
for i,(cx,cy,ax,ay,angle) in enumerate(shapes):
    img=cv2.imread(str(source/f'scene{i:02}.png'))
    if img is None: raise FileNotFoundError(source/f'scene{i:02}.png')
    img=cv2.resize(img,(w,h),interpolation=cv2.INTER_AREA)
    depth=np.full((h,w),.08,np.float32)
    cv2.ellipse(depth,(int(w*cx),int(h*cy)),(int(w*ax),int(h*ay)),angle,0,360,.46,-1)
    cv2.ellipse(depth,(int(w*cx),int(h*cy)),(max(1,int(w*ax*.65)),max(1,int(h*ay*.65))),angle,0,360,.91,-1)
    depth=cv2.GaussianBlur(depth,(51,51),18)
    masks,_=segment_layers(depth,img)
    layers=extract_layers(img,masks)
    bg=inpaint_background(layers)
    cfg=simulate_motion('horizontal' if i%3 else 'vertical', intensity=9.0, depth_exag=1.4)
    motion=compute_frame_transforms(cfg,nframes)
    path=out/f'scene{i:02}.mp4'
    proc=subprocess.Popen([ff,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r','60','-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','17','-threads','3','-pix_fmt','yuv420p',str(path)],stdin=subprocess.PIPE)
    try:
        for transforms in motion:
            canvas=bg.astype(np.float32)
            for name in ('background','midground','foreground'):
                warped=_apply_affine(layers[name],*transforms[name],(h,w))
                canvas=_alpha_composite(canvas,warped)
            proc.stdin.write(np.clip(canvas,0,255).astype(np.uint8).tobytes())
        proc.stdin.close()
        if proc.wait()!=0: raise RuntimeError(f'ffmpeg failed: {path}')
    except BaseException:
        proc.kill();proc.wait();raise
    print(f'Finished {path}',flush=True)
# Reuse the previously prepared simulation frame with camera movement; it is
# NOT AI-estimated depth and does not receive fabricated 3D reconstruction.
sim=Path('/home/user/agents/.cache/library/footage/frb/simulation_smooth.mp4')
if not sim.exists(): raise FileNotFoundError(sim)
import shutil
shutil.copyfile(sim,out/'simulation_smooth.mp4')
