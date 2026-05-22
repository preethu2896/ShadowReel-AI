import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from models.generation import Base

class DocumentaryProject(Base):
    __tablename__ = "documentary_projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    team_id = Column(String(36), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    topic = Column(Text, nullable=True)
    script = Column(Text, nullable=True)
    style = Column(String(100), default="Cinematic")
    voice = Column(String(100), default="cinematic_male")
    music_style = Column(String(100), default="cinematic_ambient")
    status = Column(String(50), default="draft", index=True)  # draft, planning, generating_assets, compositing, completed, failed
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    output_url = Column(String(1024), nullable=True)
    
    # Viral & YouTube Metadata
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(Text, nullable=True)
    seo_tags = Column(Text, nullable=True)
    chapters = Column(Text, nullable=True)
    is_short = Column(Boolean, default=False)
    is_trailer = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    scenes = relationship("DocumentaryScene", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "topic": self.topic,
            "script": self.script,
            "style": self.style,
            "voice": self.voice,
            "music_style": self.music_style,
            "status": self.status,
            "progress": self.progress,
            "error_message": self.error_message,
            "output_url": self.output_url,
            "seo_title": self.seo_title,
            "seo_description": self.seo_description,
            "seo_tags": self.seo_tags,
            "chapters": self.chapters,
            "is_short": self.is_short,
            "is_trailer": self.is_trailer,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "scenes": [s.to_dict() for s in sorted(self.scenes, key=lambda x: x.order_index)] if self.scenes else []
        }

class DocumentaryScene(Base):
    __tablename__ = "documentary_scenes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("documentary_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    order_index = Column(Integer, nullable=False)
    
    script_text = Column(Text, nullable=False)
    image_prompt = Column(Text, nullable=True)
    
    image_job_id = Column(String(255), nullable=True)
    image_url = Column(String(1024), nullable=True)
    
    video_job_id = Column(String(255), nullable=True)
    video_url = Column(String(1024), nullable=True)
    
    audio_url = Column(String(1024), nullable=True)
    subtitle_url = Column(String(1024), nullable=True)
    
    duration = Column(Float, default=5.0)
    status = Column(String(50), default="pending", index=True)  # pending, generating_image, generating_video, generating_audio, completed, failed

    project = relationship("DocumentaryProject", back_populates="scenes")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "order_index": self.order_index,
            "script_text": self.script_text,
            "image_prompt": self.image_prompt,
            "image_url": self.image_url,
            "video_url": self.video_url,
            "audio_url": self.audio_url,
            "duration": self.duration,
            "status": self.status
        }
