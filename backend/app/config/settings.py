from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "StyleSense AI API"
    ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    API_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # MongoDB
    MONGODB_URL: str
    DATABASE_NAME: str = "stylesense_db"
    
    # Cloudinary & Uploads
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB in bytes
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15 # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # 7 days
    
    # Google OAuth (Placeholders for now)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # Google Gemini API (AI Stylist + Nano Banana Image Generation)
    GEMINI_API_KEY: str = ""
    GEMINI_IMAGE_MODEL: str = "gemini-3.1-flash-image"
    
    # OpenAI API (Virtual Try-On Engine)
    OPENAI_API_KEY: str = ""
    OPENAI_IMAGE_MODEL: str = "gpt-image-1"

    # HuggingFace API (Virtual Try-On Engine)
    HF_TOKEN: str = ""
    HF_API_KEY: str = ""
    HF_VTON_MODEL: str = "yisol/IDM-VTON"


    @property
    def hf_auth_token(self) -> str:
        return self.HF_TOKEN or self.HF_API_KEY

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

# Initialize global settings
settings = Settings()
