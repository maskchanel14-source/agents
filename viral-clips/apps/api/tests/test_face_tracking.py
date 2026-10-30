"""Face detection + crop planning on real imagery (vendored cascade)."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.services.media.crop import crop_window, plan_clip_crop
from app.services.media.faces import _cascade

FACE_IMAGE = Path(__file__).parent / "fixtures" / "face.jpg"


def test_vendored_cascade_is_loaded():
    cascade = _cascade()
    assert cascade is not None, "haarcascade model missing from apps/api/vendor/models"


@pytest.mark.skipif(not FACE_IMAGE.exists(), reason="face fixture image not present")
def test_detects_a_real_face_and_centres_the_crop():
    import cv2

    cascade = _cascade()
    img = cv2.imread(str(FACE_IMAGE))
    assert img is not None
    gray = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    boxes = cascade.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=5, minSize=(28, 28))
    assert len(boxes) >= 1, "expected the frontal-face cascade to find the portrait"

    h, w = img.shape[:2]
    x, y, bw, bh = boxes[0]
    face_centre = (x + bw / 2) / w
    visuals = {
        "available": True,
        "samples": [
            {"t": i * 0.5, "face_x": float(face_centre), "motion": 0.02, "face_count": 1}
            for i in range(40)
        ],
    }
    plan = plan_clip_crop(visuals, 0.0, 20.0)
    assert plan["strategy"] == "face_tracking"
    assert abs(plan["crop_x"] - face_centre) < 0.35

    win = crop_window(1920, 1080, plan["crop_x"])
    assert win["mode"] == "crop_h"
    assert abs(win["w"] / win["h"] - 9 / 16) < 0.01
    # the face must stay inside the crop window
    face_px = face_centre * 1920
    assert win["x"] <= face_px <= win["x"] + win["w"]


def test_plan_falls_back_to_centre_without_faces():
    visuals = {"available": True, "samples": [{"t": i, "face_x": None, "motion": 0.0} for i in range(10)]}
    plan = plan_clip_crop(visuals, 0, 10)
    assert plan["strategy"] == "center"
    assert plan["crop_x"] == 0.5
