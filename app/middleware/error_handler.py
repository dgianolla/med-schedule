import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = structlog.get_logger()


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with structured responses."""
    logger.warning(
        "validation_error",
        path=request.url.path,
        method=request.method,
        errors=exc.errors(),
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters",
                "details": exc.errors(),
            }
        },
    )


class BusinessLogicError(Exception):
    """Custom exception for business logic errors."""

    def __init__(
        self,
        code: str,
        message: str,
        details: dict | None = None,
        status_code: int = 400,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


async def business_logic_exception_handler(request: Request, exc: BusinessLogicError):
    """Handle business logic errors with structured responses."""
    logger.warning(
        "business_logic_error",
        path=request.url.path,
        method=request.method,
        code=exc.code,
        message=exc.message,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )
