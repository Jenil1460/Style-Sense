from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class UploadResponse(BaseModel):
    id: str
    user_id: str
    image_url: str
    public_id: str
    format: str
    size_bytes: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
