"""
TryonEngine — Hugging Face IDM-VTON Virtual Try-On Pipeline for StyleSense AI.

Flow:
1. Receive Original Person Image + Outfit Text Prompt ("wear black suit").
2. OutfitPromptParser normalizes text and extracts garment, color, style, target.
3. GarmentSynthesisService creates/formats realistic garment reference image for IDM-VTON.
4. HFIDMVtonService sends person image + garment reference image to Hugging Face yisol/IDM-VTON space.
5. TryonValidationService verifies generated image validity, presence of person, and non-identical diff.
6. Result image uploaded to Cloudinary.
7. Returns normalized TryOn result object with provider="huggingface".
"""

import logging
import cv2
import numpy as np
import httpx
import io
import base64
import time
from PIL import Image, ImageOps

from app.config.settings import settings
from app.ai.person_detector import PersonDetector
from app.ai.outfit_prompt_parser import OutfitPromptParser
from app.services.ml.hf_idm_vton_service import HFIDMVtonService
from app.services.ml.tryon_validation_service import TryonValidationService
from app.services.cloudinary_service import cloudinary_service

logger = logging.getLogger(__name__)


class TryonEngineNotReady(Exception):
    pass


class TryonEngine:
    MODEL_READY = True

    @staticmethod
    async def _fetch_image_bytes(image_url: str) -> tuple[bytes, str]:
        """Fetch image bytes and determine mime type."""
        if not image_url:
            return None, "image/jpeg"

        if image_url.startswith("data:image"):
            header, base64_data = image_url.split(",", 1)
            mime_type = header.split(";")[0].replace("data:", "") or "image/jpeg"
            return base64.b64decode(base64_data), mime_type
        else:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(image_url)
                resp.raise_for_status()
                content_type = resp.headers.get("content-type", "image/jpeg").split(";")[0]
                return resp.content, content_type

    @classmethod
    async def generate(
        cls,
        source_image_url: str,
        outfit_description: str,
        person_bytes: bytes = None
    ) -> dict:
        """
        Master Virtual Try-On Entrypoint powered exclusively by Hugging Face IDM-VTON API.
        """
        start_time = time.time()
        logger.info(f"[TryonEngine] Starting Hugging Face IDM-VTON Virtual Try-On generation for outfit: '{outfit_description}'")

        if not outfit_description or not outfit_description.strip():
            return {
                "success": False,
                "provider": "huggingface",
                "stage": "validation",
                "error": "Please enter an outfit prompt (e.g. 'wear black suit').",
                "message": "Please enter an outfit prompt."
            }

        # ── 1. Fetch / Decode Original Person Image ──
        if not person_bytes:
            try:
                person_bytes, _ = await cls._fetch_image_bytes(source_image_url)
            except Exception as e:
                logger.error(f"[TryonEngine] Failed to fetch source person image: {e}")
                return {
                    "success": False,
                    "provider": "huggingface",
                    "stage": "image_fetch",
                    "error": f"Unable to fetch person image: {str(e)}",
                    "message": "Virtual try-on requires a valid image of a person."
                }

        if not person_bytes:
            return {
                "success": False,
                "provider": "huggingface",
                "stage": "image_fetch",
                "error": "Person image content is empty.",
                "message": "Virtual try-on requires a clear image of a person."
            }

        try:
            person_result = await PersonDetector.detect(source_image_url or person_bytes)
            if not person_result.get("detected", False):
                logger.warning("[TryonEngine] PersonDetector did not detect a person in the uploaded image.")
        except Exception as e:
            logger.warning(f"[TryonEngine] Person detection check non-blocking warning: {e}")

        # ── 2. Parse & Normalize Outfit Prompt ──
        parsed_outfit = OutfitPromptParser.parse(outfit_description)
        normalized_outfit_dict = {
            "garment": parsed_outfit["garment"],
            "color": parsed_outfit["color"],
            "style": parsed_outfit["style"],
            "target": parsed_outfit["target"]
        }

        # ── 3. Call Hugging Face IDM-VTON Service ──
        res_bytes, provider, model_name, status_msg = await HFIDMVtonService.tryon(
            person_bytes=person_bytes,
            parsed_outfit=parsed_outfit
        )

        if not res_bytes:
            return {
                "success": False,
                "provider": provider,
                "model": model_name,
                "stage": "hf_vton_generation",
                "error": status_msg,
                "message": status_msg
            }

        # ── 4. Validate Generated Output Image ──
        is_valid, val_reason = await TryonValidationService.validate_output(person_bytes, res_bytes)
        if not is_valid:
            logger.error(f"[TryonEngine] Output validation failed: {val_reason}")
            return {
                "success": False,
                "provider": provider,
                "model": model_name,
                "stage": "result_validation",
                "error": f"Result validation failed: {val_reason}",
                "message": val_reason
            }

        # ── 5. Upload Generated Image to Cloudinary ──
        try:
            up_res = await cloudinary_service.upload_image(res_bytes, "image/jpeg", folder="stylesense/tryon")
            generated_url = up_res.get("secure_url")
        except Exception as up_err:
            logger.error(f"[TryonEngine] Cloudinary upload of generated image failed: {up_err}")
            return {
                "success": False,
                "provider": provider,
                "model": model_name,
                "stage": "cloudinary_upload",
                "error": f"Failed to upload generated result image: {str(up_err)}",
                "message": "Cloudinary upload failed."
            }

        gen_time = f"{time.time() - start_time:.2f}s"

        return {
            "success": True,
            "provider": provider,
            "model": model_name,
            "original_image_url": source_image_url,
            "generated_image_url": generated_url,
            "outfit_prompt": outfit_description,
            "normalized_outfit": normalized_outfit_dict,
            "generation_time": gen_time,
            "status": "completed",
            "message": "Virtual try-on completed successfully using Hugging Face IDM-VTON."
        }
