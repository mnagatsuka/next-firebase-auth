from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local", "backend/.env", "backend/.env.local"), 
        env_prefix="APP_",
        extra="ignore"  # Ignore extra environment variables
    )

    PROJECT_NAME: str = "Next Firebase Auth Backend"
    VERSION: str = "0.1.0"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://frontend:3000"]
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Repository provider: "memory" or "dynamodb"
    REPOSITORY_PROVIDER: str = "memory"

    # AWS / LocalStack configuration
    AWS_ENDPOINT_URL: str = "http://localhost:4566"
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"

    # DynamoDB tables
    DYNAMODB_TABLE_POSTS: str = "dev_posts"
    DYNAMODB_TABLE_COMMENTS: str = "dev_comments"

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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
