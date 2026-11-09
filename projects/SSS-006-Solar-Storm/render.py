#!/usr/bin/env python3
"""SSS-006: 1080x1920 documentary with real sourced footage, no vertical crop.
Footage lives under /tmp; see README for sources, rights, and limitations.
"""
import json, math, os, subprocess, time
from pathlib import Path
import cv2, numpy as np, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

cv2.setNumThreads(3)
W,H,FPS=1080,1920,60
ROOT=Path(__file__).parent
OUT=Path('/home/user/deliverables/SSS-006');OUT.mkdir(parents=True,exist_ok=True)
work=Path('/tmp/sss006_build');meta=json.loads((ROOT/'timings.json').read_text()); total=meta['total_frames_60fps']; dur=total/FPS
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; fontreg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
TITLE=ImageFont.truetype(font,50); SMALL=ImageFont.truetype(font,21); CAP=ImageFont.truetype(font,45); MICRO=ImageFont.truetype(fontreg,19)
# Each source is used once, and dates are distinguished from the 1989 event.
shots=[
('/tmp/vesper/catalog/cities/bay-lights/loop.mp4','POWER GRID','CITY FOOTAGE • NOT QUÉBEC 1989'),
('/tmp/solar-movies/sun-24h-171.mp4','THE SUN ERUPTS','NASA/SDO • AIA 171 Å • 2026 TIMELAPSE'),
('/tmp/vesper/catalog/cosmos/earth-limb/loop.mp4','EARTH RESPONDS','NASA • ISS FOOTAGE • ILLUSTRATIVE'),
('/tmp/vesper/catalog/cosmos/lake-aurora/loop.mp4','THE GRID GOES DARK','LAPLAND AURORA • TIMELAPSE • NOT 1989'),
('/tmp/vesper/catalog/cosmos/kjaerfjord/loop.mp4','A WARNING FROM 1859','NORWAY AURORA • NOT 1859'),
('/tmp/helio/all.mp4','WATCHING THE SUN','NASA/SDO • MULTI-YEAR SCIENCE TIMELAPSE'),
('/tmp/solar-movies/sun-24h-304.mp4','RISK IS NOT CERTAINTY','NASA/SDO • AIA 304 Å • 2026 TIMELAPSE'),
('/tmp/vesper/catalog/cosmos/joshua-stars/loop.mp4','LIVING WITH SPACE WEATHER','NATIONAL PARK SERVICE • NIGHT SKY')]

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
 d.text((45,42),'SMALL SIGNAL STUDIO  /  DARK SCIENCE  #006',font=SMALL,fill=(110,198,213,255))
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

# Real frame-based cover: no generated or dramatized depiction of the event.
c=cv2.VideoCapture(shots[0][0]);ok,first=c.read();c.release();assert ok
bg=cv2.resize(first,(W,H));bg=cv2.GaussianBlur(bg,(0,0),55);bg=(bg*.26).astype(np.uint8)
stage=center_stage(first);sy=480+(730-stage.shape[0])//2;sx=(W-stage.shape[1])//2;bg[sy:sy+stage.shape[0],sx:sx+stage.shape[1]]=stage
a=Image.fromarray(cv2.cvtColor(bg,cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(a)
d.text((45,120),'SMALL SIGNAL STUDIO  /  #006',font=SMALL,fill='#81d7e2');d.text((45,260),'THE SUN',font=ImageFont.truetype(font,90),fill='white');d.text((45,375),'BLACKED OUT',font=ImageFont.truetype(font,76),fill='#ffca6a');d.text((45,1280),'THE 1989 QUÉBEC BLACKOUT',font=ImageFont.truetype(font,38),fill='white');d.text((45,1350),'CITY FOOTAGE: ILLUSTRATIVE',font=SMALL,fill='#d7e6e8')
a.save(OUT/'SSS-006_Cover_9x16.jpg',quality=93)
# Thumbnail retains entire source frame, typography layered over the real image.
thumb=cv2.resize(first,(1920,1080));b=Image.fromarray(cv2.cvtColor(thumb,cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(b);d.rectangle((0,650,1920,1080),fill=(5,10,19));d.text((80,720),'THE SUN BLACKED OUT A GRID',font=ImageFont.truetype(font,70),fill='white');d.text((80,840),'THE QUÉBEC SOLAR STORM  /  1989',font=ImageFont.truetype(font,34),fill='#ffca6a');b.save(OUT/'SSS-006_Thumbnail_16x9.png')

ff=imageio_ffmpeg.get_ffmpeg_exe(); out=OUT/'SSS-006_Solar_Storm.mp4'
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
  # Huge defocused full-height extension, not a second cropped source.
  tiny=cv2.resize(frame,(32,57),interpolation=cv2.INTER_AREA);tiny=cv2.GaussianBlur(tiny,(17,17),7)
  bg=cv2.resize(tiny,(W,H),interpolation=cv2.INTER_LINEAR)
  # Smooth vignette/contrast overlay for legible type.
  bg=(bg.astype(np.float32)*.22).astype(np.uint8)
  stage=center_stage(frame);sh,sw=stage.shape[:2];x=(W-sw)//2;y=440+(960-sh)//2
  # A subtle subpixel push, scaled INSIDE original stage, no vertical crop.
  progress=min(1,(t-meta['beats'][shot]['start'])/max(1,meta['beats'][shot]['end']-meta['beats'][shot]['start']));ease=progress*progress*(3-2*progress)
  z=1+.015*ease; M=np.float32([[z,0,sw*(1-z)*.5],[0,z,sh*(1-z)*.5]])
  stage=cv2.warpAffine(stage,M,(sw,sh),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
  bg[y:y+sh,x:x+sw]=stage
  cv2.rectangle(bg,(x-2,y-2),(x+sw+1,y+sh+1),(92,124,140),2)
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
