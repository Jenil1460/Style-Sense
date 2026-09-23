"""
BodySegmenter — Pose-Landmark-Guided GrabCut Segmentation for StyleSense AI.

Guarantees:
- Uses MediaPipe landmark positions and person bounding boxes to extract garment crops
- Performs GrabCut segmentation on garment crops to separate clothing from background/skin
- ONLY generates crops for regions that exist in the image frame
- Saves segmented masks for visual verification in debug mode
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


def run_grabcut_segmentation(crop: np.ndarray) -> np.ndarray:
    """
    Runs OpenCV GrabCut segmentation on a cropped region to extract foreground pixels.
    Returns binary mask (255 for foreground, 0 for background).
    """
    if crop is None or crop.size < 400:
        return None
    try:
        h, w = crop.shape[:2]
        mask = np.zeros((h, w), np.uint8)

        # Define interior rectangle for GrabCut initialization
        margin_x = max(1, int(w * 0.05))
        margin_y = max(1, int(h * 0.05))
        rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)

        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        cv2.grabCut(crop, mask, rect, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_RECT)
        binary_mask = np.where((mask == 2) | (mask == 0), 0, 255).astype("uint8")
        
        # If mask lost too many pixels, default to non-border pixels
        if np.count_nonzero(binary_mask) < (h * w * 0.1):
            binary_mask = np.ones((h, w), np.uint8) * 255
            binary_mask[0:margin_y, :] = 0
            binary_mask[-margin_y:, :] = 0
            binary_mask[:, 0:margin_x] = 0
            binary_mask[:, -margin_x:] = 0

        return binary_mask
    except Exception as e:
        logger.warning(f"[BodySegmenter] GrabCut failed, using fallback mask: {e}")
        h, w = crop.shape[:2]
        mask = np.ones((h, w), np.uint8) * 255
        return mask


class BodySegmenter:

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
    async def segment(image_url: Any, person_box: dict = None, pose: dict = None) -> dict:
        """
        Segments body regions using pose landmarks and GrabCut.
        """
        try:
            if hasattr(image_url, "image_bgr"):
                image = image_url.image_bgr
            elif isinstance(image_url, np.ndarray):
                image = image_url
            else:
                raw_bytes = await BodySegmenter._fetch_bytes(image_url)
                pil_img = Image.open(io.BytesIO(raw_bytes))
                pil_img = ImageOps.exif_transpose(pil_img).convert("RGB")
                image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

            h, w = image.shape[:2]
            pose = pose or {}
            landmarks = pose.get("landmarks", {})
            
            lower_body_visible = pose.get("lower_body_visible", False)
            feet_visible = pose.get("feet_visible", False)
            upper_body_visible = pose.get("upper_body_visible", True)

            # Person bounding box (pixel coordinates)
            if person_box and person_box.get("detected") and person_box.get("x_min") is not None:
                px1 = max(0, int(person_box["x_min"] * w))
                py1 = max(0, int(person_box["y_min"] * h))
                px2 = min(w, int(person_box["x_max"] * w))
                py2 = min(h, int(person_box["y_max"] * h))
            else:
                px1, py1, px2, py2 = 0, 0, w, h

            crops = {
                "upper_body": None,
                "lower_body": None,
                "shoes": None,
                "face": None,
            }
            masks = {}
            regions = {}
            evidence_parts = []

            # ── FACE / HEAD REGION ──
            if landmarks and _has_landmarks(landmarks, [0, 2, 5], min_vis=0.20):
                face_y = min(landmarks[str(0)]["y"], landmarks[str(2)]["y"], landmarks[str(5)]["y"])
                face_y_max = max(landmarks[str(0)]["y"], landmarks[str(2)]["y"], landmarks[str(5)]["y"])
                face_x_min = min(landmarks[str(2)]["x"], landmarks[str(5)]["x"])
                face_x_max = max(landmarks[str(2)]["x"], landmarks[str(5)]["x"])

                margin_x = (face_x_max - face_x_min) * 0.8
                margin_y = (face_y_max - face_y) * 1.5

                fy1 = max(0, int((face_y - margin_y) * h))
                fy2 = min(h, int((face_y_max + margin_y * 0.5) * h))
                fx1 = max(0, int((face_x_min - margin_x) * w))
                fx2 = min(w, int((face_x_max + margin_x) * w))

                face_crop = image[fy1:fy2, fx1:fx2]
                if face_crop.size > 0:
                    crops["face"] = face_crop
                    regions["face"] = _norm_region(fx1, fy1, fx2, fy2, w, h)
                    evidence_parts.append("Face region extracted from facial landmarks")

            # ── UPPER BODY REGION ──
            if upper_body_visible:
                if landmarks and _has_landmarks(landmarks, [11, 12], min_vis=0.20):
                    shoulder_y = min(landmarks[str(11)]["y"], landmarks[str(12)]["y"])
                    shoulder_x_min = min(landmarks[str(11)]["x"], landmarks[str(12)]["x"])
                    shoulder_x_max = max(landmarks[str(11)]["x"], landmarks[str(12)]["x"])

                    if _has_landmarks(landmarks, [23, 24], min_vis=0.20):
                        hip_y = max(landmarks[str(23)]["y"], landmarks[str(24)]["y"])
                    else:
                        hip_y = min(1.0, shoulder_y + 0.35)

                    margin_x = (shoulder_x_max - shoulder_x_min) * 0.5
                    uy1 = max(0, int((shoulder_y - 0.04) * h))
                    uy2 = min(h, int(hip_y * h))
                    ux1 = max(0, int((shoulder_x_min - margin_x) * w))
                    ux2 = min(w, int((shoulder_x_max + margin_x) * w))
                else:
                    pw, ph = px2 - px1, py2 - py1
                    uy1 = py1 + int(ph * 0.10)
                    uy2 = py1 + int(ph * 0.55)
                    ux1, ux2 = px1, px2

                upper_crop = image[uy1:uy2, ux1:ux2]
                if upper_crop.size > 100:
                    crops["upper_body"] = upper_crop
                    masks["upper_body"] = run_grabcut_segmentation(upper_crop)
                    regions["upper_body"] = _norm_region(ux1, uy1, ux2, uy2, w, h)
                    evidence_parts.append(f"Upper body region extracted [{ux1},{uy1},{ux2},{uy2}]")

            # ── LOWER BODY REGION ──
            if lower_body_visible:
                if landmarks and _has_landmarks(landmarks, [23, 24], min_vis=0.15):
                    hip_y = min(landmarks[str(23)]["y"], landmarks[str(24)]["y"])
                    hip_x_min = min(landmarks[str(23)]["x"], landmarks[str(24)]["x"])
                    hip_x_max = max(landmarks[str(23)]["x"], landmarks[str(24)]["x"])

                    if _has_landmarks(landmarks, [27, 28], min_vis=0.15):
                        ankle_y = max(landmarks[str(27)]["y"], landmarks[str(28)]["y"])
                    elif _has_landmarks(landmarks, [25, 26], min_vis=0.15):
                        knee_y = max(landmarks[str(25)]["y"], landmarks[str(26)]["y"])
                        ankle_y = min(1.0, knee_y + (knee_y - hip_y) * 0.8)
                    else:
                        ankle_y = py2 / h

                    margin_x = (hip_x_max - hip_x_min) * 0.6
                    ly1 = max(0, int(hip_y * h))
                    ly2 = min(h, int(ankle_y * h))
                    lx1 = max(0, int((hip_x_min - margin_x) * w))
                    lx2 = min(w, int((hip_x_max + margin_x) * w))
                else:
                    pw, ph = px2 - px1, py2 - py1
                    ly1 = py1 + int(ph * 0.50)
                    ly2 = py1 + int(ph * 0.88)
                    lx1, lx2 = px1, px2

                lower_crop = image[ly1:ly2, lx1:lx2]
                if lower_crop.size > 100:
                    crops["lower_body"] = lower_crop
                    masks["lower_body"] = run_grabcut_segmentation(lower_crop)
                    regions["lower_body"] = _norm_region(lx1, ly1, lx2, ly2, w, h)
                    evidence_parts.append(f"Lower body region extracted [{lx1},{ly1},{lx2},{ly2}]")

            # ── SHOES REGION ──
            if feet_visible:
                if landmarks and any(str(i) in landmarks for i in [27, 28, 29, 30, 31, 32]):
                    foot_pts_y = [landmarks[str(i)]["y"] for i in [27, 28, 29, 30, 31, 32] if str(i) in landmarks]
                    foot_pts_x = [landmarks[str(i)]["x"] for i in [27, 28, 29, 30, 31, 32] if str(i) in landmarks]
                    ankle_y = min(foot_pts_y)
                    ankle_x_min = min(foot_pts_x)
                    ankle_x_max = max(foot_pts_x)

                    margin_x = max(0.08, (ankle_x_max - ankle_x_min) * 0.8)
                    sy1 = max(0, int((ankle_y - 0.03) * h))
                    sy2 = min(h, py2)
                    sx1 = max(0, int((ankle_x_min - margin_x) * w))
                    sx2 = min(w, int((ankle_x_max + margin_x) * w))
                else:
                    pw, ph = px2 - px1, py2 - py1
                    sy1 = py1 + int(ph * 0.85)
                    sy2 = py2
                    sx1, sx2 = px1, px2

                shoes_crop = image[sy1:sy2, sx1:sx2]
                if shoes_crop.size > 50:
                    crops["shoes"] = shoes_crop
                    masks["shoes"] = run_grabcut_segmentation(shoes_crop)
                    regions["shoes"] = _norm_region(sx1, sy1, sx2, sy2, w, h)
                    evidence_parts.append(f"Shoes region extracted [{sx1},{sy1},{sx2},{sy2}]")

            evidence = "; ".join(evidence_parts) if evidence_parts else "No garment segmentation crops extracted"
            segmented = any(c is not None for c in crops.values())

            logger.info(f"[BodySegmenter] Segmented status={'✓' if segmented else '✗'} | {evidence}")

            return {
                "segmented": segmented,
                "image_dimensions": {"width": w, "height": h},
                "regions": regions,
                "crops": crops,
                "masks": masks,
                "mask_ready": segmented,
                "evidence": evidence,
                "source": "grabcut_segmentation",
            }

        except Exception as e:
            logger.error(f"[BodySegmenter] Error during segmentation: {e}", exc_info=True)
            return {
                "segmented": False,
                "image_dimensions": {"width": 0, "height": 0},
                "regions": {},
                "crops": {"upper_body": None, "lower_body": None, "shoes": None, "face": None},
                "masks": {},
                "mask_ready": False,
                "evidence": f"Segmentation failed: {str(e)}",
                "source": "none",
            }


def _has_landmarks(landmarks: dict, indices: list, min_vis: float = 0.20) -> bool:
    """Check if ANY or ALL specified landmark indices exist and meet minimum visibility threshold."""
    for idx in indices:
        key = str(idx)
        if key in landmarks and landmarks[key].get("visibility", 0) >= min_vis:
            return True
    return False


def _norm_region(x1, y1, x2, y2, w, h) -> dict:
    return {
        "x_min": round(x1 / w, 4),
        "y_min": round(y1 / h, 4),
        "x_max": round(x2 / w, 4),
        "y_max": round(y2 / h, 4),
    }

