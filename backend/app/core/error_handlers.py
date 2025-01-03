from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from typing import Any, Dict, Optional
import logging
import traceback

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base application error"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

class ValidationError(AppError):
    """Validation error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )

class BoardError(AppError):
    """Board-related error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BOARD_ERROR",
            details=details
        )

class InstallationError(AppError):
    """Installation process error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INSTALLATION_ERROR",
            details=details
        )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors from FastAPI"""
    errors = []
    for error in exc.errors():
        error_info = {
            "field": " -> ".join([str(x) for x in error["loc"]]),
            "message": error["msg"],
            "type": error["type"]
        }
        errors.append(error_info)
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "details": {"errors": errors}
        }
    )

async def app_error_handler(request: Request, exc: AppError):
    """Handle application-specific errors"""
    logger.error(f"Application error: {exc.message}", exc_info=True)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error("Unexpected error occurred", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": {
                "type": type(exc).__name__,
                "trace_id": request.state.trace_id if hasattr(request.state, 'trace_id') else None
            }
        }
    )

def setup_error_handlers(app):
    """Configure error handlers for the application"""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    @app.middleware("http")
    async def error_logging_middleware(request: Request, call_next):
        """Middleware to log errors and add trace ID"""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(
                f"Error processing request: {request.method} {request.url}",
                exc_info=True,
                extra={
                    "request_id": request.state.trace_id if hasattr(request.state, 'trace_id') else None,
                    "client_ip": request.client.host,
                    "path": request.url.path,
                    "method": request.method
                }
            )
            raise
