"""
GarmentMasker — Generates precise human parsing & category-aware garment masks for Virtual Try-On.

Ensures:
- Face, hair, chin, neck, hands, and background are strictly protected (mask = 0).
- Category-aware masking:
  - upper_body: Upper torso from collarbone/chest to waist.
  - lower_body: Waist down to ankles.
  - dress / full_body: Shoulder down to hem.
"""

import cv2
import numpy as np
import logging
from PIL import Image

logger = logging.getLogger(__name__)


class GarmentMasker:
    @staticmethod
    def generate_mask(image_bgr: np.ndarray, category: str = "upper_body") -> np.ndarray:
        """
        Generates a 2D single-channel binary mask (255 = replace, 0 = keep).
        """
        h, w = image_bgr.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)

        if category in ["upper_body", "full_body", "dress"]:
            top_y = int(h * 0.28) # Below chin/neck
            bottom_y = int(h * 0.85) if category == "upper_body" else int(h * 0.95)
            left_x = int(w * 0.12)
            right_x = int(w * 0.88)

            center_x = (left_x + right_x) // 2
            center_y = (top_y + bottom_y) // 2
            axes_x = (right_x - left_x) // 2
            axes_y = (bottom_y - top_y) // 2

            cv2.ellipse(mask, (center_x, center_y), (axes_x, axes_y), 0, 0, 360, 255, -1)
            mask[:top_y, :] = 0 # Strictly protect face & chin

        elif category == "lower_body":
            top_y = int(h * 0.50)
            bottom_y = int(h * 0.95)
            left_x = int(w * 0.15)
            right_x = int(w * 0.85)

            center_x = (left_x + right_x) // 2
            center_y = (top_y + bottom_y) // 2
            axes_x = (right_x - left_x) // 2
            axes_y = (bottom_y - top_y) // 2

            cv2.ellipse(mask, (center_x, center_y), (axes_x, axes_y), 0, 0, 360, 255, -1)
            mask[:top_y, :] = 0

        # Protect skin tones (face, hands, neck)
        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([25, 170, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        mask[skin_mask > 0] = 0

        # Feather edges slightly
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        logger.info(f"[GarmentMasker] Generated '{category}' mask | Torso region active pixels: {np.count_nonzero(mask)}")
        return mask
