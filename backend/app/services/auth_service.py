import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from bson import ObjectId
from fastapi import HTTPException, status

from app.database.mongodb import get_database
from app.auth.hash import get_password_hash, verify_password
from app.auth.jwt import create_access_token
from app.config.settings import settings
from app.schemas.user import UserCreate, UserLogin, ResetPasswordRequest
from app.utils.exceptions import APIException

class AuthService:
    
    @staticmethod
    def _create_refresh_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def _format_user_response(user: dict) -> dict:
        user["id"] = str(user["_id"])
        if "_id" in user:
            del user["_id"]
        return user

    @staticmethod
    async def register_user(user_data: UserCreate) -> dict:
        db = get_database()
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise APIException(status_code=400, detail="Email already registered")
            
        # Create new user document
        new_user = {
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "hashed_password": get_password_hash(user_data.password),
            "role": "user",
            "is_verified": True, # Automatically verified for now
            "refresh_token": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        result = await db.users.insert_one(new_user)
        new_user["_id"] = result.inserted_id
        
        # TODO: Send verification email here (mocking for now)
        verification_token = secrets.token_urlsafe(32)
        await db.users.update_one(
            {"_id": result.inserted_id},
            {"$set": {"verification_token": verification_token}}
        )
        
        return AuthService._format_user_response(new_user)

    @staticmethod
    async def login_user(credentials: UserLogin) -> dict:
        db = get_database()
        
        user = await db.users.find_one({"email": credentials.email})
        if not user or not verify_password(credentials.password, user.get("hashed_password", "")):
            raise APIException(status_code=401, detail="Invalid email or password")
            
        # Generate tokens
        access_token = create_access_token(data={"sub": str(user["_id"])})
        refresh_token = AuthService._create_refresh_token()
        
        # Save refresh token in DB
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "refresh_token": refresh_token,
                "last_login": datetime.now(timezone.utc)
            }}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": AuthService._format_user_response(user)
        }

    @staticmethod
    async def refresh_tokens(refresh_token: str) -> dict:
        db = get_database()
        
        user = await db.users.find_one({"refresh_token": refresh_token})
        if not user:
            raise APIException(status_code=401, detail="Invalid refresh token")
            
        # Rotate refresh token
        new_access_token = create_access_token(data={"sub": str(user["_id"])})
        new_refresh_token = AuthService._create_refresh_token()
        
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"refresh_token": new_refresh_token}}
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "user": AuthService._format_user_response(user)
        }

    @staticmethod
    async def logout_user(user_id: str) -> bool:
        db = get_database()
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"refresh_token": None}}
        )
        return True

    @staticmethod
    async def verify_email(token: str) -> bool:
        db = get_database()
        result = await db.users.update_one(
            {"verification_token": token},
            {
                "$set": {"is_verified": True},
                "$unset": {"verification_token": ""}
            }
        )
        if result.modified_count == 0:
            raise APIException(status_code=400, detail="Invalid or expired verification token")
        return True

    @staticmethod
    async def forgot_password(email: str) -> dict:
        db = get_database()
        user = await db.users.find_one({"email": email})
        
        if user:
            reset_token = secrets.token_urlsafe(32)
            reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
            
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "reset_password_token": reset_token,
                    "reset_password_expires": reset_expires
                }}
            )
            # TODO: Send email with reset token (mocking for now)
            
        # Always return success to prevent email enumeration
        return {"message": "If an account exists, a password reset link has been sent."}

    @staticmethod
    async def reset_password(data: ResetPasswordRequest) -> bool:
        db = get_database()
        user = await db.users.find_one({
            "reset_password_token": data.token,
            "reset_password_expires": {"$gt": datetime.now(timezone.utc)}
        })
        
        if not user:
            raise APIException(status_code=400, detail="Invalid or expired reset token")
            
        hashed_password = get_password_hash(data.new_password)
        
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {"hashed_password": hashed_password},
                "$unset": {
                    "reset_password_token": "", 
                    "reset_password_expires": "",
                    "refresh_token": "" # Invalidate sessions
                }
            }
        )
        return True

    @staticmethod
    async def google_login(token: str) -> dict:
        # Placeholder for actual Google token verification logic using google-auth library
        # import google.oauth2.id_token
        # import google.auth.transport.requests
        # idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
        
        raise APIException(status_code=501, detail="Google Login not fully implemented yet")
