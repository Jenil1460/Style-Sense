"""
PoseDetector — Multi-Source Pose & Body Visibility Detector for StyleSense AI.

Guarantees:
- Primary: YOLOv8 Pose / YOLO11 Pose (COCO 17 Keypoints)
- Secondary: MediaPipe Pose Landmarker
- Returns:
  - Face Visible
  - Upper Body Visible
  - Lower Body Visible
  - Hands Visible
  - Feet Visible
  - Body Visibility %
  - Pose Landmark Dictionary
"""

import cv2
import numpy as np
import httpx
import logging
import asyncio
import os
import io
import base64
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

_yolo_pose_model = None

COCO_TO_MEDIAPIPE_MAP = {
    0: "0",    # Nose
    1: "2",    # Left eye
    2: "5",    # Right eye
    3: "7",    # Left ear
    4: "8",    # Right ear
    5: "11",   # Left shoulder
    6: "12",   # Right shoulder
    7: "13",   # Left elbow
    8: "14",   # Right elbow
    9: "15",   # Left wrist
    10: "16",  # Right wrist
    11: "23",  # Left hip
    12: "24",  # Right hip
    13: "25",  # Left knee
    14: "26",  # Right knee
    15: "27",  # Left ankle
    16: "28",  # Right ankle
}


from app.services.ml.model_registry import model_registry


def _load_yolo_pose():
    return model_registry.get_yolo_pose()



class PoseDetector:

    @staticmethod
    async def _fetch_bytes(image_url: str) -> bytes:
        if image_url.startswith("data:image"):
            header, base64_data = image_url.split(",", 1)
            return base64.b64decode(base64_data)
        elif os.path.exists(image_url):
            with open(image_url, "rb") as f:
                return f.read()
        else:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(image_url)
                resp.raise_for_status()
                return resp.content

    @staticmethod
    async def detect(image_url: Any, person_box: dict = None) -> dict:
        """
        Detects body pose keypoints and computes body visibility.
        """
        try:
            if hasattr(image_url, "image_bgr"):
                image = image_url.image_bgr
            elif isinstance(image_url, np.ndarray):
                image = image_url
            else:
                raw_bytes = await PoseDetector._fetch_bytes(image_url)
                pil_img = Image.open(io.BytesIO(raw_bytes))
                pil_img = ImageOps.exif_transpose(pil_img).convert("RGB")
                image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

            h, w = image.shape[:2]
            model = _load_yolo_pose()

            landmark_data = {}
            valid_keypoint_count = 0

            if model is not None:
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    None, lambda: model.predict(source=image, conf=0.20, verbose=False)
                )

                if results and len(results[0].keypoints) > 0:
                    kpts = results[0].keypoints[0]
                    xy = kpts.xy[0].cpu().numpy()
                    conf = kpts.conf[0].cpu().numpy() if kpts.conf is not None else np.ones(len(xy))

                    for idx, (pt, c) in enumerate(zip(xy, conf)):
                        x_px, y_px = float(pt[0]), float(pt[1])
                        c_val = float(c)

                        if x_px > 0 and y_px > 0:
                            norm_x = round(x_px / w, 4)
                            norm_y = round(y_px / h, 4)
                            mp_key = COCO_TO_MEDIAPIPE_MAP.get(idx, str(idx))

                            landmark_data[mp_key] = {
                                "x": norm_x,
                                "y": norm_y,
                                "z": 0.0,
                                "visibility": round(c_val, 4),
                            }
                            if c_val >= 0.20 and (-0.05 <= norm_x <= 1.05) and (-0.05 <= norm_y <= 1.05):
                                valid_keypoint_count += 1

            # Helper to check keypoint visibility
            def is_visible(mp_key: str, min_vis: float = 0.20) -> bool:
                if mp_key not in landmark_data:
                    return False
                lm = landmark_data[mp_key]
                return lm["visibility"] >= min_vis and (-0.05 <= lm["x"] <= 1.05) and (-0.05 <= lm["y"] <= 1.05)

            # Evaluate regional visibility
            face_visible = any(is_visible(k, 0.25) for k in ["0", "2", "5", "7", "8"])
            upper_body_visible = is_visible("11", 0.20) or is_visible("12", 0.20)
            hands_visible = is_visible("15", 0.20) or is_visible("16", 0.20)
            hips_visible = is_visible("23", 0.20) or is_visible("24", 0.20)
            knees_visible = is_visible("25", 0.20) or is_visible("26", 0.20)
            ankles_visible = is_visible("27", 0.20) or is_visible("28", 0.20)
            feet_visible = ankles_visible
            lower_body_visible = hips_visible and (knees_visible or ankles_visible)

            visibility_percentage = round((valid_keypoint_count / 17.0) * 100)

            # Framing Classification
            if lower_body_visible and feet_visible:
                framing = "Full body"
            elif lower_body_visible:
                framing = "Three-Quarter"
            elif upper_body_visible:
                framing = "Upper body"
            else:
                framing = "Unknown"

            # Orientation Classification
            if is_visible("11", 0.2) and is_visible("12", 0.2):
                shoulder_width = abs(landmark_data["12"]["x"] - landmark_data["11"]["x"])
                orientation = "Side" if shoulder_width < 0.07 else ("Front" if face_visible else "Back")
            else:
                orientation = "Front" if face_visible else "Unknown"

            avg_conf = round(float(np.mean([lm["visibility"] for lm in landmark_data.values()])) if landmark_data else 0.0, 4)

            logger.info(
                f"[PoseDetector] YOLO Pose: {framing} ({orientation}) | Visibility: {visibility_percentage}% | "
                f"Upper={upper_body_visible}, Lower={lower_body_visible}, Feet={feet_visible}"
            )

            return {
                "pose_type": f"{orientation} - {framing}",
                "orientation": orientation,
                "framing": framing,
                "standing_type": orientation,
                "overall_confidence": avg_conf,
                "body_visibility_percentage": visibility_percentage,
                "body_visibility": {
                    "face_visible": face_visible,
                    "upper_body_visible": upper_body_visible,
                    "lower_body_visible": lower_body_visible,
                    "hands_visible": hands_visible,
                    "feet_visible": feet_visible,
                    "visibility_percentage": visibility_percentage,
                    "evidence": f"YOLO 17-keypoint pose analysis: {visibility_percentage}% keypoints visible.",
                },
                "face_visible": face_visible,
                "upper_body_visible": upper_body_visible,
                "lower_body_visible": lower_body_visible,
                "hands_visible": hands_visible,
                "feet_visible": feet_visible,
                "body_type_estimable": (framing == "Full body" and visibility_percentage >= 75),
                "landmarks": landmark_data,
                "evidence": f"Pose Detector located {valid_keypoint_count} keypoints. Framing: {framing}.",
                "source": "yolo_pose",
            }

        except Exception as e:
            logger.error(f"[PoseDetector] Error during pose detection: {e}", exc_info=True)
            return PoseDetector._unknown(f"Pose detection error: {str(e)}")

    @staticmethod
    def _unknown(reason: str) -> dict:
        return {
            "pose_type": "Unknown",
            "orientation": "Unknown",
            "framing": "Unknown",
            "standing_type": "Unknown",
            "overall_confidence": 0.0,
            "body_visibility_percentage": 0,
            "body_visibility": {
                "face_visible": False,
                "upper_body_visible": False,
                "lower_body_visible": False,
                "hands_visible": False,
                "feet_visible": False,
                "visibility_percentage": 0,
                "evidence": reason,
            },
            "face_visible": False,
            "upper_body_visible": False,
            "lower_body_visible": False,
            "hands_visible": False,
            "feet_visible": False,
            "body_type_estimable": False,
            "source": "yolo_pose",
        }

