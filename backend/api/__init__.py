from fastapi import APIRouter
from .generation import router as generation_router
from .documentary import router as documentary_router
from .system import router as system_router

api_router = APIRouter()
api_router.include_router(generation_router)
api_router.include_router(documentary_router)
api_router.include_router(system_router)

__all__ = ["api_router"]
