from fastapi import APIRouter, Depends
from typing import List
from app.dependencies.auth import get_current_active_user
from app.schemas.recommendation import RecommendationResponse, FavoriteToggleRequest
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.post("/generate/{analysis_id}", response_model=RecommendationResponse)
async def generate_recommendations(
    analysis_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Generates an outfit recommendation based on a previous AI analysis."""
    return await RecommendationService.generate_for_analysis(current_user["id"], analysis_id)

@router.get("/", response_model=List[RecommendationResponse])
async def get_recommendation_history(current_user: dict = Depends(get_current_active_user)):
    """Retrieves all past recommendations for the user."""
    return await RecommendationService.get_user_history(current_user["id"])

@router.put("/{recommendation_id}/favorite", response_model=RecommendationResponse)
async def toggle_favorite(
    recommendation_id: str,
    data: FavoriteToggleRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Toggles the favorite status of a specific recommendation."""
    return await RecommendationService.toggle_favorite(current_user["id"], recommendation_id, data)

@router.delete("/{recommendation_id}")
async def delete_recommendation(
    recommendation_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Deletes a specific recommendation from history."""
    await RecommendationService.delete_recommendation(current_user["id"], recommendation_id)
    return {"success": True, "message": "Recommendation successfully deleted"}
