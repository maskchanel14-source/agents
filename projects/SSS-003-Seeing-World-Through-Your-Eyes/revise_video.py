#!/usr/bin/env python3
"""Narration-forward SSS-003 revision with synced captions, score and effects.

Requires the original MP4, eight selected-voice WAVs in AUDIO_DIR and ffmpeg.
Example: python revise_video.py ORIGINAL.mp4 AUDIO_DIR OUTPUT_DIR
"""
import json, sys, os, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from build_audio import FFMPEG, SR

if len(sys.argv) != 4:
    raise SystemExit(__doc__)
original, audio_dir, output_dir = sys.argv[1:]
out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
tmp = Path(audio_dir); tmp.mkdir(parents=True, exist_ok=True)
base = Path(__file__).parent
meta = json.loads((base / 'timings.json').read_text())
beats = meta['beats']; duration = meta['total_frames_60fps'] / 60
N = round(duration * SR)
# The two panels per beat follow the narration's semantic halves.
captions = [
('Your selfie hides a tiny reflection.','Could AI reconstruct the room\nfrom your eyes?'),
('The cornea curves like a tiny mirror,\nwith a radius of about 7.8 mm.','Its reflection can hold clues\nto the world in front of you.'),
('Maryland researchers used portrait videos','and a 3D neural radiance field\nto explore these reflections.'),
('Two obstacles stood in the way:\ntiny shifts as the eye moves,','and the colored iris, which can\noverwhelm the reflected scene.'),
("The method estimates\nthe cornea's pose",'and separates the iris texture\nfrom reflected light.'),
('With enough head movement,\nit can reveal rough 3D scenes.','It is not a perfect reconstruction;\nfewer views limit the result.'),
('They even tested music videos\nfeaturing Miley Cyrus and Lady Gaga.','So what did they find?'),
('Only rough traces of the studio,\nnot a clear picture.','Like to save this paper, and subscribe\nfor the next Dark Science discovery.')]
voice = np.zeros(N, dtype=np.float32); spans=[]
for i,b in enumerate(beats):
    src = tmp / f'b{i+1}.wav'
    with wave.open(str(src), 'rb') as w: source_duration = w.getnframes()/w.getframerate()
    start = b['start']; end = b['end']; available = end-start-0.06
    speed = max(1.0, source_duration/available)
    target = tmp / f'fit{i+1}.wav'
    subprocess.run([FFMPEG,'-y','-v','error','-i',str(src),'-af',f'atempo={speed:.7f},highpass=f=75,equalizer=f=2800:t=q:w=1:g=2', '-ar',str(SR),'-ac','1','-c:a','pcm_s16le',str(target)],check=True)
    with wave.open(str(target),'rb') as w: x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
    x=x[:int(available*SR)]; peak=np.max(np.abs(x)) or 1
    x=x * min(0.88/peak,1.4)
    at=round(start*SR); voice[at:at+len(x)] += x
    actual_end=start+len(x)/SR; spans.append((start, actual_end))
    print('beat', i+1, 'speed',round(speed,2),'span',round(start,2),round(actual_end,2),flush=True)
# A restrained, original dark-science score: slow harmonic pad, pulse and shimmer.
t=np.arange(N,dtype=np.float32)/SR
chords=[(69.30,82.41,103.83),(55.00,69.30,82.41),(61.74,77.78,92.50),(51.91,65.41,77.78)]
score=np.zeros((N,2),dtype=np.float32)
for j in range(4):
    env=np.zeros(N,dtype=np.float32)
    for k in range(j, int(duration/8)+1, 4):
        a=int(k*8*SR); z=min(N,int((k+8.6)*SR)); tt=np.arange(z-a,dtype=np.float32)/SR
        env[a:z]=np.maximum(env[a:z], np.minimum(1,tt/1.0)*np.minimum(1,(z-a)/SR-tt))
    for h,f in enumerate(chords[j]):
        score[:,0] += (0.035/(h+1)**.5)*env*np.sin(2*np.pi*f*t + h*.6)
        score[:,1] += (0.035/(h+1)**.5)*env*np.sin(2*np.pi*f*1.001*t + h*.6+.2)
pulse=(np.maximum(0,np.sin(2*np.pi*0.5*t))**12)
score[:,0] += .008*pulse*np.sin(2*np.pi*277.18*t)
score[:,1] += .008*pulse*np.sin(2*np.pi*277.5*t+.8)
# Midrange repeating tones survive small phone speakers better than a sub-bass pad.
notes = [277.18, 329.63, 415.30, 329.63, 220.00, 277.18, 329.63, 277.18]
step = (t * 2).astype(np.int32)
freq = np.take(notes, step % len(notes))
phase = np.cumsum(freq, dtype=np.float64) * (2*np.pi/SR)
pluck = np.exp(-4.2 * ((t * 2) % 1))
score[:,0] += .018 * pluck * np.sin(phase)
score[:,1] += .018 * pluck * np.sin(phase + .25)
# Short restrained risers and low impacts on story transitions.
for b in beats[1:]:
    p=int(b['start']*SR); length=int(.55*SR); a=max(0,p-int(.28*SR)); z=min(N,a+length)
    q=np.arange(z-a,dtype=np.float32)/SR
    hit=.027*np.exp(-q*8)*np.sin(2*np.pi*(72*q-28*q*q))
    score[a:z,0]+=hit; score[a:z,1]+=hit*.88
fade=np.minimum(1,t/.8)*np.minimum(1,np.maximum(0,(duration-t)/.5))
score*=fade[:,None]
# Gentle dynamic ducking, keeping the music audible under words.
window=int(.12*SR)
padded=np.pad(np.abs(voice), (window//2, window-window//2), mode='edge')
cumulative=np.concatenate(([0.0], np.cumsum(padded, dtype=np.float64)))
activity=((cumulative[window:]-cumulative[:-window])/window)[:N]
duck=1-.22*np.clip(activity/.08,0,1)
score*=duck[:,None] * 4.2
mix=np.stack([voice,voice],axis=1)*.78 + score
# Keep headroom rather than hard-clipping peaks; final limiter follows muxing.
peak=np.max(np.abs(mix))
if peak > .92: mix *= .92/peak
def wav(path,data,channels):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(channels); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(data,-1,1)*32767).astype('<i2').tobytes())
wav(tmp/'mix.wav',mix,2); wav(tmp/'voice.wav',voice,1)
subprocess.run([FFMPEG,'-y','-v','error','-i',str(tmp/'voice.wav'),'-c:a','libmp3lame','-b:a','192k',str(out/'SSS-003_Revised_Voiceover.mp3')],check=True)
# Cover old burned-in captions with a matching opaque dark panel; place new captions on top.
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',38)
for i,(left,right) in enumerate(captions):
    for j,text in enumerate((left,right)):
        im=Image.new('RGBA',(1080,210),(8,12,22,255)); d=ImageDraw.Draw(im)
        d.rounded_rectangle((40,8,1040,196),radius=22,outline=(201,162,91,255),width=2)
        lines=text.split('\n'); yy=53 if len(lines)==2 else 76
        for line in lines:
            width=d.textbbox((0,0),line,font=font)[2]; d.text(((1080-width)//2,yy),line,font=font,fill=(248,250,252,255)); yy+=54
        im.save(tmp/f'cap{i+1}_{j}.png')
# One caption image sequence, one image per semantic segment; overlay via concat demuxer.
entries=[]; srt=[]
def stamp(v):
    ms=round(v*1000); return f'{ms//3600000:02}:{(ms//60000)%60:02}:{(ms//1000)%60:02},{ms%1000:03}'
for i,(start,end) in enumerate(spans):
    mid=start+(end-start)*(.57 if i!=6 else .75)
    next_start=spans[i+1][0] if i+1<len(spans) else duration
    for j,(a,z) in enumerate(((start,mid),(mid,next_start))):
        if i==0 and j==0: a=0
        entries += [f"file '{(tmp/f'cap{i+1}_{j}.png').resolve()}'",f'duration {z-a:.6f}']
        srt.append(f'{len(srt)+1}\n{stamp(a)} --> {stamp(z)}\n{captions[i][j]}\n')
entries.append(f"file '{(tmp/'cap8_1.png').resolve()}'")
(tmp/'caps.txt').write_text('\n'.join(entries)+'\n')
(out/'SSS-003_Revised_Captions.srt').write_text('\n'.join(srt))
output=out/'SSS-003_Revised_Dark_Science.mp4'
if os.environ.get('SSS_AUDIO_REMIX_ONLY'):
    output=out/'SSS-003_Music_Forward.mp4'
    subprocess.run([FFMPEG,'-y','-v','warning','-i',original,'-i',str(tmp/'mix.wav'),
                    '-filter_complex','[1:a]alimiter=limit=0.88:level=0[a]',
                    '-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','256k',
                    '-movflags','+faststart','-shortest',str(output)],check=True)
    print('Wrote',output,flush=True)
    raise SystemExit(0)
subprocess.run([FFMPEG,'-y','-v','warning','-i',original,'-f','concat','-safe','0','-i',str(tmp/'caps.txt'),'-i',str(tmp/'mix.wav'),
 '-filter_complex','[0:v][1:v]overlay=0:1218:shortest=1:format=auto,format=yuv420p[v];[2:a]alimiter=limit=0.88:level=0[a]',
 '-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-r','60','-c:a','aac','-b:a','256k','-movflags','+faststart','-shortest',str(output)],check=True)
print('Wrote',output,flush=True)
