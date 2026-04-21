from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

import structlog

from app.config import settings
from app.database import engine, async_session
from app.middleware.error_handler import (
    validation_exception_handler,
    business_logic_exception_handler,
    BusinessLogicError,
)
from app.routes import lia, appointments, availability, reference, patients, convenios, auth
from app.middleware.auth_deps import verify_token
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.future import select
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(__import__("logging"), settings.LOG_LEVEL.upper())
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()


async def ensure_admin_user():
    async with async_session() as session:
        stmt = select(User).where(User.username == settings.ADMIN_USERNAME)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if not user:
            logger.info("seed", message="Creating default admin user")
            hashed_password = pwd_context.hash(settings.ADMIN_PASSWORD)
            admin = User(
                username=settings.ADMIN_USERNAME,
                hashed_password=hashed_password,
                is_active=True
            )
            session.add(admin)
            await session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("startup", message="Starting Schedule API")
    try:
        await ensure_admin_user()
    except Exception as exc:
        logger.error(
            "startup_seed_failed",
            message="Failed to ensure default admin user",
            error=str(exc),
        )
    yield
    logger.info("shutdown", message="Shutting down Schedule API")


app = FastAPI(
    title="Schedule API",
    description="Scheduling system for Clínica Atend Já Sorocaba",
    version="1.0.0",
    lifespan=lifespan,
)

class CatchAllExceptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error(
                "unexpected_error",
                path=request.url.path,
                method=request.method,
                error=str(exc),
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                    }
                },
            )


# Middleware order: last added is outermost. CORS must wrap the exception
# catcher so 500 responses still carry Access-Control-Allow-Origin.
app.add_middleware(CatchAllExceptionsMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers (HTTP-level; run inside CORS via ExceptionMiddleware)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(BusinessLogicError, business_logic_exception_handler)

# Include routers
# Security and Auth
app.include_router(
    auth.router,
    prefix=settings.API_PREFIX,
)

# Open Agent Endpoints
app.include_router(
    lia.router,
    prefix=settings.API_PREFIX,
)

# Secured Admin Endpoints
app.include_router(
    appointments.router,
    prefix=settings.API_PREFIX,
    dependencies=[Depends(verify_token)]
)
app.include_router(
    availability.router,
    prefix=settings.API_PREFIX,
    dependencies=[Depends(verify_token)]
)
app.include_router(
    reference.router,
    prefix=settings.API_PREFIX,
    dependencies=[Depends(verify_token)]
)
app.include_router(
    patients.router,
    prefix=settings.API_PREFIX,
    dependencies=[Depends(verify_token)]
)
app.include_router(
    convenios.router,
    prefix=settings.API_PREFIX,
    dependencies=[Depends(verify_token)]
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Schedule API",
        "docs": "/docs",
        "health": "/health",
    }
