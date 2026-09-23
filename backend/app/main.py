import sys
import os

# Auto-detect local venv site-packages if running under global python
_backend_dir = os.path.dirname(os.path.dirname(__file__))
_venv_site = os.path.join(_backend_dir, "venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from app.config.settings import settings
from app.database.mongodb import db_manager
from app.database.init_db import init_db_collections_and_indexes
from app.api.router import api_router
from app.middleware.cors import setup_cors

from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi.exceptions import RequestValidationError
from app.utils.exceptions import APIException, api_exception_handler, general_exception_handler, validation_exception_handler

# Configure basic logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Events
    logger.info("Starting up StyleSense AI Backend...")
    await db_manager.connect()
    await init_db_collections_and_indexes()

    # Pre-load ML models & pre-compute CLIP text embeddings to eliminate first-request latency
    try:
        from app.services.ml.model_registry import model_registry
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, model_registry.initialize)
        await loop.run_in_executor(None, model_registry.warmup)
        logger.info("ML Models initialized and warmed up successfully.")
    except Exception as e:
        logger.error(f"Error during ML Model initialization: {e}")

    yield
    # Shutdown Events
    logger.info("Shutting down StyleSense AI Backend...")
    await db_manager.close()

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for StyleSense AI - Your Personal AI Fashion Stylist",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup Middleware
setup_cors(app)
app.add_middleware(LoggingMiddleware)

# Setup Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include Routers
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/health", tags=["Health"])
async def health_check():
    db_status = await db_manager.ping()
    return {
        "status": "healthy" if db_status else "degraded",
        "service": settings.APP_NAME,
        "environment": settings.ENV,
        "database_connected": db_status
    }
