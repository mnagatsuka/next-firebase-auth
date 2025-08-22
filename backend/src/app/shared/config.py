import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Determine a single env file to load based on APP_ENVIRONMENT (OS env only)
    # Falls back to "development" if unset/invalid. Only loads backend/.env.{env}.
    _env_name = os.getenv("APP_ENVIRONMENT", "development").strip().lower()
    if _env_name not in {"development", "staging", "production"}:
        _env_name = "development"
    _env_file = Path("backend") / f".env.{_env_name}"

    model_config = SettingsConfigDict(
        env_file=str(_env_file),
        env_prefix="APP_",
        extra="ignore"  # Ignore extra environment variables
    )

    PROJECT_NAME: str = "Next Firebase Auth Backend"
    VERSION: str = "0.1.0"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://frontend:3000", "http://localhost:6006"]
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Repository provider: "memory" or "dynamodb"
    REPOSITORY_PROVIDER: str = "memory"

    # AWS / DynamoDB Local configuration
    AWS_ENDPOINT_URL: str = "http://localhost:8002"
    AWS_REGION: str = "ap-northeast-1"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"

    # DynamoDB tables
    DYNAMODB_TABLE_POSTS: str = "posts"
    DYNAMODB_TABLE_COMMENTS: str = "comments"
    DYNAMODB_TABLE_FAVORITES: str = "favorites"

    # Firebase Auth configuration
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = None
    FIREBASE_CLIENT_ID: Optional[str] = None
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: str = "https://www.googleapis.com/oauth2/v1/certs"
    FIREBASE_CLIENT_X509_CERT_URL: Optional[str] = None
    
    # Firebase Auth Emulator (for development)
    FIREBASE_AUTH_EMULATOR_HOST: Optional[str] = None
    
    # Serverless WebSocket Configuration
    SERVERLESS_WEBSOCKET_ENDPOINT: str = "http://serverless:3000"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

# Create global settings instance
settings = get_settings()
