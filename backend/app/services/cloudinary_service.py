import asyncio
import logging
import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Dict, Any, Optional
from app.config.settings import settings
from app.utils.exceptions import APIException

logger = logging.getLogger(__name__)

class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )

    def _validate_image(self, file_content: bytes, content_type: str):
        """Validate image size and type."""
        # Check size
        if len(file_content) > settings.MAX_UPLOAD_SIZE:
            raise APIException(400, f"File size exceeds the {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB limit.")
        
        # Check MIME type
        if content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise APIException(400, f"File type {content_type} is not allowed. Supported types: {', '.join(settings.ALLOWED_IMAGE_TYPES)}")

    async def upload_image(self, file_content: bytes, content_type: str, folder: str = "stylesense_uploads") -> Dict[str, Any]:
        """
        Uploads, validates, compresses, and optimizes an image to Cloudinary asynchronously.
        Returns the secure URL and public_id.
        """
        self._validate_image(file_content, content_type)

        def _upload():
            return cloudinary.uploader.upload(
                file_content,
                folder=folder,
                resource_type="image",
                # Optimization and Compression transformations
                format="webp", # Auto-convert to webp
                quality="auto", # Auto-compress without visible quality loss
                fetch_format="auto" # Deliver best format to browser
            )
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, _upload)
            logger.info(f"Successfully uploaded image to Cloudinary: {response.get('public_id')}")
            return {
                "secure_url": response.get("secure_url"),
                "public_id": response.get("public_id"),
                "format": response.get("format"),
                "bytes": response.get("bytes")
            }
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            raise APIException(500, "Failed to upload image.")

    async def delete_image(self, public_id: str) -> bool:
        """Deletes an image from Cloudinary asynchronously."""
        def _delete():
            return cloudinary.uploader.destroy(public_id)
            
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, _delete)
            success = result.get('result') == 'ok'
            if success:
                logger.info(f"Deleted image from Cloudinary: {public_id}")
            return success
        except Exception as e:
            logger.error(f"Cloudinary delete failed for {public_id}: {e}")
            return False

    async def replace_image(self, file_content: bytes, content_type: str, old_public_id: Optional[str], folder: str = "stylesense_uploads") -> Dict[str, Any]:
        """Uploads a new image and deletes the old one if it exists."""
        # Upload new image first
        new_image_data = await self.upload_image(file_content, content_type, folder)
        
        # Then delete old image asynchronously in background (fire and forget)
        if old_public_id:
            asyncio.create_task(self.delete_image(old_public_id))
            
        return new_image_data

cloudinary_service = CloudinaryService()
