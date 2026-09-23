from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class NormalizedOutfit(BaseModel):
    garment: str
    color: str
    style: str
    target: str


class VirtualTryOnSuccessResponse(BaseModel):
    success: bool = True
    provider: str = "huggingface"
    model: str
    original_image_url: str
    generated_image_url: str
    outfit_prompt: str
    normalized_outfit: NormalizedOutfit


class VirtualTryOnFailureResponse(BaseModel):
    success: bool = False
    provider: str = "huggingface"
    error: str
    stage: str


class TryOnResponse(BaseModel):
    id: str
    user_id: str
    analysis_id: Optional[str] = None
    original_image_url: str
    generated_image_url: Optional[str] = None
    outfit_prompt: str
    normalized_outfit: Optional[Dict[str, Any]] = None
    provider: str = "huggingface"
    model: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
