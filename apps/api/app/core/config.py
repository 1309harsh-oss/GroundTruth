import os
import shutil
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# ---------------------------------------------------------------------------
# Vercel serverless: redirect writable paths to /tmp before Settings loads
# ---------------------------------------------------------------------------
_IS_VERCEL = bool(os.getenv("VERCEL"))
if _IS_VERCEL:
    # SQLite must live in /tmp (the only writable dir on Vercel)
    if not os.getenv("DATABASE_URL"):
        _tmp_db = "/tmp/groundtruth.db"
        # Seed from bundled DB if present and not yet copied
        _bundled = Path(__file__).resolve().parents[4] / "data" / "groundtruth.db"
        if _bundled.exists() and not Path(_tmp_db).exists():
            shutil.copy2(str(_bundled), _tmp_db)
        os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db}"

    # File uploads must land in /tmp/storage
    if not os.getenv("STORAGE_LOCAL_ROOT"):
        _tmp_storage = "/tmp/storage"
        Path(_tmp_storage).mkdir(parents=True, exist_ok=True)
        os.environ["STORAGE_LOCAL_ROOT"] = _tmp_storage


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

    # Firebase Cloud Database
    FIREBASE_CREDENTIALS_PATH: Optional[str] = os.getenv("FIREBASE_CREDENTIALS_PATH", None)
    FIREBASE_DATABASE_URL: Optional[str] = os.getenv("FIREBASE_DATABASE_URL", None)

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

