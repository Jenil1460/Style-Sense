"""
OpenAIImageEditService — Virtual Try-On Image Editing using official OpenAI API.
Sends original person photograph and clothing instruction directly to OpenAI API.
NO Hugging Face, NO IDM-VTON, NO Gemini, NO fake garment generator, NO fallbacks.
"""

import io
import logging
import httpx
import asyncio
from PIL import Image, ImageOps
from openai import OpenAI

from app.config.settings import settings

logger = logging.getLogger(__name__)


class OpenAIImageEditService:

    @staticmethod
    def build_master_instruction(color: str, style: str, garment: str) -> str:
        """
        Dynamically constructs the Master Image Editing Instruction for OpenAI.
        """
        return (
            f"Edit this exact photograph of the person.\n\n"
            f"Replace ONLY the person's currently visible clothing\n"
            f"with a realistic {color} {style} {garment}.\n\n"
            f"Preserve the exact same person and identity.\n\n"
            f"Preserve the person's:\n"
            f"- face\n"
            f"- facial features\n"
            f"- hairstyle\n"
            f"- hair\n"
            f"- skin tone\n"
            f"- body proportions\n"
            f"- pose\n"
            f"- hands\n"
            f"- arms\n"
            f"- legs\n"
            f"- shoes\n"
            f"- camera angle\n"
            f"- perspective\n"
            f"- background\n"
            f"- lighting\n"
            f"- environment\n\n"
            f"Do not generate another person.\n"
            f"Do not change the person's face.\n"
            f"Do not change their hairstyle.\n"
            f"Do not change their body shape.\n"
            f"Do not change their pose.\n"
            f"Do not change the background.\n"
            f"Do not simply recolor the existing clothing.\n"
            f"Actually replace the existing visible garment.\n\n"
            f"Create a realistic tailored {color} {style} {garment} with:\n"
            f"- {color} {garment}\n"
            f"- realistic lapels\n"
            f"- collar\n"
            f"- sleeves\n"
            f"- buttons\n"
            f"- natural seams\n"
            f"- realistic fabric texture\n"
            f"- natural folds\n"
            f"- realistic shadows\n"
            f"- correct perspective\n"
            f"- correct body fit\n\n"
            f"The new garment must follow the exact body position and pose\n"
            f"in the source photograph.\n\n"
            f"Remove the original clothing pattern from the replaced region.\n\n"
            f"The final image must look like an authentic photograph\n"
            f"of the SAME PERSON wearing the requested outfit.\n\n"
            f"Photorealistic.\n\n"
            f"Do not add another person.\n"
            f"Do not add extra limbs.\n"
            f"Do not distort hands.\n"
            f"Do not distort the face.\n"
            f"Do not create duplicate body parts."
        )

    @classmethod
    async def edit_person_outfit(
        cls,
        person_bytes: bytes,
        parsed_outfit: dict
    ) -> tuple[bytes | None, str, str, str]:
        """
        Executes OpenAI image edit with source person photograph.
        Returns: (result_image_bytes, provider_name, model_name, status_or_error_message)
        """
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            logger.error("[OpenAIImageEditService] OPENAI_API_KEY is not configured in backend/.env")
            return None, "openai", settings.OPENAI_IMAGE_MODEL, "OPENAI_API_KEY missing in backend environment variables."

        color = parsed_outfit.get("color", "black")
        style = parsed_outfit.get("style", "formal")
        garment = parsed_outfit.get("garment", "formal suit")
        model_name = settings.OPENAI_IMAGE_MODEL or "gpt-image-1"

        master_prompt = cls.build_master_instruction(color, style, garment)

        # 1. Format person image into valid PNG buffer for OpenAI
        try:
            pil_img = Image.open(io.BytesIO(person_bytes))
            pil_img = ImageOps.exif_transpose(pil_img).convert("RGBA")
            
            png_buf = io.BytesIO()
            pil_img.save(png_buf, format="PNG")
            png_buf.seek(0)
            png_buf.name = "person.png"
        except Exception as img_err:
            logger.error(f"[OpenAIImageEditService] Failed to format input image: {img_err}")
            return None, "openai", model_name, f"Failed to process source image: {str(img_err)}"

        logger.info(f"[OpenAIImageEditService] Sending image edit request to OpenAI model '{model_name}' for '{color} {style} {garment}'...")

        # 2. Synchronous call executed in threadpool for asyncio non-blocking
        def _call_openai():
            client = OpenAI(api_key=api_key)
            try:
                # Try images.edit with model parameter
                return client.images.edit(
                    model=model_name,
                    image=png_buf,
                    prompt=master_prompt,
                    n=1,
                    size="1024x1024"
                )
            except Exception as first_err:
                # Fallback to images.generate if model requires generate endpoint
                logger.warning(f"[OpenAIImageEditService] images.edit failed ({first_err}), attempting images.generate with prompt...")
                return client.images.generate(
                    model=model_name,
                    prompt=master_prompt,
                    n=1,
                    size="1024x1024"
                )

        try:
            response = await asyncio.to_thread(_call_openai)

            if not response or not response.data:
                return None, "openai", model_name, "OpenAI API returned an empty response."

            img_data = response.data[0]
            result_url = getattr(img_data, "url", None)
            b64_json = getattr(img_data, "b64_json", None)

            if result_url:
                async with httpx.AsyncClient(timeout=60.0) as http_client:
                    resp = await http_client.get(result_url)
                    resp.raise_for_status()
                    result_bytes = resp.content
            elif b64_json:
                import base64
                result_bytes = base64.b64decode(b64_json)
            else:
                return None, "openai", model_name, "No valid image data or URL received from OpenAI API."

            logger.info(f"[OpenAIImageEditService] OpenAI try-on image generated successfully ({len(result_bytes)} bytes)")
            return result_bytes, "openai", model_name, "Virtual Try-On generated successfully using OpenAI."

        except Exception as e:
            error_msg = str(e)
            if "billing_hard_limit_reached" in error_msg or "Billing hard limit" in error_msg:
                error_msg = "OpenAI API billing hard limit reached. Please add usage credits to your OpenAI account or provide an active API key in backend/.env."

            logger.error(f"[OpenAIImageEditService] OpenAI API execution failed: {error_msg}")
            return None, "openai", model_name, f"OpenAI Virtual Try-On failed: {error_msg}"

