from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ShadowReel AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "changeme-in-production"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database (Postgres)
    POSTGRES_USER: str = "shadowreel"
    POSTGRES_PASSWORD: str = "shadowreel_pass"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "shadowreel"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def CELERY_BROKER_URL(self) -> str:
        return self.REDIS_URL

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.REDIS_URL

    # ComfyUI
    COMFYUI_HOST: str = "localhost"
    COMFYUI_PORT: int = 8188

    @property
    def COMFYUI_BASE_URL(self) -> str:
        return f"http://{self.COMFYUI_HOST}:{self.COMFYUI_PORT}"

    @property
    def COMFYUI_WS_URL(self) -> str:
        return f"ws://{self.COMFYUI_HOST}:{self.COMFYUI_PORT}/ws"

    # Storage
    OUTPUT_DIR: str = "outputs/images"
    STATIC_URL_PREFIX: str = "/static"
    MAX_FILE_SIZE_MB: int = 50
    S3_BUCKET: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    CDN_BASE_URL: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    MAX_CONCURRENT_JOBS: int = 3

    # Generation Defaults
    DEFAULT_STEPS: int = 20
    DEFAULT_CFG: float = 7.0
    DEFAULT_WIDTH: int = 1024
    DEFAULT_HEIGHT: int = 1024
    DEFAULT_SAMPLER: str = "euler"
    DEFAULT_SCHEDULER: str = "normal"

    # ── Local dev overrides (no Docker required) ────────────────
    # USE_SQLITE=true  → skip PostgreSQL, use a local SQLite file
    USE_SQLITE: bool = False
    SQLITE_PATH: str = "shadowreel.db"

    # USE_FAKE_REDIS=true → in-memory fakeredis, no Redis server needed
    USE_FAKE_REDIS: bool = False

    @property
    def EFFECTIVE_DATABASE_URL(self) -> str:
        if self.USE_SQLITE:
            return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"
        return self.DATABASE_URL

    @property
    def EFFECTIVE_DATABASE_URL_SYNC(self) -> str:
        if self.USE_SQLITE:
            return f"sqlite:///{self.SQLITE_PATH}"
        return self.DATABASE_URL_SYNC

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
