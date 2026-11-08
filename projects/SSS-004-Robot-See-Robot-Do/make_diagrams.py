#!/usr/bin/env python3
"""Generate distinct explanatory graphics (not experimental footage)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, imageio_ffmpeg
root=Path('/home/user/agents/.cache/library/footage/rsrd');root.mkdir(parents=True,exist_ok=True)
ff=imageio_ffmpeg.get_ffmpeg_exe()
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
mono='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
B=ImageFont.truetype(font,68); M=ImageFont.truetype(mono,34); S=ImageFont.truetype(mono,27)
items=[('ONE CAMERA','FLAT FRAMES  →  3D QUESTIONS'),('HIDDEN SURFACES','OCCLUSION LIMITS THE VIEW'),('OBJECT SCAN','MULTIPLE VIEWS BUILD A 3D MODEL'),('PART SEGMENTATION','IDENTIFY THE MOVING PARTS'),('4D RECONSTRUCTION','3D OBJECT + MOTION OVER TIME'),('TRAJECTORY','OBJECT MOTION → ROBOT PLAN'),('THE FAILURE POINTS','SCAN QUALITY  •  OCCLUSION  •  VIEWPOINT'),('OBJECT-CENTRIC','COPY THE OBJECT MOTION, NOT THE HAND'),('NEXT DISCOVERY','DARK SCIENCE ARCHIVE  •  #004'),('RECONSTRUCTION','GEOMETRY  +  TIME'),('ROBOT PLANNING','MOVE THE OBJECT PARTS'),('RESEARCH LIMIT','NOT A UNIVERSAL SKILL')]
for i,(title,sub) in enumerate(items):
 im=Image.new('RGB',(1920,1080),(7,13,23));d=ImageDraw.Draw(im)
 for x in range(80,1920,90):d.line((x,0,x,1080),fill=(14,28,38),width=1)
 for y in range(0,1080,90):d.line((0,y,1920,y),fill=(14,28,38),width=1)
 d.rounded_rectangle((45,45,1875,1035),radius=24,outline=(151,124,75),width=4)
 d.text((90,90),'S M A L L   S I G N A L   S T U D I O',font=S,fill=(107,199,213))
 d.text((90,185),title,font=B,fill=(249,215,113));d.text((90,285),sub,font=M,fill=(205,220,229))
 cyan=(73,208,226); gold=(223,178,95); red=(238,93,99)
 # Varied conceptual compositions; all symbols are explanatory graphics.
 if i==0:
  d.rounded_rectangle((190,450,650,800),radius=30,outline=cyan,width=9);d.ellipse((315,515,520,720),outline=gold,width=12);d.polygon([(650,520),(1100,395),(1100,860),(650,730)],outline=cyan,width=6);d.rounded_rectangle((1300,480,1660,800),radius=25,outline=gold,width=7);d.text((1320,845),'SCENE',font=M,fill=gold)
 elif i==1:
  d.ellipse((440,430,950,900),outline=cyan,width=7);d.rectangle((650,420,1080,900),fill=(20,35,46),outline=red,width=7);d.text((710,600),'?',font=B,fill=red);d.line((150,665,440,665),fill=gold,width=9)
 elif i==2:
  d.rounded_rectangle((760,420,1140,800),radius=35,outline=cyan,width=8)
  for x,y in [(450,460),(1450,460),(450,820),(1450,820)]:
   d.ellipse((x-40,y-40,x+40,y+40),outline=gold,width=7);d.line((x,y,950,610),fill=(70,116,130),width=4)
 elif i==3:
  for k,(x,y) in enumerate([(400,470),(730,470),(1060,470),(1390,470)]):
   d.rounded_rectangle((x,y,x+210,y+270),radius=30,outline=cyan if k%2 else gold,width=8);d.text((x+70,y+100),str(k+1),font=B,fill=cyan if k%2 else gold)
 elif i==4:
  for k in range(4):
   x=230+k*390; d.rounded_rectangle((x,450,x+260,760),radius=30,outline=cyan if k%2 else gold,width=7);d.line((x+60,670,x+200,520),fill=cyan,width=9);d.text((x+90,810),f'T{k+1}',font=M,fill=gold)
 elif i==5:
  for k,(x,y) in enumerate([(350,700),(700,520),(1100,720),(1500,470)]):
   d.ellipse((x-45,y-45,x+45,y+45),fill=cyan);d.text((x-15,y+70),str(k+1),font=M,fill=gold)
  d.line([(350,700),(700,520),(1100,720),(1500,470)],fill=gold,width=8)
 elif i==6:
  for k,label in enumerate(['BAD SCAN','OCCLUSION','ANGLE']):
   x=170+k*570;d.rounded_rectangle((x,450,x+480,780),radius=30,outline=red,width=6);d.text((x+40,540),'!',font=B,fill=red);d.text((x+40,690),label,font=M,fill=(230,230,230))
 elif i==7:
  d.rounded_rectangle((250,440,790,790),radius=30,outline=cyan,width=7);d.text((315,580),'OBJECT',font=B,fill=cyan);d.line((840,620,1080,620),fill=gold,width=10);d.polygon([(1080,580),(1160,620),(1080,660)],fill=gold);d.rounded_rectangle((1200,440,1700,790),radius=30,outline=gold,width=7);d.text((1260,580),'MOTION',font=B,fill=gold)
 else:
  d.rounded_rectangle((370,410,1550,930),radius=45,outline=gold,width=8);d.text((560,575),['#004','3D + TIME','PLAN + MOVE','TEST THE LIMIT'][i-8],font=B,fill=cyan);d.text((545,965),'FOLLOW THE NEXT DISCOVERY',font=S,fill=gold)
 d.text((92,982),'EXPLANATORY GRAPHIC  •  NOT EXPERIMENTAL FOOTAGE',font=S,fill=(121,149,160))
 png=root/f'diagram{i:02}.png';mp4=root/f'diagram{i:02}.mp4';im.save(png)
 subprocess.run([ff,'-y','-v','error','-loop','1','-i',str(png),'-t','3','-vf',"zoompan=z='min(zoom+0.00025,1.025)':d=1:s=1920x1080:fps=30,format=yuv420p",'-an','-c:v','libx264','-preset','ultrafast','-crf','20','-threads','3',str(mp4)],check=True)
 print('created',mp4,flush=True)
