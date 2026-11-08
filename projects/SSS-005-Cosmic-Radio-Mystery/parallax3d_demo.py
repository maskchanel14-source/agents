#!/usr/bin/env python3
"""CPU demonstration using Parallax3D's segmentation, layers and compositor.

Clone https://github.com/Shruti2005dwivedi/Parallax3d at commit
31b877791e3e52e7b3f270c0242ff098d9e8adf4 into /tmp/parallax3d first.
The depth map is ART-DIRECTED, not predicted: it is specific to scene00.
"""
import math
from pathlib import Path
import subprocess
import sys
import cv2
import numpy as np
import imageio_ffmpeg

sys.path.insert(0, '/tmp/parallax3d/parallax_3d')
from pipeline.segmenter import segment_layers
from pipeline.layer_extractor import extract_layers
from pipeline.inpainter import inpaint_background
from pipeline.motion_sim import simulate_motion, compute_frame_transforms
from pipeline.frame_gen import _apply_affine, _alpha_composite

source = Path('/home/user/sss005/visuals/scene00.png')
output = Path('/home/user/deliverables/SSS-005/SSS-005_Parallax3D_Test.mp4')
image = cv2.imread(str(source))
if image is None:
    raise FileNotFoundError(source)
w, h = 688, 384
image = cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)
# A manually placed, blurred oval separates the central galaxy from the sky;
# it is an artistic depth approximation, not a model inference or real depth.
depth = np.full((h, w), 0.08, dtype=np.float32)
cv2.ellipse(depth, (348, 202), (187, 83), 32, 0, 360, 0.46, -1)
cv2.ellipse(depth, (347, 198), (115, 44), 32, 0, 360, 0.91, -1)
depth = cv2.GaussianBlur(depth, (31, 31), 11)
masks, _ = segment_layers(depth, image)
layers = extract_layers(image, masks)
background = inpaint_background(layers)
cfg = simulate_motion(direction='horizontal', intensity=7.0, depth_exag=1.4)
transforms = compute_frame_transforms(cfg, 300)
output.parent.mkdir(parents=True, exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [ff, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{w}x{h}', '-r', '60', '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', str(output)]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
try:
    for motion in transforms:
        canvas = background.astype(np.float32)
        for name in ['background', 'midground', 'foreground']:
            warped = _apply_affine(layers[name], *motion[name], (h, w))
            canvas = _alpha_composite(canvas, warped)
        p.stdin.write(np.clip(canvas, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError('ffmpeg failed')
except BaseException:
    p.kill()
    p.wait()
    raise
print(output)
