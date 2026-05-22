"""
ShadowReel AI — FastAPI Application Entry Point
"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from api import api_router
from websocket import job_websocket_handler
from utils.database import create_tables

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("Starting ShadowReel AI API...")

    # Ensure output directory exists
    output_dir = Path(settings.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create DB tables
    try:
        await create_tables()
    except Exception as e:
        logger.warning(f"DB table creation skipped (may already exist or DB not ready): {e}")

    logger.info(f"ComfyUI endpoint: {settings.COMFYUI_BASE_URL}")
    logger.info("API ready.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="ShadowReel AI API",
    description="Production-grade AI image and video generation backend",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Serve generated images as static files
output_dir = Path(settings.OUTPUT_DIR)
output_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(output_dir)), name="static")

# REST routes
app.include_router(api_router)


# WebSocket endpoint
@app.websocket("/ws/jobs/{job_id}")
async def websocket_job_endpoint(job_id: str, websocket: WebSocket):
    await job_websocket_handler(job_id, websocket)


# Health check
@app.get("/health", tags=["System"])
async def health():
    from services.comfyui_client import comfyui_client
    comfyui_ok = await comfyui_client.health_check()
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "comfyui": "connected" if comfyui_ok else "unreachable",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
