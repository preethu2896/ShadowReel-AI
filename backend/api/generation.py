"""
Image generation API endpoints.
"""
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.schemas import GenerateImageRequest, GenerateVideoRequest, JobResponse, JobStatusResponse
from models import GenerationJob, JobStatus
from services.redis_client import get_job_state, set_job_state
from services.comfyui_client import comfyui_client
from utils.database import get_db
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/generate", tags=["Generation"])


# ---------------------------------------------------------------------------
# Rate Limiting (simple in-memory; use Redis for production multi-instance)
# ---------------------------------------------------------------------------
from collections import defaultdict
import time

_rate_store: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(client_ip: str):
    now = time.time()
    window = 60  # seconds
    limit = settings.RATE_LIMIT_PER_MINUTE
    timestamps = [t for t in _rate_store[client_ip] if now - t < window]
    timestamps.append(now)
    _rate_store[client_ip] = timestamps
    if len(timestamps) > limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {limit} requests/minute. Try again shortly.",
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/image", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_image(
    request: Request,
    body: GenerateImageRequest,
    db: AsyncSession = Depends(get_db),
):
    """Queue an image generation job. Returns a job_id for status polling."""
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    # Check ComfyUI availability
    comfyui_ok = await comfyui_client.health_check()
    if not comfyui_ok:
        raise HTTPException(
            status_code=503,
            detail="ComfyUI backend is not reachable. Please start ComfyUI and try again.",
        )

    # Create DB record
    job = GenerationJob(
        id=uuid.uuid4(),
        prompt=body.prompt,
        negative_prompt=body.negative_prompt,
        style=body.style,
        width=body.width,
        height=body.height,
        steps=body.steps,
        cfg_scale=body.cfg_scale,
        sampler=body.sampler.value,
        scheduler=body.scheduler.value,
        seed=body.seed,
        model=body.model.value,
        status=JobStatus.QUEUED,
    )
    db.add(job)
    await db.flush()
    job_id = str(job.id)

    # Cache initial state in Redis
    await set_job_state(job_id, {"status": "queued", "progress": 0, "job_id": job_id})

    # Enqueue Celery task
    from workers.celery_app import generate_image_task
    generate_image_task.apply_async(
        kwargs={
            "job_id": job_id,
            "params": {
                "prompt": body.prompt,
                "negative_prompt": body.negative_prompt,
                "style": body.style,
                "width": body.width,
                "height": body.height,
                "steps": body.steps,
                "cfg_scale": body.cfg_scale,
                "sampler": body.sampler.value,
                "scheduler": body.scheduler.value,
                "seed": body.seed,
                "model": body.model.value,
            },
        },
        queue="generation",
    )

    logger.info(f"Queued image job {job_id} for prompt: {body.prompt[:60]}...")
    return JobResponse(job_id=job_id, status="queued", message="Generation job queued successfully.")


@router.post("/video", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_video(
    request: Request,
    body: GenerateVideoRequest,
    db: AsyncSession = Depends(get_db),
):
    """Queue a video generation job."""
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    # Check ComfyUI availability
    comfyui_ok = await comfyui_client.health_check()
    if not comfyui_ok:
        raise HTTPException(
            status_code=503,
            detail="ComfyUI backend is not reachable.",
        )

    # Create DB record
    job = GenerationJob(
        id=uuid.uuid4(),
        job_type="video",
        prompt=body.prompt or f"Image animation ({body.image_id})",
        style=body.style,
        model=body.model.value,
        status=JobStatus.QUEUED,
    )
    db.add(job)
    await db.flush()
    job_id = str(job.id)

    # Cache initial state in Redis
    await set_job_state(job_id, {"status": "queued", "progress": 0, "job_id": job_id, "job_type": "video"})

    # Enqueue Celery task
    from workers.celery_app import generate_video_task
    generate_video_task.apply_async(
        kwargs={
            "job_id": job_id,
            "params": {
                "prompt": body.prompt,
                "image_id": body.image_id,
                "motion_preset": body.motion_preset,
                "duration": body.duration,
                "model": body.model.value,
                "style": body.style,
                "fps": body.fps,
                "resolution": body.resolution,
            },
        },
        queue="video",
    )

    logger.info(f"Queued video job {job_id}")
    return JobResponse(job_id=job_id, status="queued", message="Video generation queued successfully.")


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    """Poll job status. Frontend should use WebSocket for real-time; this is for fallback."""
    # Try Redis cache first (fast)
    cached = await get_job_state(job_id)

    # Then DB for full details
    result = await db.execute(select(GenerationJob).where(GenerationJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=str(job.id),
        job_type=job.job_type,
        status=job.status.value,
        progress=job.progress,
        prompt=job.prompt,
        style=job.style,
        model=job.model,
        output_url=job.output_url,
        error_message=job.error_message,
        created_at=job.created_at.isoformat() if job.created_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
    )


@router.get("/history", response_model=list[JobStatusResponse])
async def get_generation_history(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Return recent generation jobs (gallery)."""
    result = await db.execute(
        select(GenerationJob)
        .order_by(GenerationJob.created_at.desc())
        .limit(limit)
    )
    jobs = result.scalars().all()
    return [
        JobStatusResponse(
            job_id=str(j.id),
            job_type=j.job_type,
            status=j.status.value,
            progress=j.progress,
            prompt=j.prompt,
            style=j.style,
            model=j.model,
            output_url=j.output_url,
            error_message=j.error_message,
            created_at=j.created_at.isoformat() if j.created_at else None,
            completed_at=j.completed_at.isoformat() if j.completed_at else None,
        )
        for j in jobs
    ]
