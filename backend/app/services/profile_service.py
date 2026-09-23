from datetime import datetime, timezone
from bson import ObjectId
from fastapi import UploadFile

from app.database.mongodb import get_database
from app.auth.hash import get_password_hash, verify_password
from app.schemas.profile import ProfileUpdate, UpdatePasswordRequest
from app.services.cloudinary_service import cloudinary_service
from app.utils.exceptions import APIException

class ProfileService:
    
    @staticmethod
    def _format_user_response(user: dict) -> dict:
        user["id"] = str(user["_id"])
        return user

    @staticmethod
    async def get_profile(user_id: str) -> dict:
        db = get_database()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise APIException(status_code=404, detail="User not found")
        return ProfileService._format_user_response(user)

    @staticmethod
    async def update_profile(user_id: str, profile_data: ProfileUpdate) -> dict:
        db = get_database()
        
        # Filter out None values to only update provided fields
        update_data = {k: v for k, v in profile_data.model_dump().items() if v is not None}
        
        if not update_data:
            return await ProfileService.get_profile(user_id)
            
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        return await ProfileService.get_profile(user_id)

    @staticmethod
    async def update_password(user_id: str, password_data: UpdatePasswordRequest) -> bool:
        db = get_database()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not verify_password(password_data.current_password, user.get("hashed_password", "")):
            raise APIException(status_code=400, detail="Incorrect current password")
            
        hashed_password = get_password_hash(password_data.new_password)
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "hashed_password": hashed_password,
                    "updated_at": datetime.now(timezone.utc)
                },
                "$unset": {"refresh_token": ""} # Invalidate sessions
            }
        )
        return True

    @staticmethod
    async def upload_avatar(user_id: str, file: UploadFile) -> dict:
        db = get_database()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        old_public_id = user.get("avatar_public_id")
        
        # Read file into memory
        file_content = await file.read()
        
        # Upload using our cloudinary service
        upload_result = await cloudinary_service.replace_image(
            file_content=file_content,
            content_type=file.content_type,
            old_public_id=old_public_id,
            folder="stylesense_avatars"
        )
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "avatar_url": upload_result["secure_url"],
                "avatar_public_id": upload_result["public_id"],
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        return await ProfileService.get_profile(user_id)

    @staticmethod
    async def delete_avatar(user_id: str) -> dict:
        db = get_database()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        old_public_id = user.get("avatar_public_id")
        
        if old_public_id:
            # Delete from Cloudinary
            await cloudinary_service.delete_image(old_public_id)
            
            # Remove from DB
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$unset": {"avatar_url": "", "avatar_public_id": ""},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
            
        return await ProfileService.get_profile(user_id)
