import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.shared.config import get_settings

# Add the generated code to path and import our implementation
current_dir = Path(__file__).parent
generated_dir = current_dir / "generated" / "src"
sys.path.insert(0, str(generated_dir))

# Import our posts implementation to register it with BasePostsApi
from app.api.posts_implementation import PostsImplementation


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app


app = create_app()

