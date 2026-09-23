"""
AnalysisContext & ImageCache — Shared zero-redundancy context for StyleSense AI pipeline.
"""

import cv2
import numpy as np
import httpx
import logging
import hashlib
import time
import os
import io
import base64
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

# Temporary in-memory cache for recent image uploads (upload_id -> bytes)
# Expires after 10 minutes
_UPLOAD_BYTES_CACHE: Dict[str, Tuple[bytes, float]] = {}
MAX_CACHE_AGE_SECONDS = 600
MAX_ML_IMAGE_DIM = 1280


def cache_upload_bytes(upload_id: str, raw_bytes: bytes):
    """Caches upload bytes in memory to avoid immediate Cloudinary re-download."""
    _cleanup_old_cache()
    _UPLOAD_BYTES_CACHE[str(upload_id)] = (raw_bytes, time.time())
    logger.debug(f"[ImageCache] Cached {len(raw_bytes)} bytes for upload {upload_id}")


def get_cached_upload_bytes(upload_id: str) -> Optional[bytes]:
    """Retrieves cached upload bytes if available and fresh."""
    _cleanup_old_cache()
    entry = _UPLOAD_BYTES_CACHE.get(str(upload_id))
    if entry:
        return entry[0]
    return None


def _cleanup_old_cache():
    now = time.time()
    expired = [k for k, (_, t) in _UPLOAD_BYTES_CACHE.items() if now - t > MAX_CACHE_AGE_SECONDS]
    for k in expired:
        _UPLOAD_BYTES_CACHE.pop(k, None)


@dataclass
class AnalysisContext:
    upload_id: str
    image_url: str
    raw_bytes: bytes
    image_hash: str
    original_w: int
    original_h: int
    scale_factor: float
    image_bgr: np.ndarray
    image_rgb: np.ndarray

    # Detection & pipeline states (filled during pipeline)
    person_detection: Optional[Dict[str, Any]] = None
    pose: Optional[Dict[str, Any]] = None
    segmentation: Optional[Dict[str, Any]] = None
    crops: Dict[str, np.ndarray] = field(default_factory=dict)
    masks: Dict[str, np.ndarray] = field(default_factory=dict)
    regions: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    async def create(cls, upload_id: str, image_url: str, override_bytes: Optional[bytes] = None) -> "AnalysisContext":
        """
        Fetches image bytes once, computes hash, and creates optimized ML arrays.
        """
        raw_bytes = override_bytes

        # 1. Check in-memory upload cache
        if raw_bytes is None and upload_id:
            raw_bytes = get_cached_upload_bytes(upload_id)
            if raw_bytes:
                logger.info(f"[AnalysisContext] Using in-memory cached bytes for upload {upload_id}")

        # 2. Fetch from source if not cached
        if raw_bytes is None:
            if isinstance(image_url, bytes):
                raw_bytes = image_url
            elif str(image_url).startswith("data:image"):
                _, base64_data = str(image_url).split(",", 1)
                raw_bytes = base64.b64decode(base64_data)
            elif isinstance(image_url, str) and os.path.exists(image_url):
                with open(image_url, "rb") as f:
                    raw_bytes = f.read()
            else:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=headers) as client:
                    resp = await client.get(str(image_url))
                    resp.raise_for_status()
                    raw_bytes = resp.content

        # 3. Compute deterministic hash
        image_hash = hashlib.sha256(raw_bytes).hexdigest()

        # 4. Decode once with EXIF auto-rotation
        pil_img = Image.open(io.BytesIO(raw_bytes))
        pil_img = ImageOps.exif_transpose(pil_img).convert("RGB")
        orig_w, orig_h = pil_img.size

        # 5. Optimize resolution for ML copy (max 1280px)
        scale_factor = 1.0
        max_dim = max(orig_w, orig_h)
        if max_dim > MAX_ML_IMAGE_DIM:
            scale_factor = MAX_ML_IMAGE_DIM / float(max_dim)
            new_w = max(1, int(orig_w * scale_factor))
            new_h = max(1, int(orig_h * scale_factor))
            pil_img_ml = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
            logger.info(f"[AnalysisContext] Resized ML copy from {orig_w}x{orig_h} to {new_w}x{new_h} (scale={scale_factor:.3f})")
        else:
            pil_img_ml = pil_img

        image_rgb = np.array(pil_img_ml)
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        return cls(
            upload_id=upload_id,
            image_url=image_url,
            raw_bytes=raw_bytes,
            image_hash=image_hash,
            original_w=orig_w,
            original_h=orig_h,
            scale_factor=scale_factor,
            image_bgr=image_bgr,
            image_rgb=image_rgb,
        )
