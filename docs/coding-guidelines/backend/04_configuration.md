# 4. Configuration & Environment Variables

Simple configuration management for Python + FastAPI backend using Pydantic Settings and environment variables.

## 1. Basic Settings with Pydantic

Use Pydantic Settings for type-safe configuration management.

```bash
uv add pydantic-settings
```

Example `shared/config.py`:

```python
from typing import Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings with type safety and validation."""
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Firebase Auth
    firebase_project_id: str
    firebase_credentials_path: Optional[str] = None
    
    # API
    cors_origins: list[str] = ["http://localhost:3000"]
    
    # AWS (if using DynamoDB/S3)
    aws_region: str = "us-east-1"
    dynamodb_table_name: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
```

## 2. Environment Variables

Use environment variables for different deployment environments:

```bash
# .env (for development)
ENVIRONMENT=development
DEBUG=true
FIREBASE_PROJECT_ID=your-project-id
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

```bash
# Production environment variables
ENVIRONMENT=production
DEBUG=false
FIREBASE_PROJECT_ID=your-prod-project-id
FIREBASE_CREDENTIALS_PATH=/path/to/service-account.json
CORS_ORIGINS=https://your-domain.com
```

## 3. Configuration Validation

Validate required settings at startup:

```python
def validate_config():
    """Validate required configuration."""
    required_fields = ["firebase_project_id"]
    
    for field in required_fields:
        if not getattr(settings, field):
            raise ValueError(f"Missing required config: {field}")

# Call during app startup
validate_config()
```

**Rules:**

* Never commit `.env.local` files with secrets
* Use environment variables for production secrets
* Validate configuration at application startup
* Keep configuration simple for small/medium applications