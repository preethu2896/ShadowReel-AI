import logging
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import psutil

from utils.database import get_db
from models import GenerationJob, JobStatus
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/system", tags=["System"])

def get_gpu_vram() -> Dict[str, Any]:
    """Try to get real GPU VRAM using pynvml. Fall back to RAM if no GPU."""
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        used_gb = info.used / (1024 ** 3)
        total_gb = info.total / (1024 ** 3)
        pynvml.nvmlShutdown()
        return {
            "used_gb": round(used_gb, 1),
            "total_gb": round(total_gb, 1),
            "type": "VRAM"
        }
    except Exception as e:
        logger.debug(f"Could not read GPU VRAM: {e}")
        # Fallback to system memory
        mem = psutil.virtual_memory()
        used_gb = mem.used / (1024 ** 3)
        total_gb = mem.total / (1024 ** 3)
        return {
            "used_gb": round(used_gb, 1),
            "total_gb": round(total_gb, 1),
            "type": "RAM (Fallback)"
        }

def get_storage_stats() -> Dict[str, Any]:
    """Get storage stats for the output directory."""
    try:
        output_dir = Path(settings.OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        total, used, free = shutil.disk_usage(output_dir)
        return {
            "used_gb": round(used / (1024 ** 3), 1),
            "total_gb": round(total / (1024 ** 3), 1),
        }
    except Exception as e:
        logger.error(f"Failed to read disk usage: {e}")
        return {
            "used_gb": 0,
            "total_gb": 0,
        }

@router.get("/stats")
async def get_system_stats(db: AsyncSession = Depends(get_db)):
    """Return real system stats including GPU, Storage, and Job metrics."""
    # 1. Hardware Stats
    vram = get_gpu_vram()
    storage = get_storage_stats()

    # 2. Render Queue Stats (Active/Queued jobs)
    active_query = await db.execute(
        select(func.count(GenerationJob.id))
        .where(GenerationJob.status.in_([JobStatus.QUEUED, JobStatus.PROCESSING]))
    )
    active_jobs = active_query.scalar() or 0

    # 3. Production Analytics
    # Reliability: completed / (completed + failed)
    completed_query = await db.execute(
        select(func.count(GenerationJob.id))
        .where(GenerationJob.status == JobStatus.COMPLETED)
    )
    completed_jobs = completed_query.scalar() or 0

    failed_query = await db.execute(
        select(func.count(GenerationJob.id))
        .where(GenerationJob.status == JobStatus.FAILED)
    )
    failed_jobs = failed_query.scalar() or 0

    total_finished = completed_jobs + failed_jobs
    reliability = 100.0
    if total_finished > 0:
        reliability = (completed_jobs / total_finished) * 100

    # Avg Export Time for completed jobs
    avg_time_query = await db.execute(
        select(GenerationJob.started_at, GenerationJob.completed_at)
        .where(GenerationJob.status == JobStatus.COMPLETED)
        .where(GenerationJob.started_at.is_not(None))
        .where(GenerationJob.completed_at.is_not(None))
        .order_by(GenerationJob.completed_at.desc())
        .limit(20)  # average over last 20 jobs
    )
    jobs_time = avg_time_query.all()
    
    avg_time_seconds = 0
    if jobs_time:
        total_seconds = sum((j.completed_at - j.started_at).total_seconds() for j in jobs_time)
        avg_time_seconds = total_seconds / len(jobs_time)
    
    avg_export_minutes = avg_time_seconds / 60

    return {
        "hardware": {
            "vram": vram,
            "storage": storage
        },
        "queue": {
            "active_jobs": active_jobs
        },
        "analytics": {
            "reliability_percent": round(reliability, 1),
            "failed_jobs": failed_jobs,
            "avg_export_time_minutes": round(avg_export_minutes, 1)
        }
    }
