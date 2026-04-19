from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

import structlog

from app.config import settings
from app.database import engine, async_session
from app.middleware.error_handler import (
    validation_exception_handler,
    generic_exception_handler,
    business_logic_exception_handler,
    BusinessLogicError,
)
from app.routes import lia, appointments, availability, reference, patients, convenios

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("startup", message="Starting Schedule API")
    yield
    logger.info("shutdown", message="Shutting down Schedule API")


app = FastAPI(
    title="Schedule API",
    description="Scheduling system for Clínica Atend Já Sorocaba",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(BusinessLogicError, business_logic_exception_handler)

# Include routers
app.include_router(
    lia.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    appointments.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    availability.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    reference.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    patients.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    convenios.router,
    prefix=settings.API_PREFIX,
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
