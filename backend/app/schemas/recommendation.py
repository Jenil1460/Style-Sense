from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OutfitItem(BaseModel):
    category: str
    name: str
    brand: Optional[str] = None
    color: str

class OutfitSuggestion(BaseModel):
    suggestion: str
    pieces: Optional[List[str]] = None
    occasion: Optional[str] = None

class RecommendationResponse(BaseModel):
    id: str
    user_id: str
    analysis_id: str
    
    occasion: str
    confidence: float
    outfit: List[OutfitItem]
    color_palette: List[str]
    
    # Gemini AI enhancement fields (optional — empty when Gemini unavailable)
    ai_styling_tips: Optional[List[str]] = None
    ai_outfit_suggestions: Optional[List[OutfitSuggestion]] = None
    ai_color_advice: Optional[str] = None
    source: str = "template_engine"
    
    is_favorite: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class FavoriteToggleRequest(BaseModel):
    is_favorite: bool
