"""
Image service — wraps file I/O helpers for saved generation outputs.
"""
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone

import aiofiles
from PIL import Image as PILImage

from config import settings

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(settings.OUTPUT_DIR)


async def save_image_bytes(job_id: str, filename: str, data: bytes) -> str:
    """
    Write raw image bytes to disk and return the static URL path.
    Creates the output directory if it doesn't exist.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_name = f"{job_id}_{filename}"
    dest = OUTPUT_DIR / save_name

    async with aiofiles.open(dest, "wb") as f:
        await f.write(data)

    logger.info(f"Saved image → {dest} ({len(data)} bytes)")
    return f"{settings.STATIC_URL_PREFIX}/{save_name}"


def get_image_metadata(path: Path) -> dict:
    """Extract basic image metadata using Pillow."""
    try:
        with PILImage.open(path) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": path.stat().st_size,
            }
    except Exception as e:
        logger.warning(f"Could not read image metadata for {path}: {e}")
        return {}


def list_output_files() -> list[dict]:
    """List all saved output images with metadata."""
    if not OUTPUT_DIR.exists():
        return []
    results = []
    for f in sorted(OUTPUT_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            results.append({
                "filename": f.name,
                "url": f"{settings.STATIC_URL_PREFIX}/{f.name}",
                "size_bytes": f.stat().st_size,
                "modified_at": datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat(),
            })
    return results


def delete_output_file(filename: str) -> bool:
    """Safely delete an output file. Returns True if deleted."""
    path = OUTPUT_DIR / Path(filename).name  # prevent path traversal
    if path.exists() and path.is_file() and path.parent == OUTPUT_DIR:
        path.unlink()
        logger.info(f"Deleted output file: {path}")
        return True
    return False
