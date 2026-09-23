from fastapi import APIRouter, Depends, UploadFile, File
from app.dependencies.auth import get_current_active_user
from app.schemas.user import UserResponse
from app.schemas.profile import ProfileUpdate, UpdatePasswordRequest
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_active_user)):
    """Retrieve the current user's complete profile."""
    return await ProfileService.get_profile(current_user["id"])

@router.put("/", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdate, 
    current_user: dict = Depends(get_current_active_user)
):
    """Update the current user's profile details."""
    return await ProfileService.update_profile(current_user["id"], profile_data)

@router.put("/password")
async def update_password(
    password_data: UpdatePasswordRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Securely update the user's password."""
    await ProfileService.update_password(current_user["id"], password_data)
    return {"success": True, "message": "Password updated successfully"}

@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user)
):
    """Upload or replace the user's avatar image."""
    return await ProfileService.upload_avatar(current_user["id"], file)

@router.delete("/avatar", response_model=UserResponse)
async def delete_avatar(current_user: dict = Depends(get_current_active_user)):
    """Delete the user's avatar image and revert to default."""
    return await ProfileService.delete_avatar(current_user["id"])
