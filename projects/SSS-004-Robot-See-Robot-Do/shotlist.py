#!/usr/bin/env python3
"""36 time-disjoint shots from the authors' research project page.
Download and prepare the source footage as described in README.md."""
import os
import cv2
FOOTAGE_DIR = "/home/user/agents/.cache/library/footage/rsrd"
SHOTS = [(1, 0, 1.56476, 'clip00.mp4', 0.06, 1, 'THE ROBOT WATCHES', 'REAL RESEARCH • DEMONSTRATION'), (2, 1.56476, 3.12953, 'clip01.mp4', 0.06, 1, 'THE ROBOT WATCHES', 'REAL RESEARCH • DEMONSTRATION'), (3, 3.12953, 4.69429, 'clip02.mp4', 0.06, 1, 'THE ROBOT WATCHES', 'REAL RESEARCH • DEMONSTRATION'), (4, 4.69429, 6.25905, 'clip03.mp4', 0.06, 1, 'THE ROBOT WATCHES', 'REAL RESEARCH • DEMONSTRATION'), (5, 6.25905, 7.82381, 'clip04.mp4', 0.06, 1, 'THE ROBOT WATCHES', 'REAL RESEARCH • DEMONSTRATION'), (6, 7.82381, 9.02381, 'clip05.mp4', 0.06, 2, 'ONE CAMERA • 3D WORLD', 'SINGLE CAMERA • MULTI-VIEW SCAN'), (7, 9.02381, 10.58858, 'clip06.mp4', 0.06, 2, 'ONE CAMERA • 3D WORLD', 'SINGLE CAMERA • MULTI-VIEW SCAN'), (8, 10.58858, 12.15334, 'clip07.mp4', 0.06, 2, 'ONE CAMERA • 3D WORLD', 'SINGLE CAMERA • MULTI-VIEW SCAN'), (9, 12.15334, 13.7181, 'clip08.mp4', 0.06, 2, 'ONE CAMERA • 3D WORLD', 'SINGLE CAMERA • MULTI-VIEW SCAN'), (10, 13.7181, 15.28287, 'clip09.mp4', 0.06, 2, 'ONE CAMERA • 3D WORLD', 'SINGLE CAMERA • MULTI-VIEW SCAN'), (11, 15.28287, 16.84763, 'clip10.mp4', 0.06, 3, 'UC BERKELEY • CoRL', 'ROBOT SEE ROBOT DO • 2024'), (12, 16.84763, 18.41239, 'clip11.mp4', 0.06, 3, 'UC BERKELEY • CoRL', 'ROBOT SEE ROBOT DO • 2024'), (13, 18.41239, 19.97715, 'clip00.mp4', 1.755, 3, 'UC BERKELEY • CoRL', 'ROBOT SEE ROBOT DO • 2024'), (14, 19.97715, 21.54192, 'clip01.mp4', 1.755, 3, 'UC BERKELEY • CoRL', 'ROBOT SEE ROBOT DO • 2024'), (15, 21.54192, 23.10668, 'clip04.mp4', 5.215, 4, 'SCAN + DEMONSTRATION', '4D PART MOTION RECONSTRUCTION'), (16, 23.10668, 24.67144, 'clip04.mp4', 6.93, 4, 'SCAN + DEMONSTRATION', '4D PART MOTION RECONSTRUCTION'), (17, 24.67144, 26.23621, 'clip04.mp4', 1.755, 4, 'SCAN + DEMONSTRATION', '4D PART MOTION RECONSTRUCTION'), (18, 26.23621, 27.80097, 'clip00.mp4', 3.45, 4, 'SCAN + DEMONSTRATION', '4D PART MOTION RECONSTRUCTION'), (19, 27.80097, 29.36573, 'clip00.mp4', 5.144, 5, 'MOTION BECOMES A PLAN', 'ROBOT PLANNING • NEW START POSE'), (20, 29.36573, 30.93049, 'clip04.mp4', 8.644, 5, 'MOTION BECOMES A PLAN', 'ROBOT PLANNING • NEW START POSE'), (21, 30.93049, 32.49526, 'clip04.mp4', 10.359, 5, 'MOTION BECOMES A PLAN', 'ROBOT PLANNING • NEW START POSE'), (22, 32.49526, 34.06002, 'clip09.mp4', 1.755, 5, 'MOTION BECOMES A PLAN', 'ROBOT PLANNING • NEW START POSE'), (23, 34.06002, 35.62478, 'clip10.mp4', 1.755, 6, 'THE HONEST LIMIT', 'SCAN AND VIEWPOINT MATTER'), (24, 35.62478, 37.18955, 'clip11.mp4', 1.755, 6, 'THE HONEST LIMIT', 'SCAN AND VIEWPOINT MATTER'), (25, 37.18955, 38.75431, 'clip01.mp4', 3.45, 6, 'THE HONEST LIMIT', 'SCAN AND VIEWPOINT MATTER'), (26, 38.75431, 40.31907, 'clip04.mp4', 12.074, 6, 'THE HONEST LIMIT', 'SCAN AND VIEWPOINT MATTER'), (27, 40.31907, 41.88383, 'clip04.mp4', 13.789, 6, 'THE HONEST LIMIT', 'SCAN AND VIEWPOINT MATTER'), (28, 41.88383, 43.4486, 'clip04.mp4', 15.503, 6, 'THE HONEST LIMIT', 'SCAN AND VIEWPOINT MATTER'), (29, 43.4486, 45.01336, 'clip04.mp4', 3.45, 7, 'WHAT IS COPIED?', 'HINGED OBJECTS AND A TOY'), (30, 45.01336, 46.57812, 'clip04.mp4', 17.218, 7, 'WHAT IS COPIED?', 'HINGED OBJECTS AND A TOY'), (31, 46.57812, 48.14289, 'clip04.mp4', 18.933, 7, 'WHAT IS COPIED?', 'HINGED OBJECTS AND A TOY'), (32, 48.14289, 49.70765, 'clip04.mp4', 20.648, 8, 'THE OBJECT MOVES', 'FOLLOW FOR THE NEXT DISCOVERY'), (33, 49.70765, 51.27241, 'clip04.mp4', 22.362, 8, 'THE OBJECT MOVES', 'FOLLOW FOR THE NEXT DISCOVERY'), (34, 51.27241, 52.83717, 'clip09.mp4', 3.45, 8, 'THE OBJECT MOVES', 'FOLLOW FOR THE NEXT DISCOVERY'), (35, 52.83717, 54.40194, 'clip10.mp4', 3.45, 8, 'THE OBJECT MOVES', 'FOLLOW FOR THE NEXT DISCOVERY'), (36, 54.40194, 55.9667, 'clip11.mp4', 3.45, 8, 'THE OBJECT MOVES', 'FOLLOW FOR THE NEXT DISCOVERY')]

def validate_shotlist():
    assert len(SHOTS) == 36
    previous=0
    intervals={}
    for idx,start,end,rel,source,beat,title,tag in SHOTS:
        assert abs(start-previous) < .001
        path=os.path.join(FOOTAGE_DIR,rel)
        cap=cv2.VideoCapture(path)
        assert cap.isOpened(), path
        assert int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) >= 1080
        length=cap.get(cv2.CAP_PROP_FRAME_COUNT)/(cap.get(cv2.CAP_PROP_FPS) or 1)
        cap.release()
        assert source+end-start <= length-.03, (idx,rel,length,source,end-start)
        for lo,hi in intervals.get(rel,[]):
            assert min(hi,source+end-start) <= max(lo,source)-.09, (idx,rel)
        intervals.setdefault(rel,[]).append((source,source+end-start))
        previous=end
    print("Validated 36 time-disjoint shots in",len(intervals),"source clips")
