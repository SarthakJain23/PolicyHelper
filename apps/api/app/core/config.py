from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Base directory for the repository (PolicyHelper root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(BASE_DIR / ".env"),
            str(Path(__file__).resolve().parent.parent.parent / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"

    # Security & Auth
    JWT_SECRET_KEY: str = "change_this_to_a_very_secure_random_secret_key_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Initial Super Admin
    FIRST_SUPERUSER_EMAIL: str = "admin@company.internal"
    FIRST_SUPERUSER_PASSWORD: str = "AdminInitialPass123!"
    FIRST_SUPERUSER_NAME: str = "System Administrator"

    # PostgreSQL Database
    POSTGRES_USER: str = "policyuser"
    POSTGRES_PASSWORD: str = "policypass123"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5435
    POSTGRES_DB: str = "policyhelper_db"
    DATABASE_URL: str = "postgresql+asyncpg://policyuser:policypass123@localhost:5435/policyhelper_db"

    # Storage Strategy ("local" or "s3")
    STORAGE_TYPE: Literal["local", "s3"] = "local"
    LOCAL_STORAGE_DIR: str = str(BASE_DIR / "data" / "policies")

    # S3 / MinIO (optional)
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY_ID: str = "minioadmin"
    S3_SECRET_ACCESS_KEY: str = "miniopass123"
    S3_BUCKET_NAME: str = "policies"
    S3_REGION: str = "us-east-1"

    # RAG Settings
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120
    RETRIEVAL_TOP_K: int = 15
    RERANK_TOP_K: int = 4
    AUTO_TITLE_MESSAGE_THRESHOLD: int = 2
    DEFAULT_EMBEDDING_DIMENSIONS: int = 1536


settings = Settings()
