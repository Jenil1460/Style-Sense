from fastapi import APIRouter, Depends
from typing import List, Optional
from app.dependencies.auth import get_current_active_user
from app.schemas.ai import AIAnalysisResponse
from app.services.analysis_service import FashionAnalysisService

router = APIRouter(prefix="/ai", tags=["AI Engine"])

@router.post("/analyze/{upload_id}", response_model=AIAnalysisResponse)
async def analyze_style(
    upload_id: str,
    selected_person_index: Optional[int] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Triggers the ML pipeline to analyze an uploaded image."""
    return await FashionAnalysisService.analyze_upload(
        user_id=current_user["id"],
        upload_id=upload_id,
        selected_person_index=selected_person_index
    )

@router.get("/analysis/{analysis_id}", response_model=AIAnalysisResponse)
async def get_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Retrieves a specific analysis result."""
    return await FashionAnalysisService.get_analysis(current_user["id"], analysis_id)

@router.get("/history", response_model=List[AIAnalysisResponse])
async def get_history(current_user: dict = Depends(get_current_active_user)):
    """Retrieves all past analyses for the user."""
    return await FashionAnalysisService.get_user_analyses(current_user["id"])

@router.delete("/analysis/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Deletes an analysis, its upload metadata, Cloudinary images, and try-on history."""
    await FashionAnalysisService.delete_analysis(current_user["id"], analysis_id)
    return {"success": True, "message": "Analysis deleted successfully"}

