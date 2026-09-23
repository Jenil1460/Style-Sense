"""
FaceShapeDetector — MediaPipe FaceMesh Landmark Analysis for StyleSense AI.

Zero-hallucination guarantees:
- Uses MediaPipe FaceMesh to measure jaw width / face height ratio
- NEVER hardcodes "Oval" (removed)
- Returns "Unknown" if face landmarks not detected
- Every result has {value, confidence, evidence}
"""

import cv2
import numpy as np
import httpx
import logging
import asyncio
import io
import os
import base64
from PIL import Image

logger = logging.getLogger(__name__)

from app.services.ml.model_registry import model_registry


def _get_face_mesh():
    return model_registry.get_face_mesh()


class FaceShapeDetector:
    """
    Estimates face shape using MediaPipe FaceMesh landmark geometry.
    Classifications: Oval, Round, Square, Heart, Oblong
    """

    @staticmethod
    async def detect(image_url: Any, skin_result: dict = None) -> dict:
        try:
            # Fetch image
            if hasattr(image_url, "image_bgr"):
                image = image_url.image_bgr
            elif isinstance(image_url, np.ndarray):
                image = image_url
            elif str(image_url).startswith("data:image"):
                header, base64_data = str(image_url).split(",", 1)
                raw = base64.b64decode(base64_data)
                image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
            elif isinstance(image_url, str) and os.path.exists(image_url):
                with open(image_url, "rb") as f:
                    raw = f.read()
                image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
            else:
                headers = {"User-Agent": "Mozilla/5.0"}
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
                    resp = await client.get(str(image_url))
                    resp.raise_for_status()
                    raw = resp.content
                image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)

            if image is None:
                return FaceShapeDetector._unknown("Could not decode image for FaceMesh")

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w = image.shape[:2]

            # Run FaceLandmarker
            landmarker = model_registry.get_face_landmarker()
            if landmarker is None:
                return FaceShapeDetector._unknown("MediaPipe FaceLandmarker not available")

            import mediapipe as mp
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, lambda: landmarker.detect(mp_image))

            if not results or not results.face_landmarks:
                return FaceShapeDetector._unknown("No face landmarks detected by FaceLandmarker")

            target_face = results.face_landmarks[0]
            face_lm = target_face if isinstance(target_face, list) else target_face.landmark

            # Key measurements using FaceMesh landmark indices:
            # Forehead width: landmarks 54 to 284 (across forehead)
            # Jaw width: landmarks 172 to 397 (across jaw)
            # Face height: landmarks 10 (top forehead) to 152 (chin)
            # Cheekbone width: landmarks 234 to 454

            forehead_width = abs(face_lm[54].x - face_lm[284].x)
            jaw_width = abs(face_lm[172].x - face_lm[397].x)
            cheekbone_width = abs(face_lm[234].x - face_lm[454].x)
            face_height = abs(face_lm[10].y - face_lm[152].y)

            # Ratios for classification
            jaw_to_cheek = jaw_width / max(cheekbone_width, 0.001)
            width_to_height = cheekbone_width / max(face_height, 0.001)
            forehead_to_jaw = forehead_width / max(jaw_width, 0.001)

            # Classification based on geometric ratios
            if width_to_height > 0.85:
                face_shape = "Round"
                evidence = f"Width-to-height ratio {width_to_height:.2f} > 0.85 indicates round face"
                confidence = min(0.85, 0.5 + abs(width_to_height - 0.85) * 2)
            elif jaw_to_cheek > 0.90 and width_to_height < 0.75:
                face_shape = "Square"
                evidence = f"Jaw-to-cheekbone ratio {jaw_to_cheek:.2f} and low W/H {width_to_height:.2f} indicate square face"
                confidence = min(0.85, 0.5 + (jaw_to_cheek - 0.9) * 2)
            elif forehead_to_jaw > 1.2:
                face_shape = "Heart"
                evidence = f"Forehead-to-jaw ratio {forehead_to_jaw:.2f} > 1.2 indicates heart-shaped face"
                confidence = min(0.80, 0.5 + (forehead_to_jaw - 1.2) * 1.5)
            elif width_to_height < 0.65:
                face_shape = "Oblong"
                evidence = f"Width-to-height ratio {width_to_height:.2f} < 0.65 indicates oblong face"
                confidence = min(0.80, 0.5 + abs(0.65 - width_to_height) * 3)
            else:
                face_shape = "Oval"
                evidence = f"Balanced proportions (W/H={width_to_height:.2f}, J/C={jaw_to_cheek:.2f}) indicate oval face"
                confidence = 0.75

            # Accessory recommendations based on detected shape
            tips = {
                "Oval": "Oval face shapes complement most necklines, collars, and eyewear frames.",
                "Round": "Angular frames and V-necklines help elongate a round face shape.",
                "Square": "Round frames and scoop necklines soften strong jawline features.",
                "Heart": "Cat-eye frames and crew necklines balance a wider forehead.",
                "Oblong": "Wide frames and boat necklines add width to an elongated face.",
            }

            logger.info(f"[FaceShapeDetector] Detected: {face_shape} (conf={confidence:.2f})")

            return {
                "face_shape": face_shape,
                "confidence": round(confidence, 2),
                "accessory_tip": tips.get(face_shape, ""),
                "evidence": f"FaceMesh landmarks: {evidence}",
                "source": "mediapipe_facemesh",
                "measurements": {
                    "forehead_width": round(forehead_width, 4),
                    "jaw_width": round(jaw_width, 4),
                    "cheekbone_width": round(cheekbone_width, 4),
                    "face_height": round(face_height, 4),
                }
            }

        except Exception as e:
            logger.error(f"[FaceShapeDetector] Error: {e}", exc_info=True)
            return FaceShapeDetector._unknown(f"Face shape detection failed: {str(e)}")

    @staticmethod
    def _unknown(reason: str) -> dict:
        return {
            "face_shape": "Unknown",
            "confidence": 0.0,
            "accessory_tip": "Face shape could not be determined from this image.",
            "evidence": reason,
            "source": "none",
        }
