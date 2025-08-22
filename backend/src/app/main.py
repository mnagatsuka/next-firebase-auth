import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Import generated code setup (must be before other app imports)
from app.shared.generated_imports import setup_generated_imports

from app.api.router import api_router
from app.shared.config import get_settings
from app.shared.firebase import get_firebase_service
from app.application.exceptions import AuthenticationError, InvalidTokenError

# Ensure generated imports are available
setup_generated_imports()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Note: CORS is handled by Lambda Function URL configuration.
    # Avoid app-level CORS to prevent conflicting headers.

    # Initialize Firebase Admin SDK
    try:
        firebase_service = get_firebase_service()
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize Firebase Admin SDK: %s", str(e))
        # You might want to raise an exception here depending on your requirements
        # raise e

    # Add global exception handlers
    @app.exception_handler(AuthenticationError)
    @app.exception_handler(InvalidTokenError)
    async def authentication_exception_handler(request: Request, exc: AuthenticationError):
        """Handle authentication errors globally."""
        logger.warning(f"Authentication error: {exc.message}", extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": exc.__class__.__name__
        })
        return JSONResponse(
            status_code=401,
            content={"detail": exc.message},
            headers={"WWW-Authenticate": "Bearer"}
        )

    app.include_router(api_router)

    return app


app = create_app()
