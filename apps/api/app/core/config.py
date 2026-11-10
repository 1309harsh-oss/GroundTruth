import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GroundTruth API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-dev-key-groundtruth-2026-audit-integrity")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/groundtruth.db")
    
    # Storage
    STORAGE_LOCAL_ROOT: str = os.getenv("STORAGE_LOCAL_ROOT", "./data/storage")
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB
    ALLOWED_MIME_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

