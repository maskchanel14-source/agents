#!/usr/bin/env python3
"""SSS-007: full-screen portrait reframe of real sourced footage.
Footage lives under /tmp; see README for sources, rights, and limitations.
"""
import json, math, os, subprocess, time
from pathlib import Path
import cv2, numpy as np, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

cv2.setNumThreads(3)
W,H,FPS=1080,1920,60
ROOT=Path(__file__).parent
OUT=Path('/home/user/deliverables/SSS-007');OUT.mkdir(parents=True,exist_ok=True)
work=Path('/tmp/sss007_build');meta=json.loads((ROOT/'timings.json').read_text()); total=meta['total_frames_60fps']; dur=total/FPS
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; fontreg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
TITLE=ImageFont.truetype(font,50); SMALL=ImageFont.truetype(font,21); CAP=ImageFont.truetype(font,45); MICRO=ImageFont.truetype(fontreg,19)
# Each source is used once, and dates are distinguished from the 1989 event.
shots=[
('/tmp/sss007_build/eht.mp4','NOT THE BLACK HOLE','EHT COLLABORATION • 2017 RADIO IMAGE'),
('/tmp/sss007_build/eht2018.mp4','A SHADOW','EHT COLLABORATION • 2018 RADIO IMAGE'),
('/tmp/vesper/catalog/cosmos/orion/loop.mp4','55 MILLION LIGHT-YEARS','ORION NEBULA • VISUALIZATION • ILLUSTRATIVE'),
('/tmp/sss007_build/eht.mp4','6.5 BILLION SUNS','EHT COLLABORATION • 2017 RADIO IMAGE'),
('/tmp/vesper/catalog/cosmos/earth-limb/loop.mp4','AN EARTH-SIZED TELESCOPE','NASA • EARTH FROM ISS • ILLUSTRATIVE'),
('/tmp/vesper/catalog/cosmos/joshua-stars/loop.mp4','RECONSTRUCTED FROM DATA','NPS • NIGHT SKY • ILLUSTRATIVE'),
('/tmp/vesper/catalog/cosmos/pillars/loop.mp4','THE EVENT HORIZON','ESO • NEBULA VISUALIZATION • ILLUSTRATIVE'),
('/tmp/sss007_build/eht2018.mp4','WE SEE ITS SHADOW','EHT COLLABORATION • 2018 RADIO IMAGE')]


# Source uses one distinct file for each beat; 60fps container does not claim
# the 24fps footage or 6fps scientific data have been temporally interpolated.
for p,_,_ in shots:
 if not Path(p).is_file():raise FileNotFoundError(p)

# Subdivide captions to small readable chunks; alignment is proportional, not forced.
segments=[]
for cap in meta['captions']:
 words=cap['text'].replace('\n',' ').split(); chunks=[]
 while words: chunks.append(words[:5]);words=words[5:]
 total_letters=sum(len(' '.join(c)) for c in chunks); cursor=cap['start']
 for ix,c in enumerate(chunks):
  end=cap['end'] if ix==len(chunks)-1 else cursor+(cap['end']-cap['start'])*len(' '.join(c))/total_letters
  segments.append((cursor,end,' '.join(c)));cursor=end

def fit_text(draw,text,font,maxwidth):
 words=text.split(); lines=[];line=''
 for word in words:
  trial=(line+' '+word).strip()
  if line and draw.textlength(trial,font=font)>maxwidth:lines.append(line);line=word
  else:line=trial
 if line:lines.append(line)
 return lines

def caption_image(text, highlight):
 im=Image.new('RGBA',(W,260),(0,0,0,0));d=ImageDraw.Draw(im)
 lines=fit_text(d,text,CAP,900); height=len(lines)*65+40; y=10
 d.rounded_rectangle((35,y,1045,y+height),radius=20,fill=(5,11,21,230),outline=(76,100,118,210),width=2)
 count=0
 for ln in lines:
  ww=ln.split();width=d.textlength(ln,font=CAP);x=(W-width)/2; yy=y+20+count*65;count+=1
  for word in ww:
   ix=sum(len(v.split()) for v in lines[:count-1])+ww.index(word) # approximate word highlight
   fill=(255,205,92,255) if ix==highlight else (249,251,255,255)
   d.text((x,yy),word,font=CAP,fill=fill,stroke_width=0);x+=d.textlength(word+' ',font=CAP)
 return np.array(im)

def header(title,tag):
 im=Image.new('RGBA',(W,360),(0,0,0,0));d=ImageDraw.Draw(im)
 d.text((45,42),'SMALL SIGNAL STUDIO  /  DARK SCIENCE  #007',font=SMALL,fill=(110,198,213,255))
 d.line((45,88,1035,88),fill=(84,138,151,180),width=2)
 d.text((45,115),title,font=TITLE,fill=(250,248,242,255),stroke_width=1,stroke_fill=(0,0,0,120))
 d.text((46,210),tag,font=SMALL,fill=(231,224,205,255))
 return np.array(im)

def over(dst,rgba,x=0,y=0):
 h,w=rgba.shape[:2];roi=dst[y:y+h,x:x+w]; a=rgba[:,:,3:4].astype(np.float32)/255
 # PIL RGBA -> OpenCV BGR
 roi[:]=(rgba[:,:,:3][:,:,::-1].astype(np.float32)*a+roi.astype(np.float32)*(1-a)).astype(np.uint8)

def center_stage(raw):
 rh,rw=raw.shape[:2];scale=min(1036/rw,960/rh,1.0)
 nw,nh=int(rw*scale)//2*2,int(rh*scale)//2*2
 return cv2.resize(raw,(nw,nh),interpolation=cv2.INTER_AREA)

def source_frame(cap,index):
 fps=cap.get(cv2.CAP_PROP_FPS) or 24
 # Source frames sampled at their native cadence; no fabricated interpolation.
 target=min(int(index*fps/FPS),int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1)
 current=int(cap.get(cv2.CAP_PROP_POS_FRAMES))
 while current<=target:
  ok,frame=cap.read()
  if not ok:raise RuntimeError('source decode ended')
  current+=1
 return frame

ff=imageio_ffmpeg.get_ffmpeg_exe(); out=OUT/'SSS-007_Black_Hole_Shadow.mp4'
cmd=[ff,'-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(work/'master_mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','veryfast','-threads','4','-crf','18','-pix_fmt','yuv420p','-g','60','-c:a','aac','-b:a','256k','-movflags','+faststart','-shortest',str(out)]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
headers=[header(t,tag) for _,t,tag in shots];cache={}
shot_index=-1;cap=None;frame=None;start_index=0;wall=time.time()
try:
 for f in range(total):
  t=f/FPS
  shot=next((i for i,beat in enumerate(meta['beats']) if t<beat['end']+.18),len(shots)-1)
  if shot!=shot_index:
   if cap:cap.release()
   shot_index=shot;start_index=f;cap=cv2.VideoCapture(shots[shot][0]);frame=None
   if not cap.isOpened():raise RuntimeError(shots[shot][0])
  # Use sequential decode and cache frames for 60fps output.
  fps=cap.get(cv2.CAP_PROP_FPS) or 24;target=int((f-start_index)*fps/FPS)
  pos=int(cap.get(cv2.CAP_PROP_POS_FRAMES));maxframe=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
  target=min(target,maxframe-1)
  while pos<=target:
   ok,frame=cap.read()
   if not ok:raise RuntimeError(f'failed {shots[shot][0]} at {pos}')
   pos+=1
  # Fill portrait canvas with footage, preserving aspect ratio. Landscape
  # sources necessarily lose their left/right edges; no background padding.
  rh,rw=frame.shape[:2]
  scale=max(W/rw,H/rh)
  sw,sh=round(rw*scale),round(rh*scale)
  resized=cv2.resize(frame,(sw,sh),interpolation=cv2.INTER_LINEAR)
  x=(sw-W)//2;y=(sh-H)//2
  bg=resized[y:y+H,x:x+W].copy()
  over(bg,headers[shot],0,0)
  for idx,(a,b,txt) in enumerate(segments):
   if a<=t<=b:
    n=len(txt.split());hi=min(n-1,max(0,int((t-a)/max(.001,b-a)*n)));key=(idx,hi)
    if key not in cache:cache[key]=caption_image(txt,hi)
    over(bg,cache[key],0,1485);break
  proc.stdin.write(bg.tobytes())
  if f%600==0:print('render',f,'/',total,round(time.time()-wall,1),flush=True)
 cap.release();proc.stdin.close();rc=proc.wait()
 if rc:raise RuntimeError(f'ffmpeg failed {rc}')
except BaseException:
 proc.kill();proc.wait();raise
print('DONE',out,flush=True)
