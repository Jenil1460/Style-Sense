from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "StyleSense AI API"
    ENV: str = "production"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Frontend / CORS
    FRONTEND_URL: str = ""
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://stylesense-ai.vercel.app",
        "https://stylesense-ai.onrender.com"
    ]
    
    # MongoDB
    MONGODB_URL: str = ""
    DATABASE_NAME: str = "stylesense_db"
    
    # Cloudinary & Uploads
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB in bytes
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    
    # JWT Auth Configuration
    JWT_SECRET_KEY: str = "default-stylesense-jwt-secret-key-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth (Placeholders)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # Google Gemini API (AI Stylist + Fashion Summary)
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
    def cors_origins_list(self) -> List[str]:
        origins = []
        if isinstance(self.CORS_ORIGINS, str):
            origins = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        elif isinstance(self.CORS_ORIGINS, list):
            origins = list(self.CORS_ORIGINS)
        
        if self.FRONTEND_URL and self.FRONTEND_URL.strip():
            url = self.FRONTEND_URL.strip().rstrip("/")
            if url not in origins:
                origins.append(url)
            # Also allow with trailing slash
            if f"{url}/" not in origins:
                origins.append(f"{url}/")
        return origins

    @property
    def hf_auth_token(self) -> str:
        return self.HF_TOKEN or self.HF_API_KEY

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

# Initialize global settings safely
settings = Settings()
