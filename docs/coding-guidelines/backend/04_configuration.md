# 4. Configuration & Environments

This section describes how to manage **configuration**, **environment variables**, and **secrets** in a Python + FastAPI backend using **Pydantic Settings** for type-safe configuration management.

It covers **typed settings**, **environment separation**, **secrets handling**, **feature flags**, and **operational toggles** to ensure consistent and secure configuration across all deployment environments.

## 1. Typed Settings with Pydantic Settings

We use **Pydantic Settings** for type-safe configuration management with automatic environment variable loading and validation.

Install Pydantic Settings:

```bash
uv add pydantic-settings
```

Example `shared/config.py`:

```python
from typing import Literal, Optional
from pydantic import BaseSettings, Field, validator
from pydantic.networks import AnyHttpUrl


class Settings(BaseSettings):
    """Application settings with type safety and validation."""
    
    # Environment & Debug
    environment: Literal["local", "dev", "staging", "prod"] = "local"
    debug: bool = Field(default=False)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    
    # API Configuration
    api_title: str = "Backend API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]
    
    # Database
    dynamodb_table_name: str = Field(...)
    dynamodb_region: str = "us-east-1"
    dynamodb_endpoint: Optional[AnyHttpUrl] = None  # For LocalStack
    
    # Storage
    s3_bucket_name: str = Field(...)
    s3_region: str = "us-east-1"
    s3_endpoint: Optional[AnyHttpUrl] = None  # For LocalStack
    
    # Authentication
    firebase_project_id: str = Field(...)
    firebase_credentials_path: Optional[str] = None
    auth_token_cache_ttl: int = 300  # seconds
    
    # Performance
    request_timeout: int = 30
    max_connections: int = 100
    connection_pool_size: int = 10
    
    # Feature Flags
    enable_metrics: bool = True
    enable_tracing: bool = False
    enable_rate_limiting: bool = True
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("environment")
    def validate_environment(cls, v):
        if v not in ["local", "dev", "staging", "prod"]:
            raise ValueError("Invalid environment")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
```

**Rules:**

* Use **Pydantic Settings** for all configuration management.
* Define **explicit types** for all settings fields.
* Use **validators** for complex validation logic.
* Provide **sensible defaults** where appropriate.

## 2. Environment Separation

We maintain separate configuration for each environment with clear precedence rules.

### Environment Files

* `.env.local` — Local development (not committed)
* `.env.dev` — Development environment
* `.env.staging` — Staging environment  
* `.env.prod` — Production environment
* `.env.test` — Testing environment

### Environment Loading Precedence

1. **Environment variables** (highest priority)
2. **`.env.{environment}` file**
3. **`.env` file**
4. **Default values** (lowest priority)

Example environment-specific loading:

```python
import os
from shared.config import Settings

def load_settings() -> Settings:
    """Load settings based on current environment."""
    env = os.getenv("ENVIRONMENT", "local")
    
    env_files = [
        ".env",
        f".env.{env}",
        ".env.local"  # Always load local overrides if present
    ]
    
    # Filter existing files
    existing_files = [f for f in env_files if os.path.exists(f)]
    
    return Settings(_env_file=existing_files)
```

**Rules:**

* Never commit `.env.local` or files containing secrets.
* Use **environment variables** for production secrets.
* Document all required variables in `docs/env.md`.
* Use clear naming conventions: `{SERVICE}_{COMPONENT}_{SETTING}`.

## 3. Secrets Handling

### Local Development

```bash
# .env.local (not committed)
FIREBASE_PROJECT_ID=my-project-dev
DYNAMODB_TABLE_NAME=my-app-dev
S3_BUCKET_NAME=my-app-dev-bucket
FIREBASE_CREDENTIALS_PATH=/path/to/service-account.json
```

### Production (AWS Lambda)

Use **AWS Systems Manager Parameter Store** or **AWS Secrets Manager**:

```python
import boto3
from functools import lru_cache

@lru_cache(maxsize=None)
def get_secret(secret_name: str) -> str:
    """Get secret from AWS Secrets Manager with caching."""
    client = boto3.client("secretsmanager")
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response["SecretString"]
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve secret {secret_name}: {e}")


class ProductionSettings(Settings):
    """Production settings with secrets from AWS."""
    
    @validator("firebase_credentials_path", pre=True)
    def load_firebase_credentials(cls, v):
        if not v and cls.environment == "prod":
            return get_secret("firebase-service-account-key")
        return v
```

**Rules:**

* **Never** commit secrets or credentials to version control.
* Use **AWS Secrets Manager** or **Parameter Store** in production.
* Cache secrets to avoid repeated API calls.
* Use **IAM roles** instead of access keys when possible.

## 4. Feature Flags & Operational Toggles

Implement feature flags for gradual rollouts and operational control:

```python
from enum import Enum

class FeatureFlag(str, Enum):
    """Available feature flags."""
    ENHANCED_LOGGING = "enhanced_logging"
    NEW_AUTH_FLOW = "new_auth_flow"
    EXPERIMENTAL_CACHING = "experimental_caching"


class Settings(BaseSettings):
    # Feature Flags
    feature_flags: dict[str, bool] = Field(default_factory=dict)
    
    # Operational Toggles
    maintenance_mode: bool = False
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 1000
    
    def is_feature_enabled(self, feature: FeatureFlag) -> bool:
        """Check if a feature flag is enabled."""
        return self.feature_flags.get(feature.value, False)
    
    @validator("feature_flags", pre=True)
    def parse_feature_flags(cls, v):
        if isinstance(v, str):
            # Parse comma-separated flags: "flag1=true,flag2=false"
            flags = {}
            for flag in v.split(","):
                if "=" in flag:
                    key, value = flag.split("=", 1)
                    flags[key.strip()] = value.strip().lower() == "true"
            return flags
        return v or {}
```

Usage in application code:

```python
from shared.config import settings

def create_user(user_data: dict):
    """Create user with optional enhanced logging."""
    
    if settings.is_feature_enabled(FeatureFlag.ENHANCED_LOGGING):
        logger.info("Enhanced logging enabled", extra={"user_data": user_data})
    
    if settings.is_feature_enabled(FeatureFlag.NEW_AUTH_FLOW):
        return create_user_v2(user_data)
    else:
        return create_user_v1(user_data)
```

**Rules:**

* Use **feature flags** for gradual rollouts and A/B testing.
* Implement **operational toggles** for runtime control.
* Remove **obsolete flags** after full rollout.
* Document all flags and their expected lifecycle.

## 5. Configuration Validation

Validate configuration at application startup:

```python
import sys
from shared.config import settings

def validate_configuration():
    """Validate configuration at startup."""
    
    required_for_production = [
        "dynamodb_table_name",
        "s3_bucket_name", 
        "firebase_project_id"
    ]
    
    if settings.environment == "prod":
        missing = [field for field in required_for_production 
                  if not getattr(settings, field, None)]
        
        if missing:
            raise ValueError(f"Missing required production config: {missing}")
    
    # Validate AWS resources exist
    if settings.environment != "local":
        validate_aws_resources()

def validate_aws_resources():
    """Validate that required AWS resources exist."""
    # Implementation depends on specific AWS services used
    pass

# Call during application startup
if __name__ == "__main__":
    try:
        validate_configuration()
        print(f"✓ Configuration valid for environment: {settings.environment}")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        sys.exit(1)
```

**Rules:**

* **Validate configuration** at application startup.
* **Fail fast** if required settings are missing.
* **Test configuration** in CI/CD pipelines.
* Provide **clear error messages** for configuration issues.

By following these configuration patterns, we ensure **type safety**, **security**, and **consistency** across all environments while maintaining flexibility for different deployment scenarios.