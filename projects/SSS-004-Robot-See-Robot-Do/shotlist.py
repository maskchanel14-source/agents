#!/usr/bin/env python3
"""Unique source clips and explanatory graphics for the SSS-004 revision."""
import os
import cv2
FOOTAGE_DIR = "/home/user/agents/.cache/library/footage/rsrd"
SHOTS = [(1, 0, 2.42576, 'clip00.mp4', 0.04, 1, 'THE ROBOT WATCHES', 'RESEARCH DEMONSTRATION • UC BERKELEY'), (2, 2.42576, 4.85152, 'cinematic00.mp4', 0.04, 1, 'THE ROBOT WATCHES', 'AI ILLUSTRATION • NOT RESEARCH FOOTAGE'), (3, 4.85152, 6.10152, 'clip05.mp4', 0.04, 1, 'THE ROBOT WATCHES', 'RESEARCH DEMONSTRATION • UC BERKELEY'), (4, 6.10152, 8.52728, 'cinematic01.mp4', 0.04, 1, 'THE ROBOT WATCHES', 'AI ILLUSTRATION • NOT RESEARCH FOOTAGE'), (5, 8.52728, 10.95304, 'clip12.mp4', 0.04, 2, 'ONE CAMERA • 3D WORLD', 'RESEARCH SIMULATION • UC BERKELEY'), (6, 10.95304, 13.3788, 'cinematic02.mp4', 0.04, 2, 'ONE CAMERA • 3D WORLD', 'AI ILLUSTRATION • NOT RESEARCH FOOTAGE'), (7, 13.3788, 15.80455, 'clip06.mp4', 0.04, 2, 'ONE CAMERA • 3D WORLD', 'RESEARCH DEMONSTRATION • UC BERKELEY'), (8, 15.80455, 18.23031, 'clip08.mp4', 0.04, 3, 'UC BERKELEY • CORL', 'RESEARCH DEMONSTRATION • UC BERKELEY'), (9, 18.23031, 20.65607, 'cinematic03.mp4', 0.04, 3, 'UC BERKELEY • CORL', 'AI ILLUSTRATION • NOT RESEARCH FOOTAGE'), (10, 20.65607, 23.08183, 'clip14.mp4', 0.04, 4, 'SCAN + DEMONSTRATION', 'RESEARCH SIMULATION • UC BERKELEY'), (11, 23.08183, 25.50759, 'cinematic04.mp4', 0.04, 4, 'SCAN + DEMONSTRATION', 'AI ILLUSTRATION • NOT RESEARCH FOOTAGE'), (12, 25.50759, 27.93335, 'clip15.mp4', 0.04, 4, 'SCAN + DEMONSTRATION', 'RESEARCH SIMULATION • UC BERKELEY'), (13, 27.93335, 30.35911, 'cinematic09.mp4', 0.04, 5, 'MOTION BECOMES A PLAN', 'AI ILLUSTRATION • NOT RESEARCH FOOTAGE'), (14, 30.35911, 31.70911, 'clip02.mp4', 0.04, 5, 'MOTION BECOMES A PLAN', 'RESEARCH DEMONSTRATION • UC BERKELEY'), (15, 31.70911, 34.13487, 'cinematic05.mp4', 0.04, 5, 'MOTION BECOMES A PLAN', 'AI ILLUSTRATION • NOT RESEARCH FOOTAGE'), (16, 34.13487, 38.98639, 'clip09.mp4', 0.04, 6, 'THE HONEST LIMIT', 'RESEARCH DEMONSTRATION • UC BERKELEY'), (17, 38.98639, 41.41215, 'clip17.mp4', 0.04, 6, 'THE HONEST LIMIT', 'RESEARCH SIMULATION • UC BERKELEY'), (18, 41.41215, 43.8379, 'cinematic06.mp4', 0.04, 6, 'THE HONEST LIMIT', 'AI ILLUSTRATION • NOT RESEARCH FOOTAGE'), (19, 43.8379, 46.26366, 'clip11.mp4', 0.04, 7, 'WHAT IS COPIED?', 'RESEARCH DEMONSTRATION • UC BERKELEY'), (20, 46.26366, 48.68942, 'clip16.mp4', 0.04, 7, 'WHAT IS COPIED?', 'RESEARCH SIMULATION • UC BERKELEY'), (21, 48.68942, 53.54094, 'cinematic07.mp4', 0.04, 8, 'THE OBJECT MOVES', 'AI ILLUSTRATION • NOT RESEARCH FOOTAGE'), (22, 53.54094, 55.9667, 'cinematic08.mp4', 0.04, 8, 'THE OBJECT MOVES', 'AI ILLUSTRATION • NOT RESEARCH FOOTAGE')]

def validate_shotlist():
    assert len(SHOTS) == 22
    assert len({s[3] for s in SHOTS}) == len(SHOTS), "A source clip is reused"
    previous=0
    for idx,start,end,rel,source,beat,title,tag in SHOTS:
        assert abs(start-previous) < .001
        path=os.path.join(FOOTAGE_DIR,rel)
        cap=cv2.VideoCapture(path)
        assert cap.isOpened(), path
        height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        assert height >= (768 if rel.startswith("cinematic") else 1080)
        fps=cap.get(cv2.CAP_PROP_FPS) or 1
        cap.set(cv2.CAP_PROP_POS_MSEC, (source+end-start-.05)*1000)
        ok,_=cap.read()
        cap.release()
        assert ok, (idx,rel,source,end-start)
        previous=end
    print("Validated",len(SHOTS),"distinct source clips/graphics")
