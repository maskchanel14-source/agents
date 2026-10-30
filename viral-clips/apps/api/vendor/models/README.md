# Vendored models

| File | Source | Licence | Why vendored |
|---|---|---|---|
| `haarcascade_frontalface_default.xml` | [opencv/opencv `data/haarcascades`](https://github.com/opencv/opencv/tree/4.x/data/haarcascades) | Apache-2.0 (© OpenCV Foundation) | Offline frontal-face detection for speaker-aware 9:16 cropping. The `opencv-python-headless` wheel ships an empty `cv2/data` directory, and downloading a model at runtime would break air-gapped workers |

It is a 930 KB AdaBoost cascade run through `cv2.CascadeClassifier`. Faces are sampled at 0.5 fps on
480-px-wide frames (see `app/services/media/faces.py`), so detection cost is negligible relative to decode.

To replace it (e.g. with a DNN/MediaPipe detector), swap `_cascade()` and keep the
`{"t", "face_x", "face_count", "motion", "brightness"}` sample contract — the crop planner and all tests
stay unchanged.
