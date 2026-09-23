from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from typing import List
from fastapi import UploadFile
import logging

from app.database.mongodb import get_database
from app.services.cloudinary_service import cloudinary_service
from app.ai.image_validator import ImageValidator, ImageValidationError
from app.utils.exceptions import APIException

logger = logging.getLogger(__name__)


class UploadService:

    @staticmethod
    def _format_upload_response(upload: dict) -> dict:
        upload["id"] = str(upload["_id"])
        if "format" not in upload:
            upload["format"] = "webp"
        if "size_bytes" not in upload:
            upload["size_bytes"] = 0
        return upload

    @staticmethod
    async def upload_outfit(user_id: str, file: UploadFile) -> dict:
        db = get_database()

        file_content = await file.read()
        content_type = file.content_type or "image/jpeg"

        # --- Image validation ---
        try:
            image_meta = ImageValidator.validate(file_content, content_type)
            logger.info(f"Image validated: {image_meta}")
        except ImageValidationError as e:
            raise APIException(status_code=400, detail=e.message)

        # --- Upload to Cloudinary ---
        cloudinary_data = await cloudinary_service.upload_image(
            file_content=file_content,
            content_type=content_type,
            folder=f"stylesense_outfits/{user_id}"
        )

        upload_doc = {
            "user_id": user_id,
            "image_url": cloudinary_data["secure_url"],
            "public_id": cloudinary_data["public_id"],
            "format": cloudinary_data.get("format", "webp"),
            "size_bytes": cloudinary_data.get("bytes", 0),
            "image_meta": image_meta,
            "status": "uploaded",
            "created_at": datetime.now(timezone.utc),
        }

        result = await db.uploads.insert_one(upload_doc)
        upload_doc["_id"] = result.inserted_id

        # Cache upload bytes in memory so immediate analysis skips network download
        try:
            from app.services.ml.analysis_context import cache_upload_bytes
            cache_upload_bytes(str(upload_doc["_id"]), file_content)
        except Exception as e:
            logger.warning(f"Failed to cache upload bytes in memory: {e}")

        return UploadService._format_upload_response(upload_doc)

    @staticmethod
    async def get_user_uploads(user_id: str) -> List[dict]:
        db = get_database()
        cursor = db.uploads.find({"user_id": user_id}).sort("created_at", -1)
        uploads = await cursor.to_list(length=100)
        return [UploadService._format_upload_response(u) for u in uploads]

    @staticmethod
    async def delete_upload(user_id: str, upload_id: str) -> bool:
        """
        Robust cascading delete for uploads and associated analysis/tryon jobs.
        Never fails if an associated sub-resource was already deleted.
        """
        db = get_database()
        
        # 1. Safely query upload by string or ObjectId
        query = {"user_id": user_id}
        if ObjectId.is_valid(upload_id):
            query["_id"] = ObjectId(upload_id)
        else:
            query["_id"] = upload_id

        upload = await db.uploads.find_one(query)

        # 2. Delete primary image from Cloudinary if upload exists
        if upload and upload.get("public_id"):
            try:
                await cloudinary_service.delete_image(upload["public_id"])
            except Exception as e:
                logger.warning(f"Failed to delete primary Cloudinary image {upload.get('public_id')}: {e}")

        # 3. Find and cascadingly delete associated analysis & tryon jobs
        analysis_query = {"user_id": user_id}
        if ObjectId.is_valid(upload_id):
            analysis_query["upload_id"] = ObjectId(upload_id)
        else:
            analysis_query["upload_id"] = upload_id

        analyses = await db.analysis.find(analysis_query).to_list(length=50)

        for analysis in analyses:
            analysis_id_str = str(analysis["_id"])
            # Delete tryon jobs
            try:
                tryons = await db.virtual_tryon.find({"analysis_id": analysis_id_str}).to_list(length=100)
                for t in tryons:
                    if t.get("public_id"):
                        try:
                            await cloudinary_service.delete_image(t["public_id"])
                        except Exception:
                            pass
                await db.virtual_tryon.delete_many({"analysis_id": analysis_id_str})
                await db.favorites.delete_many({"analysis_id": analysis_id_str})
            except Exception as e:
                logger.warning(f"Error cleaning tryons/favorites for analysis {analysis_id_str}: {e}")

            # Delete analysis record
            await db.analysis.delete_one({"_id": analysis["_id"]})

        # 4. Delete upload document from MongoDB if present
        if upload:
            await db.uploads.delete_one({"_id": upload["_id"]})

        logger.info(f"Cascadingly deleted upload {upload_id} and associated records.")
        return True
