"""Smart 9:16 crop planning from face/subject positions."""
from __future__ import annotations

TARGET_W, TARGET_H = 1080, 1920
ASPECT = TARGET_W / TARGET_H  # 0.5625


def crop_window(src_w: int, src_h: int, center_x: float | None = None) -> dict:
    """Compute a 9:16 crop rectangle. center_x is a 0..1 normalised x."""
    if src_w <= 0 or src_h <= 0:
        return {"x": 0, "y": 0, "w": TARGET_W, "h": TARGET_H, "mode": "scale"}
    ratio = src_w / src_h
    if abs(ratio - ASPECT) < 0.03:
        return {"x": 0, "y": 0, "w": src_w, "h": src_h, "mode": "exact"}
    if ratio > ASPECT:  # wider than 9:16 -> crop horizontally
        w = int(round(src_h * ASPECT)) // 2 * 2
        h = src_h
        cx = (center_x if center_x is not None else 0.5) * src_w
        x = int(round(cx - w / 2))
        x = max(0, min(src_w - w, x))
        return {"x": x, "y": 0, "w": w, "h": h, "mode": "crop_h"}
    # taller than 9:16 -> crop vertically (rare)
    h = int(round(src_w / ASPECT)) // 2 * 2
    w = src_w
    y = max(0, (src_h - h) // 2)
    return {"x": 0, "y": y, "w": w, "h": h, "mode": "crop_v"}


def plan_clip_crop(
    visuals: dict | None,
    start_s: float,
    end_s: float,
    *,
    fallback_x: float = 0.5,
    smoothing: float = 0.55,
) -> dict:
    """Pick the crop centre for a clip from the sampled visual timeline.

    Blends face positions (weighted) with motion-weighted saliency so a clip
    with occasional faces doesn't snap around. Returns crop_x plus confidence.
    """
    if not visuals or not visuals.get("available"):
        return {"crop_x": fallback_x, "confidence": 0.0, "strategy": "center"}

    samples = [s for s in visuals.get("samples", []) if start_s <= s["t"] <= end_s]
    if not samples:
        return {"crop_x": fallback_x, "confidence": 0.0, "strategy": "center"}

    face_vals = [(s["t"], s["face_x"]) for s in samples if s.get("face_x") is not None]
    if face_vals:
        xs = [v for _, v in face_vals]
        # trim 10% outliers for stability
        xs_sorted = sorted(xs)
        keep = xs_sorted[max(0, int(len(xs) * 0.1)) : max(1, int(len(xs) * 0.9))] or xs_sorted
        centre = sum(keep) / len(keep)
        centre = fallback_x + (centre - fallback_x) * smoothing
        return {
            "crop_x": round(min(0.95, max(0.05, centre)), 4),
            "confidence": round(len(face_vals) / len(samples), 3),
            "strategy": "face_tracking",
        }

    # No faces: centre the frame on the busiest region (motion-weighted).
    top = sorted(samples, key=lambda s: s.get("motion", 0), reverse=True)[: max(1, len(samples) // 4)]
    if top and max(s.get("motion", 0) for s in top) > 0.02:
        return {"crop_x": 0.5, "confidence": 0.2, "strategy": "motion_center"}
    return {"crop_x": fallback_x, "confidence": 0.05, "strategy": "center"}
