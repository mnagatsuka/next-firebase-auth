from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("backend/.env", "backend/.env.local"), env_prefix="APP_")

    PROJECT_NAME: str = "Next Firebase Auth Backend"
    VERSION: str = "0.1.0"
    ALLOWED_ORIGINS: List[str] = ["*"]
    ENVIRONMENT: str = "development"
    DEBUG: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

