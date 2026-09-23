import logging
from datetime import datetime, timezone
from bson import ObjectId
from typing import List, Optional
from fastapi import UploadFile

from app.database.mongodb import get_database
from app.services.cloudinary_service import cloudinary_service
from app.services.ml.tryon_engine import TryonEngine
from app.utils.exceptions import APIException

logger = logging.getLogger(__name__)


class VirtualTryonService:

    @staticmethod
    def _fmt(doc: dict) -> dict:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        return doc

    @classmethod
    async def create_tryon_job(
        cls,
        user_id: str,
        outfit_prompt: str,
        image_file: Optional[UploadFile] = None,
        person_image_url: Optional[str] = None,
        analysis_id: Optional[str] = None,
    ) -> dict:
        """
        Processes OpenAI Virtual Try-On request and stores results in MongoDB & Cloudinary.
        """
        db = get_database()

        image_bytes: Optional[bytes] = None
        source_url = person_image_url

        # 1. If UploadFile provided, read bytes and upload original photo to Cloudinary
        if image_file:
            try:
                image_bytes = await image_file.read()
                if image_bytes:
                    content_type = image_file.content_type or "image/jpeg"
                    cloud_res = await cloudinary_service.upload_image(
                        image_bytes,
                        content_type,
                        folder="stylesense/original_persons"
                    )
                    source_url = cloud_res.get("secure_url")
            except Exception as e:
                logger.error(f"[VirtualTryonService] Failed to read/upload input person image: {e}")
                return {
                    "success": False,
                    "provider": "openai",
                    "stage": "image_upload",
                    "error": f"Failed to upload original image: {str(e)}"
                }

        # 2. If no direct image provided, fallback to analysis image if available
        if not source_url and analysis_id:
            try:
                analysis = await db.analysis.find_one({
                    "_id": ObjectId(analysis_id),
                    "user_id": user_id
                })
                if analysis:
                    source_url = analysis.get("image_url")
            except Exception as e:
                logger.warning(f"Failed to fetch analysis {analysis_id}: {e}")

        if not source_url and not image_bytes:
            return {
                "success": False,
                "provider": "openai",
                "stage": "validation",
                "error": "Virtual try-on requires a clear photograph of a person."
            }

        # 3. Call TryonEngine (OpenAI Pipeline)
        tryon_res = await TryonEngine.generate(
            source_image_url=source_url,
            outfit_description=outfit_prompt,
            person_bytes=image_bytes
        )

        is_success = tryon_res.get("success", False)

        if is_success:
            job_doc = {
                "user_id": user_id,
                "analysis_id": ObjectId(analysis_id) if analysis_id and ObjectId.is_valid(analysis_id) else None,
                "original_image_url": tryon_res.get("original_image_url") or source_url,
                "generated_image_url": tryon_res.get("generated_image_url"),
                "outfit_prompt": outfit_prompt,
                "normalized_outfit": tryon_res.get("normalized_outfit"),
                "provider": "huggingface",
                "model": tryon_res.get("model", "yisol/IDM-VTON"),
                "status": "completed",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

            result = await db.virtual_tryon.insert_one(job_doc)
            logger.info(f"Virtual try-on completed for user {user_id}, doc_id={result.inserted_id}")

            return {
                "success": True,
                "provider": "huggingface",
                "model": tryon_res.get("model", "yisol/IDM-VTON"),
                "original_image_url": tryon_res.get("original_image_url") or source_url,
                "generated_image_url": tryon_res.get("generated_image_url"),
                "outfit_prompt": outfit_prompt,
                "normalized_outfit": tryon_res.get("normalized_outfit")
            }
        else:
            stage = tryon_res.get("stage", "generation")
            error_msg = tryon_res.get("error") or tryon_res.get("message") or "Generation failed"
            
            # Log real backend error
            logger.error(f"[VirtualTryonService] Try-on failed at stage '{stage}': {error_msg}")

            failed_doc = {
                "user_id": user_id,
                "original_image_url": source_url,
                "outfit_prompt": outfit_prompt,
                "provider": "huggingface",
                "status": "failed",
                "stage": stage,
                "error": error_msg,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            await db.virtual_tryon.insert_one(failed_doc)

            return {
                "success": False,
                "provider": "huggingface",
                "stage": stage,
                "error": error_msg
            }


    @staticmethod
    async def get_history(user_id: str) -> List[dict]:
        db = get_database()
        cursor = db.virtual_tryon.find({"user_id": user_id}).sort("created_at", -1)
        jobs = await cursor.to_list(length=50)
        return [VirtualTryonService._fmt(j) for j in jobs]

    @staticmethod
    async def delete_job(user_id: str, job_id: str) -> bool:
        db = get_database()
        job = await db.virtual_tryon.find_one({
            "_id": ObjectId(job_id),
            "user_id": user_id
        })
        if not job:
            raise APIException(status_code=404, detail="Job not found.")

        await db.virtual_tryon.delete_one({"_id": ObjectId(job_id)})
        return True
