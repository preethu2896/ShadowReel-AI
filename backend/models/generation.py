import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=True, index=True)
    celery_task_id = Column(String(255), nullable=True, unique=True, index=True)
    job_type = Column(String(20), default="image")  # "image" or "video"

    # Prompt info
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, default="")
    style = Column(String(100), default="Cinematic")

    # Generation params
    width = Column(Integer, default=1024)
    height = Column(Integer, default=1024)
    steps = Column(Integer, default=20)
    cfg_scale = Column(Float, default=7.0)
    sampler = Column(String(100), default="euler")
    scheduler = Column(String(100), default="normal")
    seed = Column(Integer, default=-1)
    model = Column(String(255), default="flux")

    # Status
    status = Column(SAEnum(JobStatus), default=JobStatus.PENDING, index=True)
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    # Output
    output_filename = Column(String(512), nullable=True)
    output_url = Column(String(1024), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "job_type": self.job_type,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "style": self.style,
            "width": self.width,
            "height": self.height,
            "steps": self.steps,
            "cfg_scale": self.cfg_scale,
            "sampler": self.sampler,
            "seed": self.seed,
            "model": self.model,
            "status": self.status.value if self.status else "pending",
            "progress": self.progress,
            "error_message": self.error_message,
            "output_url": self.output_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
