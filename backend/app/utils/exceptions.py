from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class APIException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

from fastapi.exceptions import RequestValidationError

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        field_path = " -> ".join([str(loc) for loc in first_error.get("loc", [])])
        msg = first_error.get("msg", "invalid")
        detail = f"Validation Error on '{field_path}': {msg}"
    else:
        detail = "Request validation failed."
        
    return JSONResponse(
        status_code=422,
        content={"success": False, "detail": detail, "error": detail},
    )

async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail, "detail": exc.detail},
    )

async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": f"Internal server error: {str(exc)}"},
    )
