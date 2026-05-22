"""
Pydantic schemas for API request/response validation.
"""
import uuid
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ModelChoice(str, Enum):
    FLUX = "flux"
    SDXL = "sdxl"


class VideoModelChoice(str, Enum):
    WAN21 = "wan21"
    COGVIDEO = "cogvideo"
    SVD = "svd"


class SamplerChoice(str, Enum):
    EULER = "euler"
    EULER_ANCESTRAL = "euler_ancestral"
    DPM_2 = "dpm_2"
    DPM_2_ANCESTRAL = "dpm_2_ancestral"
    DDIM = "ddim"
    LCMS = "lcm"


class SchedulerChoice(str, Enum):
    NORMAL = "normal"
    KARRAS = "karras"
    EXPONENTIAL = "exponential"
    SIMPLE = "simple"


class GenerateImageRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    negative_prompt: str = Field(default="", max_length=1000)
    style: str = Field(default="Cinematic")
    width: int = Field(default=1024, ge=512, le=2048, multiple_of=64)
    height: int = Field(default=1024, ge=512, le=2048, multiple_of=64)
    steps: int = Field(default=20, ge=1, le=150)
    cfg_scale: float = Field(default=7.0, ge=1.0, le=20.0)
    sampler: SamplerChoice = SamplerChoice.EULER
    scheduler: SchedulerChoice = SchedulerChoice.NORMAL
    seed: int = Field(default=-1, ge=-1, le=2**32 - 1)
    model: ModelChoice = ModelChoice.FLUX

    @field_validator("style")
    @classmethod
    def validate_style(cls, v: str) -> str:
        valid = [
            "Cinematic", "Documentary", "Dark Noir", "Anime", "Hyper Realistic", "Vintage War", "Sci-Fi",
            "Dark Documentary", "War Archives", "Cinematic Realism", "Neo Noir", "Analog Film",
            "Horror Atmosphere", "Sci-Fi Future", "Historical Reconstruction", "Drone Shot", "Apocalypse"
        ]
        if v not in valid:
            raise ValueError(f"style must be one of {valid}")
        return v


class GenerateVideoRequest(BaseModel):
    prompt: Optional[str] = Field(default="", max_length=2000)
    image_id: Optional[str] = Field(default=None) # Reference image to animate
    motion_preset: str = Field(default="Pan Right")
    duration: str = Field(default="5s")
    model: VideoModelChoice = VideoModelChoice.WAN21
    style: str = Field(default="Cinematic Realism")
    fps: int = Field(default=24)
    resolution: str = Field(default="720p")


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    job_type: str = "image"
    status: str
    progress: int
    prompt: Optional[str] = None
    style: Optional[str] = None
    model: Optional[str] = None
    output_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

class CreateDocumentaryRequest(BaseModel):
    title: str = Field(default="Untitled Documentary", max_length=255)
    topic: Optional[str] = Field(default=None, max_length=1000)
    script: Optional[str] = Field(default=None)
    style: str = Field(default="Dark Documentary")
    voice: str = Field(default="cinematic_male")
    music_style: str = Field(default="cinematic_ambient")
    is_short: bool = Field(default=False)
    is_trailer: bool = Field(default=False)

class DocumentarySceneResponse(BaseModel):
    id: str
    order_index: int
    script_text: str
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    duration: float
    status: str

class DocumentaryProjectResponse(BaseModel):
    id: str
    title: str
    topic: Optional[str] = None
    script: Optional[str] = None
    style: str
    voice: str
    music_style: str
    status: str
    progress: int
    error_message: Optional[str] = None
    output_url: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_tags: Optional[str] = None
    chapters: Optional[str] = None
    is_short: bool = False
    is_trailer: bool = False
    created_at: Optional[str] = None
    scenes: list[DocumentarySceneResponse] = []
