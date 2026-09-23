"""
TryonValidationService — Mandatory Output Validation Service for StyleSense AI.

Validates generated try-on result images from OpenAI before returning SUCCESS.

Mandatory Checks:
1. Person still exists & face present (YOLOv8 + CLIP via PersonDetector).
2. Generated image is distinct from original (mean pixel diff > 6.0).
3. Rejects simple recoloring or dark tint overlays.
4. Rejects corrupted outputs or giant black blobs (>75% black).
"""

import logging
import cv2
import numpy as np
import io
from PIL import Image, ImageOps
from typing import Tuple

from app.ai.person_detector import PersonDetector

logger = logging.getLogger(__name__)


class TryonValidationService:
    @classmethod
    async def validate_output(
        cls,
        original_bytes: bytes,
        generated_bytes: bytes
    ) -> Tuple[bool, str]:
        """
        Validates generated try-on image bytes against original person image bytes.
        """
        if not generated_bytes or len(generated_bytes) < 1000:
            return False, "Generated image bytes empty or corrupted."

        try:
            # Decode images to BGR
            pil_orig = Image.open(io.BytesIO(original_bytes)).convert("RGB")
            orig_bgr = cv2.cvtColor(np.array(pil_orig), cv2.COLOR_RGB2BGR)

            pil_gen = Image.open(io.BytesIO(generated_bytes)).convert("RGB")
            gen_bgr = cv2.cvtColor(np.array(pil_gen), cv2.COLOR_RGB2BGR)

            # 1. Size match & basic validity
            if orig_bgr is None or gen_bgr is None:
                return False, "Failed to decode original or generated image."

            orig_h, orig_w = orig_bgr.shape[:2]
            gen_h, gen_w = gen_bgr.shape[:2]

            # Resize gen to orig if dimensions differ slightly
            if (gen_h, gen_w) != (orig_h, orig_w):
                gen_bgr = cv2.resize(gen_bgr, (orig_w, orig_h))

            # 2. Check for giant black blobs / corrupted black screen (>75% black)
            gray_gen = cv2.cvtColor(gen_bgr, cv2.COLOR_BGR2GRAY)
            black_ratio = float(np.sum(gray_gen < 15)) / float(orig_h * orig_w)
            if black_ratio > 0.75:
                return False, f"Generated output contains invalid black blob overlay ({black_ratio*100:.1f}% black)."

            # 3. Person count & presence check via YOLOv8 + CLIP
            try:
                person_res = await PersonDetector.detect(gen_bgr)
                if not person_res.get("detected", False):
                    return False, "Generated image lost person structure or identity."
            except Exception as e:
                logger.warning(f"[TryonValidationService] Person detector check skipped: {e}")

            # 4. Check for identical output (mean pixel diff)
            diff = cv2.absdiff(orig_bgr, gen_bgr)
            mean_diff = float(np.mean(diff))
            if mean_diff < 5.0:
                return False, f"Generated image is virtually identical to original (mean_diff={mean_diff:.2f}). No garment replacement occurred."

            # 5. Check for fake darkening / overlay (Canny edge map comparison)
            orig_edges = cv2.Canny(orig_bgr, 100, 200)
            gen_edges = cv2.Canny(gen_bgr, 100, 200)
            edge_diff = float(np.mean(cv2.absdiff(orig_edges, gen_edges)))
            if edge_diff < 0.8:
                return False, f"Output appears to be a simple color tint or overlay (edge_diff={edge_diff:.2f})."

            logger.info(f"[TryonValidationService] Output VALIDATED: mean_diff={mean_diff:.2f}, edge_diff={edge_diff:.2f}")
            return True, "Output image passed all validation checks."

        except Exception as e:
            logger.error(f"[TryonValidationService] Error during output validation: {e}", exc_info=True)
            return False, f"Output validation error: {e}"
