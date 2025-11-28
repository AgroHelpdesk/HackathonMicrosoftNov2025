"""Main FastAPI application module.

This module initializes the FastAPI application, configures middleware,
and registers all API routers.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.acs_webhook import router as acs_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.orchestrator import router as orchestrator_router
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting AgroHelpDesk backend application")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    yield
    # Shutdown
    logger.info("Shutting down AgroHelpDesk backend application")


app = FastAPI(
    title="AgroHelpDesk Backend",
    description="Sistema de atendimento agrícola com IA",
    version="0.1.0",
    lifespan=lifespan,
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions globally."""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else None,
        },
    )


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


# Register routers
app.include_router(health_router, tags=["health"])
app.include_router(orchestrator_router, prefix="/orchestrator", tags=["orchestrator"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(acs_router, prefix="/acs", tags=["acs"])


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": "AgroHelpDesk Backend",
        "version": "0.1.0",
        "status": "running",
    }
