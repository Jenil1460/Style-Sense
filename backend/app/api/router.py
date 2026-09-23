from fastapi import APIRouter
from app.api import auth, ai, uploads, recommendation, virtual_try_on, history, profile, wardrobe

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(ai.router)
api_router.include_router(uploads.router)
api_router.include_router(recommendation.router)
api_router.include_router(virtual_try_on.router)
api_router.include_router(virtual_try_on.legacy_router)

api_router.include_router(history.router)
api_router.include_router(profile.router)
api_router.include_router(wardrobe.router)

