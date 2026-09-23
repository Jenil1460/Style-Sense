import sys
import os
import logging
import traceback
import asyncio
from contextlib import asynccontextmanager

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app.startup")

logger.info("STARTUP: application import started")

try:
    from app.config.settings import settings
    logger.info(f"STARTUP: configuration loaded (ENV={settings.ENV}, DEBUG={settings.DEBUG})")
except Exception as e:
    logger.error(f"STARTUP: configuration load FAILED: {e}\n{traceback.format_exc()}")
    raise

try:
    from app.database.mongodb import db_manager
    from app.database.init_db import init_db_collections_and_indexes
    logger.info("STARTUP: database configuration loaded")
except Exception as e:
    logger.error(f"STARTUP: database module load FAILED: {e}\n{traceback.format_exc()}")
    raise

try:
    from app.services.ml.model_registry import model_registry
    logger.info("STARTUP: AI modules loaded")
except Exception as e:
    logger.error(f"STARTUP: AI modules load warning: {e}\n{traceback.format_exc()}")

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi.exceptions import RequestValidationError

from app.api.router import api_router
from app.middleware.cors import setup_cors
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import limiter
from app.utils.exceptions import (
    APIException,
    api_exception_handler,
    general_exception_handler,
    validation_exception_handler
)


async def _async_model_warmup():
    """Warms up ML models in the background without delaying server port binding."""
    try:
        logger.info("STARTUP: background model initialization started...")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, model_registry.initialize)
        await loop.run_in_executor(None, model_registry.warmup)
        logger.info("STARTUP: background model initialization and warmup COMPLETED successfully.")
    except Exception as e:
        logger.warning(f"STARTUP: background model initialization warning: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Events
    logger.info("Starting up StyleSense AI Backend server...")

    # 1. Connect MongoDB
    try:
        await db_manager.connect()
        if db_manager.db is not None:
            await init_db_collections_and_indexes()
    except Exception as e:
        logger.warning(f"MongoDB startup warning (non-fatal): {e}")

    # 2. Trigger non-blocking background model initialization
    asyncio.create_task(_async_model_warmup())

    logger.info("STARTUP: application startup completed — ready to accept requests.")
    yield

    # Shutdown Events
    logger.info("Shutting down StyleSense AI Backend...")
    try:
        await db_manager.close()
    except Exception as e:
        logger.warning(f"Shutdown cleanup warning: {e}")


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for StyleSense AI - Your Personal AI Fashion Stylist",
    version="2.0.0",
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

# Include API Routers
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Fast health check endpoint for Render and uptime monitors.
    Always returns status: ok immediately without blocking on external network calls.
    """
    db_status = await db_manager.ping()
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "environment": settings.ENV,
        "database": "connected" if db_status else "disconnected"
    }
