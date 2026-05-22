import os
import shutil
import time
import logging
from pathlib import Path
from config import settings

logger = logging.getLogger(__name__)

class StorageManager:
    """
    Handles asset cleanup, temp storage management, and disk space monitoring.
    Vital for production scalability where high-res videos can quickly fill EBS volumes.
    """
    def __init__(self, output_dir: str = settings.OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.max_age_days = 7

    def _get_disk_usage_percent(self) -> float:
        """Returns the current disk usage percentage of the output directory volume."""
        try:
            total, used, free = shutil.disk_usage(self.output_dir)
            return (used / total) * 100
        except Exception as e:
            logger.error(f"Failed to get disk usage: {e}")
            return 0.0

    def cleanup_orphaned_assets(self, emergency: bool = False):
        """
        Deletes intermediate render files (e.g. temp clips, isolated audio, raw mp4) older than max_age_days.
        If emergency=True, aggressively deletes files older than 1 day to free space.
        """
        disk_usage = self._get_disk_usage_percent()
        logger.info(f"StorageManager: Starting asset cleanup. Current Disk Usage: {disk_usage:.1f}%")
        
        if disk_usage > 90.0:
            logger.warning("StorageManager: CRITICAL DISK SPACE! Activating emergency cleanup.")
            emergency = True
            
        current_time = time.time()
        deleted_count = 0
        freed_bytes = 0
        age_limit_days = 1 if emergency else self.max_age_days

        if not self.output_dir.exists():
            return {"deleted_count": 0, "freed_mb": 0.0}

        for root, _, files in os.walk(self.output_dir):
            for file in files:
                file_path = Path(root) / file
                # Target temp clips, intermediate chunks, and old raw mp4s
                if file.startswith("temp_clip_") or file.endswith((".wav", ".mp4", ".png")):
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (age_limit_days * 86400):
                        try:
                            freed_bytes += file_path.stat().st_size
                            file_path.unlink()
                            deleted_count += 1
                        except Exception as e:
                            logger.error(f"Failed to delete {file_path}: {e}")

        freed_mb = freed_bytes / (1024 * 1024)
        logger.info(f"StorageManager: Cleanup complete. Deleted {deleted_count} files, freed {freed_mb:.2f} MB. Emergency Mode: {emergency}")
        return {"deleted_count": deleted_count, "freed_mb": round(freed_mb, 2), "emergency_mode": emergency}
