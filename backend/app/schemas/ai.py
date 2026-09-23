from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class ColorEntry(BaseModel):
    name: str
    percentage: float


class ColorPalette(BaseModel):
    primary: str
    secondary: Optional[str] = None
    accent: Optional[str] = None
    palette: Optional[List[ColorEntry]] = []


class StyleClassification(BaseModel):
    style_name: str
    confidence: float


class ClothingItem(BaseModel):
    item: str
    confidence: float
    region: Optional[str] = None


class SkinToneResult(BaseModel):
    tone: str
    confidence: float


class PersonDetectionResult(BaseModel):
    detected: bool
    confidence: float
    x_min: Optional[float] = None
    y_min: Optional[float] = None
    x_max: Optional[float] = None
    y_max: Optional[float] = None


class PoseResult(BaseModel):
    pose_type: str
    orientation: Optional[str] = None
    overall_confidence: float
    shoulder_visibility: Optional[float] = None
    hip_visibility: Optional[float] = None
    knee_visibility: Optional[float] = None


class RadarMetrics(BaseModel):
    overall_score: int
    color_harmony: int
    fit: int
    style_consistency: int
    accessories: int
    occasion_suitability: int
    modern_trends: int


class BodyTypeResult(BaseModel):
    body_type: str
    confidence: float
    fit_recommendation: Optional[str] = None
    disclaimer: Optional[str] = None


class FaceShapeResult(BaseModel):
    face_shape: str
    confidence: float
    accessory_tip: Optional[str] = None


class ColorCard(BaseModel):
    name: str
    hex: str
    rgb: List[int]
    why_it_works: Optional[str] = None
    experiment_note: Optional[str] = None


class OutfitCombination(BaseModel):
    title: str
    top: str
    bottom: str
    shoes: str
    description: str


class PersonalColorPaletteResponse(BaseModel):
    skin_tone: str
    undertone: str
    confidence: float
    evidence: Optional[str] = None
    recommended_colors: List[ColorCard] = []
    experimental_colors: List[ColorCard] = []
    outfit_combinations: List[OutfitCombination] = []
    existing_outfit_harmony: Optional[str] = None


class AIAnalysisResponse(BaseModel):
    id: str
    user_id: str
    upload_id: str
    image_url: str

    # Core ML outputs
    person_detection: Optional[Any] = None
    pose: Optional[Any] = None
    segmentation: Optional[Any] = None
    colors: Optional[Any] = None
    clothing_detected: Optional[List[Any]] = []
    skin_tone: Optional[Any] = None
    personal_color_palette: Optional[Any] = None
    body_type: Optional[Any] = None
    face_shape: Optional[Any] = None
    styles: Optional[List[Any]] = []

    # Derived results
    occasion: Optional[str] = None
    season: Optional[str] = None
    fashion_score: int
    radar_metrics: Optional[Any] = None
    recommendations: List[str]
    garments: Optional[List[Any]] = []
    body_visibility: Optional[Any] = None
    lower_body_status: Optional[str] = None
    footwear_status: Optional[str] = None
    visibility_note: Optional[str] = None
    explainability: Optional[Any] = None
    ai_summary: Optional[str] = None

    status: str
    created_at: datetime

    class Config:
        from_attributes = True


