"""
DebugVisualizer — Visual Inspection & Debugging for StyleSense AI.

Saves:
- Person & Garment YOLO Bounding Boxes
- MediaPipe Pose Skeleton
- Garment Masks & Crops
"""

import cv2
import numpy as np
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

DEBUG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "debug")
os.makedirs(DEBUG_DIR, exist_ok=True)

# MediaPipe Pose connections indices
POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16), # Arms
    (11, 23), (12, 24), (23, 24),                   # Torso
    (23, 25), (25, 27), (24, 26), (26, 28),         # Legs
    (27, 29), (29, 31), (28, 30), (30, 32),         # Feet
    (0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6)   # Head
]

class DebugVisualizer:

    @staticmethod
    def save_debug_visuals(
        image_bgr: np.ndarray,
        person_box: dict = None,
        landmarks: dict = None,
        garments: List[dict] = None,
        crops: Dict[str, np.ndarray] = None,
        prefix: str = "analysis"
    ) -> str:
        """
        Draws person boxes, skeleton, garment bounding boxes, and saves cropped regions.
        """
        if image_bgr is None:
            return ""

        try:
            h, w = image_bgr.shape[:2]
            debug_img = image_bgr.copy()

            # 1. Draw Person Bounding Box
            if person_box and person_box.get("detected"):
                px1 = int(person_box.get("x_min", 0) * w)
                py1 = int(person_box.get("y_min", 0) * h)
                px2 = int(person_box.get("x_max", 1) * w)
                py2 = int(person_box.get("y_max", 1) * h)
                conf = person_box.get("confidence", 0.0)
                
                cv2.rectangle(debug_img, (px1, py1), (px2, py2), (0, 255, 0), 2)
                cv2.putText(
                    debug_img, f"Person {conf:.0%}", (px1, max(20, py1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
                )

            # 2. Draw MediaPipe Skeleton
            if landmarks:
                pts = {}
                for idx_str, lm in landmarks.items():
                    try:
                        idx = int(idx_str)
                        lx = int(lm["x"] * w)
                        ly = int(lm["y"] * h)
                        pts[idx] = (lx, ly)
                        vis = lm.get("visibility", 1.0)
                        color = (0, 255, 255) if vis > 0.3 else (0, 0, 180)
                        cv2.circle(debug_img, (lx, ly), 4, color, -1)
                    except Exception:
                        pass

                for p1, p2 in POSE_CONNECTIONS:
                    if p1 in pts and p2 in pts:
                        cv2.line(debug_img, pts[p1], pts[p2], (255, 100, 0), 2)

            # 3. Draw Garment Bounding Boxes
            if garments:
                for idx, g in enumerate(garments):
                    bbox = g.get("bounding_box", {})
                    if bbox and "x_min" in bbox:
                        gx1 = int(bbox["x_min"] * w)
                        gy1 = int(bbox["y_min"] * h)
                        gx2 = int(bbox["x_max"] * w)
                        gy2 = int(bbox["y_max"] * h)
                        
                        item_name = g.get("item", g.get("garment", "Garment"))
                        conf = g.get("confidence", 0.0)
                        color_name = g.get("color", "")
                        
                        cv2.rectangle(debug_img, (gx1, gy1), (gx2, gy2), (255, 0, 128), 2)
                        label = f"{color_name} {item_name} ({conf:.0%})"
                        cv2.putText(
                            debug_img, label, (gx1, max(20, gy1 - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 128), 2
                        )

            # Save full composite debug image
            out_path = os.path.join(DEBUG_DIR, f"{prefix}_full_pipeline.jpg")
            cv2.imwrite(out_path, debug_img)

            # 4. Save individual garment crops
            if crops:
                for region_name, crop_img in crops.items():
                    if crop_img is not None and crop_img.size > 0:
                        crop_path = os.path.join(DEBUG_DIR, f"{prefix}_crop_{region_name}.jpg")
                        cv2.imwrite(crop_path, crop_img)

            logger.info(f"[DebugVisualizer] Saved debug visuals to: {out_path}")
            return out_path
        except Exception as e:
            logger.warning(f"[DebugVisualizer] Error saving debug visuals: {e}")
            return ""
