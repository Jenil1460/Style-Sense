from fastapi import APIRouter, Depends, UploadFile, File
from typing import List
from app.dependencies.auth import get_current_active_user
from app.schemas.upload import UploadResponse
from app.services.upload_service import UploadService

router = APIRouter(prefix="/uploads", tags=["Uploads"])

@router.post("/image", response_model=UploadResponse)
async def upload_image_endpoint(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user)
):
    """Uploads an outfit image, compresses it, and saves metadata."""
    return await UploadService.upload_outfit(current_user["id"], file)

@router.get("/", response_model=List[UploadResponse])
async def list_user_uploads(current_user: dict = Depends(get_current_active_user)):
    """Retrieves all previous outfit uploads for the current user."""
    return await UploadService.get_user_uploads(current_user["id"])

@router.delete("/{upload_id}")
async def delete_upload(
    upload_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Deletes a specific upload from both Cloudinary and MongoDB."""
    await UploadService.delete_upload(current_user["id"], upload_id)
    return {"success": True, "message": "Upload successfully deleted"}
