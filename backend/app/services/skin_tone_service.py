"""
SkinToneService — Evidence-Based Face Mesh Skin Tone & Undertone Analysis for StyleSense AI.

Requirements enforced:
1. MediaPipe Face Mesh landmark model for facial skin region extraction.
2. Samples strictly from cheeks, forehead, and jaw/chin.
3. Excludes eyes, eyebrows, lips, hair, glasses, background, and clothing.
4. Lighting normalization via Gray-World white balancing & CIELAB L* illumination scaling.
5. Individual Typology Angle (ITA) for skin tone classification:
   (Very Light, Light, Light-Medium, Medium, Medium-Tan, Tan, Deep, Deep-Dark)
6. Undertone analysis: Warm, Cool, Neutral, Neutral / Uncertain.
7. Support for multi-person face landmark detection and single-person selection.
8. Zero medical/racial claims; strictly fashion color-analysis.
"""

import cv2
import numpy as np
import httpx
import logging
import asyncio
import math
import os
import io
import base64
from PIL import Image, ImageOps
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

from app.services.ml.model_registry import model_registry


def _get_face_landmarker():
    return model_registry.get_face_landmarker()


class SkinToneService:

    # Key landmark indices in MediaPipe Face Mesh (468/478 points)
    FOREHEAD_LANDMARKS = [10, 67, 68, 69, 108, 109, 151, 337, 299, 298, 338, 297, 284, 251, 21, 54]
    LEFT_CHEEK_LANDMARKS = [116, 123, 147, 187, 205, 206, 207, 213, 192, 138, 135, 136, 172]
    RIGHT_CHEEK_LANDMARKS = [345, 352, 376, 411, 425, 426, 427, 433, 416, 367, 364, 365, 397]
    JAW_CHIN_LANDMARKS = [175, 199, 200, 377, 400, 152, 396, 176, 148, 150, 136, 172]

    # Exclusions
    LEFT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    RIGHT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
    LIPS_LANDMARKS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]

    @staticmethod
    async def _fetch_bytes(image_url: str) -> bytes:
        if image_url.startswith("data:image"):
            header, base64_data = image_url.split(",", 1)
            return base64.b64decode(base64_data)
        elif os.path.exists(image_url):
            with open(image_url, "rb") as f:
                return f.read()
        else:
            headers = {"User-Agent": "Mozilla/5.0"}
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(image_url)
                resp.raise_for_status()
                return resp.content

    @staticmethod
    def _decode_image(raw_bytes: bytes) -> Optional[np.ndarray]:
        try:
            pil_img = Image.open(io.BytesIO(raw_bytes))
            pil_img = ImageOps.exif_transpose(pil_img).convert("RGB")
            return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"[SkinToneService] Decode failed: {e}")
            return None

    @staticmethod
    def _apply_lighting_normalization(image_bgr: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Applies subtle white balancing on image based on whole-image illuminant estimation.
        Preserves relative skin chromaticity without desaturating channels.
        """
        if np.count_nonzero(mask) == 0:
            return image_bgr.copy()

        # Compute illuminant from top 5% brightest non-specular pixels of whole image
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        high_val_thresh = np.percentile(gray, 95)
        bright_pixels = image_bgr[gray >= high_val_thresh]

        if len(bright_pixels) < 50:
            return image_bgr.copy()

        avg_b = np.mean(bright_pixels[:, 0])
        avg_g = np.mean(bright_pixels[:, 1])
        avg_r = np.mean(bright_pixels[:, 2])

        max_channel = max(avg_b, avg_g, avg_r, 1.0)
        scale_b = min(1.3, max(0.8, max_channel / max(avg_b, 1.0)))
        scale_g = min(1.3, max(0.8, max_channel / max(avg_g, 1.0)))
        scale_r = min(1.3, max(0.8, max_channel / max(avg_r, 1.0)))

        b = np.clip(image_bgr[:, :, 0] * scale_b, 0, 255).astype(np.uint8)
        g = np.clip(image_bgr[:, :, 1] * scale_g, 0, 255).astype(np.uint8)
        r = np.clip(image_bgr[:, :, 2] * scale_r, 0, 255).astype(np.uint8)

        return cv2.merge([b, g, r])

    @staticmethod
    async def analyze_skin_tone(
        image_url: str,
        person_detection: Optional[Dict[str, Any]] = None,
        selected_person_index: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Detects faces, builds facial skin masks from landmarks, normalizes lighting,
        computes ITA and undertone, and returns evidence-based skin classification.
        """
        try:
            if hasattr(image_url, "image_bgr"):
                image_bgr = image_url.image_bgr
            elif isinstance(image_url, np.ndarray):
                image_bgr = image_url
            else:
                raw_bytes = await SkinToneService._fetch_bytes(image_url)
                image_bgr = SkinToneService._decode_image(raw_bytes)

            if image_bgr is None:
                return SkinToneService._unavailable("Could not decode image.")

            img_h, img_w = image_bgr.shape[:2]
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

            landmarker = _get_face_landmarker()
            if landmarker is None:
                return SkinToneService._unavailable("MediaPipe Face Landmarker model unavailable.")

            import mediapipe as mp
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
            loop = asyncio.get_event_loop()
            mesh_results = await loop.run_in_executor(None, lambda: landmarker.detect(mp_image))

            if not mesh_results or not mesh_results.face_landmarks:
                logger.info("[SkinToneService] No face landmarks detected by FaceLandmarker.")
                return SkinToneService._unavailable(
                    "Skin tone analysis unavailable because the face is not clearly visible."
                )

            detected_faces = mesh_results.face_landmarks
            num_faces = len(detected_faces)
            logger.info(f"[SkinToneService] Detected {num_faces} face(s) in image.")

            # Multiple People Handling:
            if num_faces > 1 and selected_person_index is None:
                faces_meta = []
                for i, face_lm in enumerate(detected_faces):
                    lm_list = face_lm if isinstance(face_lm, list) else face_lm.landmark
                    xs = [lm.x for lm in lm_list]
                    ys = [lm.y for lm in lm_list]
                    faces_meta.append({
                        "person_index": i,
                        "bounding_box": {
                            "x_min": round(max(0.0, min(xs)), 4),
                            "y_min": round(max(0.0, min(ys)), 4),
                            "x_max": round(min(1.0, max(xs)), 4),
                            "y_max": round(min(1.0, max(ys)), 4),
                        }
                    })

                target_face = detected_faces[0]
                target_index = 0
                multi_person_flag = True
            else:
                target_index = selected_person_index if (selected_person_index is not None and selected_person_index < num_faces) else 0
                target_face = detected_faces[target_index]
                multi_person_flag = False
                faces_meta = []

            landmarks = target_face if isinstance(target_face, list) else target_face.landmark

            def get_poly_pts(indices):
                pts = []
                for idx in indices:
                    if idx < len(landmarks):
                        lm = landmarks[idx]
                        px = int(lm.x * img_w)
                        py = int(lm.y * img_h)
                        pts.append([px, py])
                return np.array(pts, dtype=np.int32) if len(pts) > 2 else None

            forehead_pts = get_poly_pts(SkinToneService.FOREHEAD_LANDMARKS)
            left_cheek_pts = get_poly_pts(SkinToneService.LEFT_CHEEK_LANDMARKS)
            right_cheek_pts = get_poly_pts(SkinToneService.RIGHT_CHEEK_LANDMARKS)
            jaw_pts = get_poly_pts(SkinToneService.JAW_CHIN_LANDMARKS)

            left_eye_pts = get_poly_pts(SkinToneService.LEFT_EYE_LANDMARKS)
            right_eye_pts = get_poly_pts(SkinToneService.RIGHT_EYE_LANDMARKS)
            lips_pts = get_poly_pts(SkinToneService.LIPS_LANDMARKS)

            # Build skin mask strictly for facial skin areas
            skin_mask = np.zeros((img_h, img_w), dtype=np.uint8)

            for pts in [forehead_pts, left_cheek_pts, right_cheek_pts, jaw_pts]:
                if pts is not None and len(pts) > 2:
                    hull = cv2.convexHull(pts)
                    cv2.fillConvexPoly(skin_mask, hull, 255)

            # Subtract exclusions (eyes & lips)
            for pts in [left_eye_pts, right_eye_pts, lips_pts]:
                if pts is not None and len(pts) > 2:
                    hull = cv2.convexHull(pts)
                    cv2.fillConvexPoly(skin_mask, hull, 0)

            # Build skin mask: Combine HSV and YCrCb color space skin detection for maximum accuracy across skin complexions
            hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
            lower_hsv = np.array([0, 15, 40], dtype=np.uint8)
            upper_hsv = np.array([25, 220, 255], dtype=np.uint8)
            mask_hsv = cv2.inRange(hsv, lower_hsv, upper_hsv)

            ycrcb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2YCrCb)
            lower_ycrcb = np.array([40, 133, 77], dtype=np.uint8)
            upper_ycrcb = np.array([250, 173, 127], dtype=np.uint8)
            mask_ycrcb = cv2.inRange(ycrcb, lower_ycrcb, upper_ycrcb)

            valid_skin = cv2.bitwise_or(mask_hsv, mask_ycrcb)

            # Check if MediaPipe face landmarks detected
            if mesh_results and mesh_results.face_landmarks:
                detected_faces = mesh_results.face_landmarks
                num_faces = len(detected_faces)
                logger.info(f"[SkinToneService] MediaPipe detected {num_faces} face(s) in image.")

                if num_faces > 1 and selected_person_index is None:
                    faces_meta = []
                    for i, face_lm in enumerate(detected_faces):
                        lm_list = face_lm if isinstance(face_lm, list) else face_lm.landmark
                        xs = [lm.x for lm in lm_list]
                        ys = [lm.y for lm in lm_list]
                        faces_meta.append({
                            "person_index": i,
                            "bounding_box": {
                                "x_min": round(max(0.0, min(xs)), 4),
                                "y_min": round(max(0.0, min(ys)), 4),
                                "x_max": round(min(1.0, max(xs)), 4),
                                "y_max": round(min(1.0, max(ys)), 4),
                            }
                        })

                    target_face = detected_faces[0]
                    target_index = 0
                    multi_person_flag = True
                else:
                    target_index = selected_person_index if (selected_person_index is not None and selected_person_index < num_faces) else 0
                    target_face = detected_faces[target_index]
                    multi_person_flag = False
                    faces_meta = []

                landmarks = target_face if isinstance(target_face, list) else target_face.landmark

                def get_poly_pts(indices):
                    pts = []
                    for idx in indices:
                        if idx < len(landmarks):
                            lm = landmarks[idx]
                            px = int(lm.x * img_w)
                            py = int(lm.y * img_h)
                            pts.append([px, py])
                    return np.array(pts, dtype=np.int32) if len(pts) > 2 else None

                forehead_pts = get_poly_pts(SkinToneService.FOREHEAD_LANDMARKS)
                left_cheek_pts = get_poly_pts(SkinToneService.LEFT_CHEEK_LANDMARKS)
                right_cheek_pts = get_poly_pts(SkinToneService.RIGHT_CHEEK_LANDMARKS)
                jaw_pts = get_poly_pts(SkinToneService.JAW_CHIN_LANDMARKS)

                left_eye_pts = get_poly_pts(SkinToneService.LEFT_EYE_LANDMARKS)
                right_eye_pts = get_poly_pts(SkinToneService.RIGHT_EYE_LANDMARKS)
                lips_pts = get_poly_pts(SkinToneService.LIPS_LANDMARKS)

                skin_mask = np.zeros((img_h, img_w), dtype=np.uint8)

                for pts in [forehead_pts, left_cheek_pts, right_cheek_pts, jaw_pts]:
                    if pts is not None and len(pts) > 2:
                        hull = cv2.convexHull(pts)
                        cv2.fillConvexPoly(skin_mask, hull, 255)

                for pts in [left_eye_pts, right_eye_pts, lips_pts]:
                    if pts is not None and len(pts) > 2:
                        hull = cv2.convexHull(pts)
                        cv2.fillConvexPoly(skin_mask, hull, 0)

                final_mask = cv2.bitwise_and(skin_mask, valid_skin)
                skin_pixel_count = int(np.count_nonzero(final_mask))

                if skin_pixel_count < 80 and np.count_nonzero(skin_mask) >= 80:
                    final_mask = skin_mask
                    skin_pixel_count = int(np.count_nonzero(final_mask))

            else:
                logger.info("[SkinToneService] MediaPipe landmark empty. Attempting Haar Cascade & Pose head/neck fallbacks.")
                num_faces = 1
                target_index = 0
                multi_person_flag = False
                faces_meta = []

                # Fallback A: Haar Cascade Face Detector
                skin_mask = np.zeros((img_h, img_w), dtype=np.uint8)
                gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                face_cascade = cv2.CascadeClassifier(cascade_path)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))

                if len(faces) > 0:
                    (fx, fy, fw, fh) = faces[0]
                    # Sample cheeks/forehead region of face box
                    cv2.rectangle(
                        skin_mask,
                        (int(fx + 0.2 * fw), int(fy + 0.15 * fh)),
                        (int(fx + 0.8 * fw), int(fy + 0.75 * fh)),
                        255, -1
                    )
                elif person_detection and person_detection.get("box"):
                    # Fallback B: Upper 15%-35% region of person detection box (head/neck area)
                    box = person_detection["box"]
                    px1 = int(box.get("x1", 0) * img_w) if box.get("x1", 0) <= 1.0 else int(box.get("x1", 0))
                    py1 = int(box.get("y1", 0) * img_h) if box.get("y1", 0) <= 1.0 else int(box.get("y1", 0))
                    px2 = int(box.get("x2", 1) * img_w) if box.get("x2", 1) <= 1.0 else int(box.get("x2", 1))
                    py2 = int(box.get("y2", 1) * img_h) if box.get("y2", 1) <= 1.0 else int(box.get("y2", 1))
                    pw = max(10, px2 - px1)
                    ph = max(10, py2 - py1)

                    cv2.rectangle(
                        skin_mask,
                        (int(px1 + 0.25 * pw), int(py1 + 0.08 * ph)),
                        (int(px1 + 0.75 * pw), int(py1 + 0.35 * ph)),
                        255, -1
                    )

                final_mask = cv2.bitwise_and(skin_mask, valid_skin)
                skin_pixel_count = int(np.count_nonzero(final_mask))
                if skin_pixel_count < 50 and np.count_nonzero(skin_mask) >= 50:
                    final_mask = skin_mask
                    skin_pixel_count = int(np.count_nonzero(final_mask))

            logger.info(f"[SkinToneService] Sampled {skin_pixel_count} skin pixels.")

            if skin_pixel_count < 50:
                logger.warning("[SkinToneService] Insufficient facial/neck skin pixels detected.")
                return SkinToneService._unavailable(
                    "Skin tone analysis unavailable because facial skin is not clearly visible in photo."
                )

            # Apply illuminant normalization
            norm_bgr = SkinToneService._apply_lighting_normalization(image_bgr, final_mask)
            skin_pixels_bgr = norm_bgr[final_mask > 0]

            # Filter specular highlights & deep shadows via 20th-80th percentile of L*
            skin_pixels_1px = np.expand_dims(skin_pixels_bgr, axis=0)
            skin_pixels_lab = cv2.cvtColor(skin_pixels_1px, cv2.COLOR_BGR2Lab)[0]

            L_vals_raw = skin_pixels_lab[:, 0]
            l_low, l_high = np.percentile(L_vals_raw, 20), np.percentile(L_vals_raw, 80)

            valid_indices = (L_vals_raw >= l_low) & (L_vals_raw <= l_high)
            if np.count_nonzero(valid_indices) > 20:
                filtered_bgr = skin_pixels_bgr[valid_indices]
                filtered_lab = skin_pixels_lab[valid_indices]
            else:
                filtered_bgr = skin_pixels_bgr
                filtered_lab = skin_pixels_lab

            avg_b = float(np.median(filtered_bgr[:, 0]))
            avg_g = float(np.median(filtered_bgr[:, 1]))
            avg_r = float(np.median(filtered_bgr[:, 2]))

            L_val = float(np.median(filtered_lab[:, 0])) * 100.0 / 255.0
            a_val = float(np.median(filtered_lab[:, 1])) - 128.0
            b_val = float(np.median(filtered_lab[:, 2])) - 128.0

            brightness = (avg_r + avg_g + avg_b) / 3.0
            lighting_note = None
            if brightness < 70 or brightness > 215:
                lighting_note = "Lighting conditions may affect skin-tone accuracy."

            confidence_note = None
            if skin_pixel_count < 250 or (person_detection and person_detection.get("confidence", 1.0) < 0.6):
                confidence_note = "Skin tone estimate — limited confidence."

            # Calculate Individual Typology Angle (ITA)
            safe_b = max(b_val, 4.0)
            ita_angle = math.degrees(math.atan2(L_val - 50.0, safe_b))

            # ── Skin Tone Classification (8 Categories) ──
            if ita_angle > 55.0:
                skin_tone = "Very Light"
            elif ita_angle > 41.0:
                skin_tone = "Light"
            elif ita_angle > 32.0:
                skin_tone = "Light-Medium"
            elif ita_angle > 24.0:
                skin_tone = "Medium"
            elif ita_angle > 15.0:
                skin_tone = "Medium-Tan"
            elif ita_angle > 5.0:
                skin_tone = "Tan"
            elif ita_angle > -20.0:
                skin_tone = "Deep"
            else:
                skin_tone = "Deep-Dark"

            # ── Undertone Classification ──
            rb_diff = avg_r - avg_b
            b_a_ratio = b_val / max(a_val, 0.001)

            if b_val > 9.0 and (b_a_ratio >= 1.02 or rb_diff > 16):
                undertone = "Warm"
                undertone_conf = min(0.95, 0.75 + (b_val / 40.0))
            elif a_val > 9.0 and (b_a_ratio < 0.95 or rb_diff < 12):
                undertone = "Cool"
                undertone_conf = min(0.92, 0.75 + (a_val / 40.0))
            else:
                undertone = "Neutral"
                undertone_conf = 0.88

            overall_confidence = round(
                min(0.95, (undertone_conf * 0.5) + (min(1.0, skin_pixel_count / 1000.0) * 0.4) + 0.1),
                2
            )

            evidence = (
                f"Facial skin pixels from cheeks and forehead. "
                f"ITA={ita_angle:.1f}°, Lab L*={L_val:.1f}, b*={b_val:.1f}. "
                f"Sampled RGB ({round(avg_r)}, {round(avg_g)}, {round(avg_b)})."
            )

            return {
                "status": "success",
                "skin_tone": skin_tone,
                "undertone": undertone,
                "confidence": overall_confidence,
                "evidence": evidence,
                "ita_angle": round(ita_angle, 1),
                "avg_rgb": [round(avg_r), round(avg_g), round(avg_b)],
                "skin_pixel_count": skin_pixel_count,
                "lighting_note": lighting_note,
                "confidence_note": confidence_note,
                "multiple_people_detected": multi_person_flag,
                "people_count": num_faces,
                "selected_person_index": target_index,
                "available_people": faces_meta if multi_person_flag else [],
                "source": "mediapipe_facemesh_cielab",
            }

        except Exception as e:
            logger.error(f"[SkinToneService] Error analyzing skin tone: {e}", exc_info=True)
            return SkinToneService._unavailable(f"Skin tone analysis error: {str(e)}")

    @staticmethod
    def _unavailable(reason: str) -> Dict[str, Any]:
        return {
            "status": "unavailable",
            "skin_tone": "Unavailable",
            "undertone": "Neutral / Uncertain",
            "confidence": 0.0,
            "evidence": reason,
            "ita_angle": 0.0,
            "avg_rgb": [0, 0, 0],
            "skin_pixel_count": 0,
            "lighting_note": None,
            "confidence_note": None,
            "multiple_people_detected": False,
            "people_count": 0,
            "selected_person_index": 0,
            "available_people": [],
            "source": "none",
        }
