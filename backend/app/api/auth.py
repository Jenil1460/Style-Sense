from fastapi import APIRouter, Depends, Request
from typing import Dict, Any

from app.schemas.user import (
    UserCreate, UserLogin, TokenResponse, 
    RefreshTokenRequest, GoogleLoginRequest, 
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Dict[str, Any], status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserCreate):
    return await AuthService.register_user(user_data)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, credentials: UserLogin):
    return await AuthService.login_user(credentials)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest):
    return await AuthService.refresh_tokens(data.refresh_token)

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    await AuthService.logout_user(current_user["id"])
    return {"success": True, "message": "Successfully logged out"}

@router.post("/google-login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def google_login(request: Request, data: GoogleLoginRequest):
    return await AuthService.google_login(data.token)

@router.get("/verify-email")
async def verify_email(token: str):
    await AuthService.verify_email(token)
    return {"success": True, "message": "Email successfully verified"}

@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: ForgotPasswordRequest):
    return await AuthService.forgot_password(data.email)

@router.post("/reset-password")
@limiter.limit("3/minute")
async def reset_password(request: Request, data: ResetPasswordRequest):
    await AuthService.reset_password(data)
    return {"success": True, "message": "Password successfully reset"}
