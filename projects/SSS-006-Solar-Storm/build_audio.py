#!/usr/bin/env python3
"""Build SSS-006 narration, captions and audible original electronic score.
Requires eight selected-voice b1.wav..b8.wav at /home/user/sss006/audio.
"""
import json, subprocess, wave
from pathlib import Path
import numpy as np
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe(); sr=48000
work=Path('/tmp/sss006_build'); work.mkdir(parents=True,exist_ok=True)
audio=Path('/home/user/sss006/audio'); out=Path('/home/user/deliverables/SSS-006'); out.mkdir(parents=True,exist_ok=True)
parts=[('In 1989, the Sun helped shut down an entire power grid.', 'Millions of people in Quebec lost electricity for nine hours.'), ("The culprit wasn't sunlight.", 'It was a cloud of magnetized plasma thrown into space by the Sun: a coronal mass ejection.'), ("When it reached Earth, it disturbed our planet's magnetic field.", 'That changing field drove electric currents through the ground and long power lines.'), ("Protective equipment tripped, and Quebec's grid collapsed.", 'The same storm also produced auroras far from the poles.'), ("This wasn't the first warning.", 'In 1859, the Carrington storm disrupted telegraph systems, and some operators reported sparks.'), ('Today, satellites monitor the Sun, and grid operators can prepare.', 'But forecasting exactly how a storm will affect infrastructure remains difficult.'), ('Not every solar storm causes a blackout.', "The danger depends on the storm, Earth's magnetic response, and the grid itself."), ('The lights in the sky are beautiful. They are also a reminder:', 'Our technology lives inside space weather. Save this and subscribe for more real science.')]

chunks=[]; beats=[]; captions=[]; cursor=.15
for i,(a,b) in enumerate(parts):
 src=audio/f'b{i+1}.wav'; fit=work/f'fit{i+1}.wav'
 subprocess.run([ff,'-y','-v','error','-i',str(src),'-af','atempo=1.33,highpass=f=75,equalizer=f=2800:t=q:w=1:g=2','-ar',str(sr),'-ac','1','-c:a','pcm_s16le',str(fit)],check=True)
 with wave.open(str(fit),'rb') as w: x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
 peak=np.max(np.abs(x)) or 1; x=x*min(.86/peak,1.3)
 dur=len(x)/sr; start=cursor; end=cursor+dur
 # Split captions proportional to text length; narration may not align word-for-word.
 midpoint=start+dur*(len(a.replace('\n',' '))/(len(a)+len(b)))
 captions += [{'start':round(start,3),'end':round(midpoint,3),'text':a,'beat':i+1},{'start':round(midpoint,3),'end':round(end,3),'text':b,'beat':i+1}]
 beats.append({'beat':i+1,'start':round(start,3),'end':round(end,3)})
 chunks.append((round(start*sr),x));cursor=end+.18
frames=int(np.ceil((cursor+.15)*60)); dur=frames/60; n=frames*800
voice=np.zeros(n,np.float32)
for pos,x in chunks: voice[pos:pos+len(x)]+=x
# Same arrangement concept as the user-approved SSS-003 Music Loud, remixed for this voice.
t=np.arange(n,dtype=np.float32)/sr
chords=[(69.30,82.41,103.83),(55.,69.30,82.41),(61.74,77.78,92.50),(51.91,65.41,77.78)]
score=np.zeros((n,2),np.float32)
for j,chord in enumerate(chords):
 env=np.zeros(n,np.float32)
 for k in range(j,int(dur/8)+1,4):
  a=int(k*8*sr);z=min(n,int((k*8+8.6)*sr));q=np.arange(z-a,dtype=np.float32)/sr
  env[a:z]=np.maximum(env[a:z],np.minimum(1,q)*np.minimum(1,(z-a)/sr-q))
 for h,f in enumerate(chord):
  score[:,0] += (.035/(h+1)**.5)*env*np.sin(2*np.pi*f*t+h*.6)
  score[:,1] += (.035/(h+1)**.5)*env*np.sin(2*np.pi*f*1.001*t+h*.6+.2)
pulse=np.maximum(0,np.sin(2*np.pi*.5*t))**12
score[:,0]+=.008*pulse*np.sin(2*np.pi*277.18*t);score[:,1]+=.008*pulse*np.sin(2*np.pi*277.5*t+.8)
notes=[277.18,329.63,415.30,329.63,220.,277.18,329.63,277.18]
step=(t*2).astype(np.int32);freq=np.take(notes,step%len(notes));phase=np.cumsum(freq,dtype=np.float64)*2*np.pi/sr
pluck=np.exp(-4.2*((t*2)%1));score[:,0]+=.018*pluck*np.sin(phase);score[:,1]+=.018*pluck*np.sin(phase+.25)
sfx=np.zeros((n,2),np.float32)
for beat in beats[1:]:
 p=int(beat['start']*sr);a=max(0,p-int(.28*sr));z=min(n,a+int(.55*sr));q=np.arange(z-a,dtype=np.float32)/sr
 hit=.027*np.exp(-q*8)*np.sin(2*np.pi*(72*q-28*q*q));sfx[a:z,0]+=hit;sfx[a:z,1]+=hit*.88
fade=np.minimum(1,t/.8)*np.minimum(1,np.maximum(0,(dur-t)/.5));score*=fade[:,None]
window=int(.12*sr); padded=np.pad(np.abs(voice),(window//2,window-window//2),mode='edge'); c=np.concatenate(([0.0],np.cumsum(padded,dtype=np.float64)));activity=((c[window:]-c[:-window])/window)[:n]
score*=((1-.10*np.clip(activity/.08,0,1))*5.0)[:,None];sfx*=4
mix=np.stack([voice,voice],axis=1)*.78+score+sfx
peak=np.max(np.abs(mix)); scale=min(1,.86/peak);mix*=scale
def write(path,x,ch):
 with wave.open(str(path),'wb') as w: w.setnchannels(ch);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes())
write(work/'master_mix.wav',mix,2);write(work/'voice.wav',voice,1);write(work/'music.wav',score*scale,2);write(work/'sfx.wav',sfx*scale,2)
subprocess.run([ff,'-y','-v','error','-i',str(work/'music.wav'),'-c:a','libmp3lame','-b:a','192k',str(out/'SSS-006_Music_Only.mp3')],check=True)
subprocess.run([ff,'-y','-v','error','-i',str(work/'voice.wav'),'-c:a','libmp3lame','-b:a','192k',str(out/'SSS-006_Voiceover.mp3')],check=True)
def timestamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
srt='\n'.join(f"{i}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}\n" for i,c in enumerate(captions,1));(out/'SSS-006_Captions.srt').write_text(srt);Path(__file__).with_name('captions.srt').write_text(srt)
meta={'total_frames_60fps':frames,'total_duration':round(dur,4),'silence_window':[-1,-1],'beats':beats,'captions':captions};Path(__file__).with_name('timings.json').write_text(json.dumps(meta,indent=2));print('duration',dur,'frames',frames,'peaks',float(peak),'scale',scale,flush=True)
