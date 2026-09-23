"""
Hugging Face IDM-VTON Virtual Try-On Service.
Runs Hugging Face yisol/IDM-VTON Gradio Client space (yisol-idm-vton.hf.space).
Uses Hugging Face HF_TOKEN / HF_API_KEY from backend environment.
"""

import io
import time
import logging
import asyncio
import httpx
from PIL import Image, ImageOps
from gradio_client import Client, handle_file

from app.config.settings import settings
from app.services.ml.garment_synthesis_service import GarmentSynthesisService

logger = logging.getLogger(__name__)


class HFIDMVtonService:
    @classmethod
    async def tryon(
        cls,
        person_bytes: bytes,
        parsed_outfit: dict,
        garment_bytes: bytes = None
    ) -> tuple[bytes | None, str, str, str]:
        """
        Executes Hugging Face yisol/IDM-VTON Virtual Try-On space.
        Returns: (result_image_bytes, provider_name, model_name, status_message)
        """
        hf_token = settings.hf_auth_token
        model_name = settings.HF_VTON_MODEL or "yisol/IDM-VTON"

        color = parsed_outfit.get("color", "black")
        style = parsed_outfit.get("style", "formal")
        garment = parsed_outfit.get("garment", "formal suit")
        clean_desc = parsed_outfit.get("cleanDescription", f"{color} {style} {garment}")

        logger.info(f"[HFIDMVtonService] Starting HuggingFace IDM-VTON Virtual Try-On for '{clean_desc}'...")

        # 1. Prepare Person Image File
        try:
            pil_person = Image.open(io.BytesIO(person_bytes))
            pil_person = ImageOps.exif_transpose(pil_person).convert("RGB")
            
            # Save person image to temporary buffer file
            person_buf = io.BytesIO()
            pil_person.save(person_buf, format="JPEG", quality=95)
            person_buf.seek(0)
            person_path = "temp_person.jpg"
            with open(person_path, "wb") as f:
                f.write(person_buf.getvalue())
        except Exception as p_err:
            logger.error(f"[HFIDMVtonService] Failed to process person image: {p_err}")
            return None, "huggingface", model_name, f"Failed to process person photo: {str(p_err)}"

        # 2. Prepare Garment Reference Image File
        try:
            if not garment_bytes:
                garment_bytes = GarmentSynthesisService.generate_garment_reference(color, garment, style)
            
            pil_garment = Image.open(io.BytesIO(garment_bytes)).convert("RGB")
            garment_path = "temp_garment.jpg"
            with open(garment_path, "wb") as f:
                pil_garment.save(f, format="JPEG", quality=95)
        except Exception as g_err:
            logger.error(f"[HFIDMVtonService] Failed to prepare garment reference image: {g_err}")
            return None, "huggingface", model_name, f"Failed to prepare garment image: {str(g_err)}"

        # 3. Call HuggingFace yisol/IDM-VTON Gradio Client
        def _call_gradio():
            client = Client("yisol/IDM-VTON", token=hf_token if hf_token else None)
            
            editor_data = {
                "background": handle_file(person_path),
                "layers": [],
                "composite": None
            }
            
            result = client.predict(
                dict=editor_data,
                garm_img=handle_file(garment_path),
                garment_des=clean_desc,
                is_checked=True,
                is_checked_crop=False,
                denoise_steps=30,
                seed=42,
                api_name="/tryon"
            )
            return result

        try:
            result = await asyncio.to_thread(_call_gradio)
            
            # Extract result file path from Gradio return tuple (output, masked_image_output)
            output_file_path = None
            if isinstance(result, (list, tuple)) and len(result) > 0:
                output_file_path = result[0]
            elif isinstance(result, str):
                output_file_path = result
            elif isinstance(result, dict) and "path" in result:
                output_file_path = result["path"]

            if not output_file_path:
                return None, "huggingface", model_name, "Hugging Face IDM-VTON returned empty image result."

            # Read result file bytes
            if isinstance(output_file_path, dict) and "path" in output_file_path:
                output_file_path = output_file_path["path"]

            with open(output_file_path, "rb") as rf:
                result_bytes = rf.read()

            logger.info(f"[HFIDMVtonService] Hugging Face IDM-VTON SUCCESS ({len(result_bytes)} bytes)!")
            return result_bytes, "huggingface", model_name, "Virtual Try-On generated successfully using Hugging Face IDM-VTON."

        except Exception as hf_err:
            err_msg = str(hf_err)
            logger.error(f"[HFIDMVtonService] Hugging Face Gradio client call failed: {err_msg}")
            
            if "ZeroGPU" in err_msg or "quota" in err_msg or "queue" in err_msg:
                err_msg = "Hugging Face space is currently busy or GPU limit reached. Please try again in a few moments."
            
            return None, "huggingface", model_name, f"Hugging Face Try-On failed: {err_msg}"
