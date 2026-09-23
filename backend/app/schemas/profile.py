from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from enum import Enum

class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"
    non_binary = "Non-binary"
    other = "Other"

class BodyTypeEnum(str, Enum):
    slim = "Slim"
    athletic = "Athletic"
    average = "Average"
    plus_size = "Plus-size"

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    gender: Optional[GenderEnum] = None
    height: Optional[float] = Field(None, gt=0, description="Height in cm")
    weight: Optional[float] = Field(None, gt=0, description="Weight in kg")
    body_type: Optional[BodyTypeEnum] = None
    preferred_styles: Optional[List[str]] = Field(default_factory=list)
    favorite_colors: Optional[List[str]] = Field(default_factory=list)
    fashion_preferences: Optional[str] = Field(None, max_length=500)

class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
