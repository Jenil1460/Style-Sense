import logging
from PIL import Image, ImageOps
import io
import numpy as np
import cv2

logger = logging.getLogger(__name__)

ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
MIN_RESOLUTION = (100, 100)
MIN_BRIGHTNESS = 20
MAX_BRIGHTNESS = 245
MIN_BLUR_VARIANCE = 50.0

class ImageValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class ImageValidator:
    @staticmethod
    def validate(file_content: bytes, content_type: str) -> dict:
        if not file_content or len(file_content) == 0:
            raise ImageValidationError("Image file is empty or missing.")

        # 1. File type check
        if content_type and content_type.lower() not in ALLOWED_TYPES:
            raise ImageValidationError(
                f"Unsupported file type '{content_type}'. Allowed types: JPEG, PNG, WEBP."
            )

        # 2. File size check
        size_mb = len(file_content) / (1024 * 1024)
        if len(file_content) > MAX_SIZE_BYTES:
            raise ImageValidationError(
                f"File size {size_mb:.1f}MB exceeds the 10MB limit."
            )

        # 3. Attempt to open with Pillow & verify integrity
        try:
            img_raw = Image.open(io.BytesIO(file_content))
            img_raw.verify()
        except Exception:
            raise ImageValidationError("The uploaded file is corrupted or not a valid image.")

        # 4. Re-open to read data and auto-rotate via EXIF if available
        try:
            img = Image.open(io.BytesIO(file_content))
            img = ImageOps.exif_transpose(img).convert("RGB")
        except Exception:
            raise ImageValidationError("Could not read image data.")

        # 5. Minimum resolution check
        width, height = img.size
        if width < MIN_RESOLUTION[0] or height < MIN_RESOLUTION[1]:
            raise ImageValidationError(
                f"Image resolution {width}x{height} is too small. Minimum resolution is {MIN_RESOLUTION[0]}x{MIN_RESOLUTION[1]}."
            )

        # 6. Brightness check
        img_array = np.array(img)
        avg_brightness = float(img_array.mean())
        if avg_brightness < MIN_BRIGHTNESS:
            raise ImageValidationError(
                f"Image is too dark for analysis (brightness score: {avg_brightness:.1f}). Please upload a well-lit photo."
            )
        if avg_brightness > MAX_BRIGHTNESS:
            raise ImageValidationError(
                f"Image is overexposed (brightness score: {avg_brightness:.1f}). Please upload a properly lit photo."
            )

        # 7. Blur/sharpness check using Laplacian variance
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if blur_score < MIN_BLUR_VARIANCE:
            raise ImageValidationError(
                f"Image appears blurry (sharpness score: {blur_score:.1f}). Please upload a clearer photo."
            )

        logger.info(f"[ImageValidator] Validated: {width}x{height}, brightness={avg_brightness:.1f}, sharpness={blur_score:.1f}")

        return {
            "valid": True,
            "width": width,
            "height": height,
            "brightness": round(avg_brightness, 2),
            "sharpness": round(blur_score, 2),
            "size_bytes": len(file_content),
            "format": img.format or "RGB",
        }

