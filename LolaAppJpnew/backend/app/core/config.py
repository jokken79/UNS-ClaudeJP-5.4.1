"""
Core configuration for LolaAppJp backend
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings with environment variable loading"""

    # Application
    APP_NAME: str = "LolaAppJp - HR Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://frontend:3000"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Azure Computer Vision OCR
    AZURE_CV_ENDPOINT: Optional[str] = None
    AZURE_CV_KEY: Optional[str] = None

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "/app/uploads"
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".pdf"]

    # Email (Future)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # LINE Notify (Future)
    LINE_NOTIFY_TOKEN: Optional[str] = None

    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://otel-collector:4317"
    PROMETHEUS_METRICS_PORT: int = 8001

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Timezone
    TIMEZONE: str = "Asia/Tokyo"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
