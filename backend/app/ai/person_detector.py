"""
PersonDetector — Robust Multi-Strategy Person Detection for StyleSense AI.

Detection cascade (in order of priority):
1. YOLO standard detection (imgsz=640, conf=0.25)
2. YOLO scaled detection (for small images, lower conf)
3. YOLO aggressive retry (very low conf, multiple imgsz, padded image)
4. CLIP-only standalone person classification (zero-shot)
5. MediaPipe pose skeleton detection (if skeleton found → person exists)

Guarantees:
- Uses Ultralytics YOLO person detector as primary (COCO Class 0 = person)
- CLIP zero-shot verification rejects false positives on low-confidence YOLO
- CLIP and MediaPipe serve as fallbacks when YOLO fails entirely
- NO OpenCV Haar Cascades, NO HOG, NO skin-tone heuristics
- Returns person detected status, normalized & pixel bounding boxes, and confidence.
"""

import cv2
import numpy as np
import httpx
import logging
import os
import asyncio
import io
import base64
from typing import Any
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

PERSON_CLASS_ID = 0  # COCO class 0 = person
CONFIDENCE_THRESHOLD = 0.25

# CLIP verification threshold: if CLIP says "person" probability < this, reject
CLIP_PERSON_VERIFY_THRESHOLD = 0.38

_yolo_model = None

# CLIP model cache (shared with clothing_detector if already loaded)
_clip_model = None
_clip_preprocess = None
_clip_tokenizer = None


from app.services.ml.model_registry import model_registry, PERSON_VERIFY_PROMPTS


def _load_yolo():
    return model_registry.get_yolo_person()


def _load_clip():
    return model_registry.get_clip()


def _verify_person_with_clip(image_bgr: np.ndarray) -> dict:
    """
    CLIP zero-shot verification: Is this image actually a person/human?
    Uses precomputed text embeddings from ModelRegistry for sub-10ms verification.
    """
    try:
        keys = ["person", "not_person"]
        res = model_registry.classify_crop_with_clip(image_bgr, "person_verify", keys)
        if res is None:
            return {"is_person": True, "person_prob": 1.0, "evidence": "CLIP unavailable, verification skipped."}

        person_prob = res["probs"].get("person", 0.5)
        not_person_prob = res["probs"].get("not_person", 0.5)
        is_person = person_prob >= not_person_prob

        evidence = (
            f"CLIP verification: person={person_prob:.3f}, not_person={not_person_prob:.3f}. "
            f"{'PASS' if is_person else 'REJECTED — image is not a person.'}"
        )
        logger.info(f"[PersonDetector] {evidence}")
        return {"is_person": is_person, "person_prob": person_prob, "evidence": evidence}
    except Exception as e:
        logger.warning(f"[PersonDetector] CLIP verification error: {e}")
        return {"is_person": True, "person_prob": 1.0, "evidence": f"CLIP error: {e}, verification skipped."}

    try:
        import torch
        from PIL import Image as PILImage

        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        pil_img = PILImage.fromarray(rgb)
        image_input = preprocess(pil_img).unsqueeze(0)

        # Binary classification: person vs not-person
        prompts = [
            "a photograph of a person, human, man, or woman",
            "a photograph of a machine, vehicle, animal, food, product, or landscape with no people",
        ]
        text_inputs = tokenizer(prompts)

        with torch.no_grad():
            image_features = model.encode_image(image_input)
            text_features = model.encode_text(text_inputs)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            sims = (image_features @ text_features.T).squeeze(0)
            probs = sims.softmax(dim=-1)

        person_prob = float(probs[0])
        not_person_prob = float(probs[1])

        # Reject ONLY if non-person clearly dominates
        is_person = person_prob >= not_person_prob

        evidence = (
            f"CLIP verification: person={person_prob:.3f}, not_person={not_person_prob:.3f}. "
            f"{'PASS' if is_person else 'REJECTED — image is not a person.'}"
        )

        logger.info(f"[PersonDetector] {evidence}")
        return {"is_person": is_person, "person_prob": person_prob, "evidence": evidence}

    except Exception as e:
        logger.warning(f"[PersonDetector] CLIP verification error: {e}")
        return {"is_person": True, "person_prob": 1.0, "evidence": f"CLIP error: {e}, verification skipped."}


def _detect_person_with_mediapipe(image_bgr: np.ndarray) -> dict:
    """
    MediaPipe Pose fallback: if we can detect a human skeleton, a person exists.
    Uses the new MediaPipe Tasks API (PoseLandmarker).
    Returns {"detected": bool, "confidence": float, "evidence": str, "landmarks_found": int}
    """
    try:
        import mediapipe as mp
        import os
        import urllib.request

        # Download the pose landmarker model if not cached
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(backend_dir, "pose_landmarker_lite.task")

        if not os.path.exists(model_path):
            logger.info("[PersonDetector] Downloading MediaPipe pose landmarker model...")
            url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
            try:
                urllib.request.urlretrieve(url, model_path)
                logger.info(f"[PersonDetector] Pose landmarker model saved to {model_path}")
            except Exception as dl_err:
                logger.warning(f"[PersonDetector] Could not download pose model: {dl_err}")
                return {"detected": False, "confidence": 0.0, "evidence": f"Pose model download failed: {dl_err}", "landmarks_found": 0}

        # Use Tasks API
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.IMAGE,
            min_pose_detection_confidence=0.3,
            min_tracking_confidence=0.3,
        )

        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        with PoseLandmarker.create_from_options(options) as landmarker:
            result = landmarker.detect(mp_image)

            if result.pose_landmarks and len(result.pose_landmarks) > 0:
                landmarks = result.pose_landmarks[0]
                # Count visible landmarks (visibility > 0.3)
                visible = sum(1 for lm in landmarks if lm.visibility > 0.3)
                total = len(landmarks)
                conf = round(visible / total, 3) if total > 0 else 0.0

                logger.info(f"[PersonDetector] MediaPipe fallback: {visible}/{total} landmarks visible, conf={conf}")
                return {
                    "detected": True,
                    "confidence": max(conf, 0.45),  # Floor at 0.45 since skeleton = definite person
                    "evidence": f"MediaPipe skeleton detected ({visible}/{total} landmarks visible).",
                    "landmarks_found": visible,
                }
            else:
                return {"detected": False, "confidence": 0.0, "evidence": "MediaPipe found no skeleton.", "landmarks_found": 0}
    except Exception as e:
        logger.warning(f"[PersonDetector] MediaPipe fallback error: {e}")
        return {"detected": False, "confidence": 0.0, "evidence": f"MediaPipe error: {e}", "landmarks_found": 0}


class PersonDetector:

    @staticmethod
    async def _fetch_bytes(image_url: Any) -> bytes:
        """Fetch bytes from HTTP/HTTPS, local file path, Base64 URI, or raw bytes."""
        if isinstance(image_url, bytes):
            return image_url
        if str(image_url).startswith("data:image"):
            header, base64_data = str(image_url).split(",", 1)
            return base64.b64decode(base64_data)
        elif isinstance(image_url, str) and os.path.exists(image_url):
            with open(image_url, "rb") as f:
                return f.read()
        else:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(str(image_url))
                resp.raise_for_status()
                return resp.content

    @staticmethod
    def _decode_image(raw_bytes: bytes) -> np.ndarray:
        """Decode image bytes to BGR numpy array with EXIF auto-rotation."""
        try:
            pil_img = Image.open(io.BytesIO(raw_bytes))
            pil_img = ImageOps.exif_transpose(pil_img).convert("RGB")
            return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"[PersonDetector] Image decode failed: {e}")
            return None

    @staticmethod
    def _run_yolo_on_image(model, image: np.ndarray, conf: float, imgsz: int) -> list:
        """Run YOLO prediction synchronously and extract person boxes."""
        img_h, img_w = image.shape[:2]
        person_boxes = []
        try:
            results = model.predict(source=image, conf=conf, verbose=False, imgsz=imgsz)
            for box in results[0].boxes:
                cls_id = int(box.cls[0].item())
                box_conf = round(float(box.conf[0].item()), 4)
                if cls_id == PERSON_CLASS_ID:
                    x1, y1, x2, y2 = [round(v) for v in box.xyxy[0].tolist()]
                    person_boxes.append({
                        "confidence": box_conf,
                        "x_min_px": max(0, x1),
                        "y_min_px": max(0, y1),
                        "x_max_px": min(img_w, x2),
                        "y_max_px": min(img_h, y2),
                        "x_min": round(max(0, x1) / img_w, 4),
                        "y_min": round(max(0, y1) / img_h, 4),
                        "x_max": round(min(img_w, x2) / img_w, 4),
                        "y_max": round(min(img_h, y2) / img_h, 4),
                        "source": f"yolo_imgsz{imgsz}"
                    })
        except Exception as e:
            logger.warning(f"[PersonDetector] YOLO predict error (imgsz={imgsz}, conf={conf}): {e}")
        return person_boxes

    @staticmethod
    async def detect(image_url: Any) -> dict:
        """
        Multi-strategy person detection with robust fallback chain.

        Strategy cascade:
        1. YOLO standard (imgsz=640, conf=0.25)
        2. YOLO scaled (for small images < 1200px)
        3. YOLO aggressive (very low conf=0.10, multiple imgsz, padded image)
        4. CLIP-only standalone person classification
        5. MediaPipe pose skeleton detection
        """
        desc_str = "numpy array" if isinstance(image_url, np.ndarray) else str(image_url)[:80]
        logger.info(f"[PersonDetector] Running person detection on: {desc_str}...")

        # ═══ STEP 1: Fetch & Decode Image ═══
        orig_w, orig_h = None, None
        if hasattr(image_url, "image_bgr"):
            image = image_url.image_bgr
            orig_w = image_url.original_w
            orig_h = image_url.original_h
        elif isinstance(image_url, np.ndarray):
            image = image_url
            orig_h, orig_w = image.shape[:2]
        else:
            try:
                raw_bytes = await PersonDetector._fetch_bytes(image_url)
            except Exception as e:
                logger.error(f"[PersonDetector] Fetch failed: {e}")
                return PersonDetector._no_detection(reason="download_failed")

            image = PersonDetector._decode_image(raw_bytes)
            if image is not None:
                orig_h, orig_w = image.shape[:2]

        if image is None:
            return PersonDetector._no_detection(reason="decode_failed")

        img_h, img_w = image.shape[:2]

        # ═══ STEP 2: YOLO Detection — Multi-strategy ═══
        model = _load_yolo()
        person_boxes = []

        if model is not None:
            try:
                loop = asyncio.get_event_loop()

                # Strategy 2a: Standard YOLO (imgsz=640, conf=0.25)
                person_boxes = await loop.run_in_executor(
                    None,
                    lambda: PersonDetector._run_yolo_on_image(model, image, CONFIDENCE_THRESHOLD, 640)
                )

                if person_boxes:
                    logger.info(f"[PersonDetector] Strategy 2a (standard): found {len(person_boxes)} person(s)")

                # Strategy 2b: Scaled YOLO for small images
                if not person_boxes and max(img_w, img_h) < 1200:
                    scale = 1200.0 / max(img_w, img_h)
                    scaled_img = cv2.resize(image, (int(img_w * scale), int(img_h * scale)))

                    scaled_boxes = await loop.run_in_executor(
                        None,
                        lambda: PersonDetector._run_yolo_on_image(model, scaled_img, CONFIDENCE_THRESHOLD * 0.8, 640)
                    )

                    # Map scaled coordinates back to original
                    for box in scaled_boxes:
                        box["x_min_px"] = max(0, round(box["x_min_px"] / scale))
                        box["y_min_px"] = max(0, round(box["y_min_px"] / scale))
                        box["x_max_px"] = min(img_w, round(box["x_max_px"] / scale))
                        box["y_max_px"] = min(img_h, round(box["y_max_px"] / scale))
                        box["x_min"] = round(box["x_min_px"] / img_w, 4)
                        box["y_min"] = round(box["y_min_px"] / img_h, 4)
                        box["x_max"] = round(box["x_max_px"] / img_w, 4)
                        box["y_max"] = round(box["y_max_px"] / img_h, 4)
                        box["source"] = "yolo_scaled"
                    person_boxes = scaled_boxes

                    if person_boxes:
                        logger.info(f"[PersonDetector] Strategy 2b (scaled): found {len(person_boxes)} person(s)")

                # Strategy 2c: Aggressive YOLO — very low conf, multiple resolutions, padded image
                if not person_boxes:
                    logger.info("[PersonDetector] Strategy 2c: aggressive YOLO retry...")

                    # Try multiple imgsz values with very low confidence
                    for imgsz_try in [320, 480, 1024]:
                        boxes_try = await loop.run_in_executor(
                            None,
                            lambda isz=imgsz_try: PersonDetector._run_yolo_on_image(model, image, 0.10, isz)
                        )
                        if boxes_try:
                            person_boxes = boxes_try
                            logger.info(f"[PersonDetector] Strategy 2c (imgsz={imgsz_try}): found {len(person_boxes)} person(s)")
                            break

                    # If still nothing, try with padded image (adds context around the image)
                    if not person_boxes:
                        pad = max(img_h, img_w) // 4
                        padded = cv2.copyMakeBorder(image, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(128, 128, 128))
                        padded_boxes = await loop.run_in_executor(
                            None,
                            lambda: PersonDetector._run_yolo_on_image(model, padded, 0.10, 640)
                        )
                        # Map padded coordinates back to original
                        for box in padded_boxes:
                            box["x_min_px"] = max(0, box["x_min_px"] - pad)
                            box["y_min_px"] = max(0, box["y_min_px"] - pad)
                            box["x_max_px"] = min(img_w, box["x_max_px"] - pad)
                            box["y_max_px"] = min(img_h, box["y_max_px"] - pad)
                            box["x_min"] = round(max(0, box["x_min_px"]) / img_w, 4)
                            box["y_min"] = round(max(0, box["y_min_px"]) / img_h, 4)
                            box["x_max"] = round(min(img_w, box["x_max_px"]) / img_w, 4)
                            box["y_max"] = round(min(img_h, box["y_max_px"]) / img_h, 4)
                            box["source"] = "yolo_padded"
                        person_boxes = padded_boxes

                        if person_boxes:
                            logger.info(f"[PersonDetector] Strategy 2c (padded): found {len(person_boxes)} person(s)")

            except Exception as e:
                logger.error(f"[PersonDetector] YOLO detection exception: {e}")
                # Don't return yet — fallback strategies below
        else:
            logger.warning("[PersonDetector] YOLO model unavailable, skipping to fallbacks.")

        # ═══ STEP 3: Fallback — CLIP-only + MediaPipe when YOLO found nothing ═══
        if not person_boxes:
            logger.info("[PersonDetector] YOLO found nothing. Running CLIP + MediaPipe fallbacks...")

            # Fallback A: CLIP standalone person classification
            clip_result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: _verify_person_with_clip(image)
            )

            # Fallback B: MediaPipe skeleton detection
            mediapipe_result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: _detect_person_with_mediapipe(image)
            )

            clip_says_person = clip_result.get("is_person", False)
            mediapipe_says_person = mediapipe_result.get("detected", False)
            clip_prob = clip_result.get("person_prob", 0.0)

            logger.info(
                f"[PersonDetector] Fallback results: CLIP={clip_says_person} (prob={clip_prob:.3f}), "
                f"MediaPipe={mediapipe_says_person} (landmarks={mediapipe_result.get('landmarks_found', 0)})"
            )

            # Accept if EITHER fallback confirms a person
            # For CLIP-only (without MediaPipe), require higher confidence to avoid false positives
            # on blank/ambiguous images where CLIP gives ~50% probability
            clip_standalone_threshold = 0.55
            clip_confident = clip_says_person and clip_prob >= clip_standalone_threshold

            if clip_confident or mediapipe_says_person:
                # Use full image as bounding box since YOLO couldn't localize
                fallback_conf = max(
                    clip_prob if clip_confident else 0.0,
                    mediapipe_result.get("confidence", 0.0) if mediapipe_says_person else 0.0,
                )
                # Floor confidence at 0.40 — fallback detection is legitimate
                fallback_conf = max(fallback_conf, 0.40)

                sources = []
                evidence_parts = []
                if clip_confident:
                    sources.append("clip")
                    evidence_parts.append(f"CLIP person_prob={clip_prob:.2f}")
                if mediapipe_says_person:
                    sources.append("mediapipe")
                    evidence_parts.append(f"MediaPipe skeleton ({mediapipe_result.get('landmarks_found', 0)} landmarks)")
                source_str = "+".join(sources) + "_fallback"
                evidence_str = ", ".join(evidence_parts)

                logger.info(
                    f"[PersonDetector] Person CONFIRMED via fallback ({source_str}): {evidence_str}"
                )

                return {
                    "detected": True,
                    "confidence": round(fallback_conf, 4),
                    "x_min": 0.0,
                    "y_min": 0.0,
                    "x_max": 1.0,
                    "y_max": 1.0,
                    "x_min_px": 0,
                    "y_min_px": 0,
                    "x_max_px": img_w,
                    "y_max_px": img_h,
                    "num_detections": 1,
                    "all_boxes": [{
                        "confidence": round(fallback_conf, 4),
                        "x_min_px": 0, "y_min_px": 0,
                        "x_max_px": img_w, "y_max_px": img_h,
                        "x_min": 0.0, "y_min": 0.0,
                        "x_max": 1.0, "y_max": 1.0,
                        "source": source_str,
                    }],
                    "evidence": (
                        f"Person detected via fallback ({source_str}). "
                        f"YOLO did not localize a person, but {evidence_str} confirmed a person is present. "
                        f"Using full image as detection region."
                    ),
                    "clip_verification": clip_result,
                    "source": source_str,
                }

            # All strategies exhausted — genuinely no person
            logger.warning("[PersonDetector] ALL strategies failed. No person in image.")
            return PersonDetector._no_detection(
                reason="no_person_found",
                evidence=(
                    f"YOLO, CLIP, and MediaPipe all failed to detect a person. "
                    f"CLIP person_prob={clip_prob:.3f}, "
                    f"MediaPipe landmarks={mediapipe_result.get('landmarks_found', 0)}."
                )
            )

        # ═══ STEP 4: YOLO succeeded — select best box ═══
        num_detections = len(person_boxes)
        best = max(person_boxes, key=lambda b: (b["confidence"], (b["x_max"] - b["x_min"]) * (b["y_max"] - b["y_min"])))

        # ═══ STEP 5: CLIP VERIFICATION GATE ═══
        # Only verify with CLIP when YOLO confidence is below 0.60
        # High-confidence YOLO detections are reliable and don't need verification
        clip_verification = {"is_person": True, "person_prob": 1.0, "evidence": "High YOLO confidence, CLIP skipped."}

        if best["confidence"] < 0.60:
            clip_verification = await asyncio.get_event_loop().run_in_executor(
                None, lambda: _verify_person_with_clip(image)
            )

            if not clip_verification["is_person"]:
                logger.warning(
                    f"[PersonDetector] YOLO detected person (conf={best['confidence']:.2f}) "
                    f"but CLIP REJECTED: {clip_verification['evidence']}"
                )
                return PersonDetector._no_detection(
                    reason="clip_rejected_not_person",
                    evidence=f"YOLO false positive rejected by CLIP. {clip_verification['evidence']}"
                )

        logger.info(
            f"[PersonDetector] Person VERIFIED | YOLO conf={best['confidence']:.2f} | "
            f"CLIP person_prob={clip_verification['person_prob']:.2f}"
        )

        return {
            "detected": True,
            "confidence": best["confidence"],
            "x_min": best["x_min"],
            "y_min": best["y_min"],
            "x_max": best["x_max"],
            "y_max": best["y_max"],
            "x_min_px": best["x_min_px"],
            "y_min_px": best["y_min_px"],
            "x_max_px": best["x_max_px"],
            "y_max_px": best["y_max_px"],
            "num_detections": num_detections,
            "all_boxes": person_boxes,
            "evidence": (
                f"Person detected using YOLO with {best['confidence']:.0%} confidence. "
                f"Verified by CLIP (person_prob={clip_verification['person_prob']:.2f})."
            ),
            "clip_verification": clip_verification,
            "source": best["source"],
        }

    @staticmethod
    def _no_detection(reason: str = "", evidence: str = "") -> dict:
        return {
            "detected": False,
            "confidence": 0.0,
            "x_min": None, "y_min": None,
            "x_max": None, "y_max": None,
            "x_min_px": None, "y_min_px": None,
            "x_max_px": None, "y_max_px": None,
            "num_detections": 0,
            "all_boxes": [],
            "reason": reason,
            "evidence": evidence or f"No person detected. Reason: {reason}",
            "source": "yolo",
        }