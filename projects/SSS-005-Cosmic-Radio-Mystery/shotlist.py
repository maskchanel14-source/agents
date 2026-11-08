#!/usr/bin/env python3
"""Unique illustrated clips and one credited scientific simulation."""
import cv2,os
FOOTAGE_DIR='/home/user/agents/.cache/library/footage/frb'
SHOTS = [(1, 0, 5.21833, 'scene00.mp4', 0.04, 1, 'A SIGNAL FROM SPACE', 'AI ILLUSTRATION • NOT REAL FOOTAGE'), (2, 5.21833, 10.43666, 'scene01.mp4', 0.04, 1, 'A SIGNAL FROM SPACE', 'AI ILLUSTRATION • NOT REAL FOOTAGE'), (3, 10.43666, 15.65499, 'scene02.mp4', 0.04, 2, 'MILLISECOND BURSTS', 'AI ILLUSTRATION • NOT REAL FOOTAGE'), (4, 15.65499, 19.65499, 'simulation_smooth.mp4', 0.04, 3, 'THE RADIO DETECTIVES', 'SIMULATION FRAME • KONIETZKA • CC BY 4.0'), (5, 19.65499, 24.87332, 'scene03.mp4', 0.04, 3, 'THE RADIO DETECTIVES', 'AI ILLUSTRATION • NOT REAL FOOTAGE'), (6, 24.87332, 30.09165, 'scene04.mp4', 0.04, 4, 'A CLUE IN OUR GALAXY', 'AI ILLUSTRATION • NOT REAL FOOTAGE'), (7, 30.09165, 35.30998, 'scene05.mp4', 0.04, 4, 'A CLUE IN OUR GALAXY', 'AI ILLUSTRATION • NOT REAL FOOTAGE'), (8, 35.30998, 40.52831, 'scene06.mp4', 0.04, 5, 'CLOSE TO A DEAD STAR', 'AI ILLUSTRATION • NOT REAL FOOTAGE'), (9, 40.52831, 45.74664, 'scene07.mp4', 0.04, 6, 'THE UNSOLVED QUESTION', 'AI ILLUSTRATION • NOT REAL FOOTAGE'), (10, 45.74664, 50.96497, 'scene08.mp4', 0.04, 7, 'SOME SIGNALS REPEAT', 'AI ILLUSTRATION • NOT REAL FOOTAGE'), (11, 50.96497, 56.1833, 'scene09.mp4', 0.04, 8, 'THE MYSTERY REMAINS', 'AI ILLUSTRATION • NOT REAL FOOTAGE')]

def validate_shotlist():
    assert len(SHOTS)==11 and len({s[3] for s in SHOTS})==11
    prev=0
    for idx,a,b,rel,src,beat,title,tag in SHOTS:
        assert abs(a-prev)<.001
        path=os.path.join(FOOTAGE_DIR,rel);cap=cv2.VideoCapture(path)
        assert cap.isOpened(),path
        width,height=cap.get(3),cap.get(4)
        assert width>=1376 and height>=768
        cap.set(cv2.CAP_PROP_POS_MSEC,(src+b-a-.08)*1000)
        ok,_=cap.read();cap.release();assert ok,(rel,src,b-a)
        prev=b
    print('Validated 11 unique sources, including a credited simulation')
