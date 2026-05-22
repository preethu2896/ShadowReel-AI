import logging
import gc
import time
from functools import wraps

logger = logging.getLogger(__name__)

def cleanup_vram():
    """
    Force garbage collection and clear PyTorch CUDA cache.
    Also unloads cached ComfyUI models via SmartVRAMManager.
    Vital for preventing OOM (Out Of Memory) errors between heavy generation tasks.
    """
    try:
        # Import vram manager to flush models
        from services.comfy_cache.vram_manager import vram_manager
        vram_manager.free_vram(vram_manager.vram_limit_mb) # Free everything
    except ImportError:
        logger.warning("VRAM manager not found, skipping model cache flush.")

    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            gc.collect()
            logger.info("VRAM cleanup successful. CUDA cache cleared.")
    except ImportError:
        logger.warning("PyTorch not installed. Skipping VRAM cleanup.")
    except Exception as e:
        logger.error(f"Error during VRAM cleanup: {e}")

def retry_on_oom(retries=3, backoff_sec=5):
    """
    Decorator to automatically retry a function if a CUDA OOM error occurs.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "out of memory" in error_msg or "oom" in error_msg:
                        attempt += 1
                        logger.warning(f"OOM detected in {func.__name__}. Attempt {attempt}/{retries}. Cleaning VRAM...")
                        cleanup_vram()
                        time.sleep(backoff_sec * attempt)
                        if attempt == retries:
                            logger.error(f"Failed {func.__name__} after {retries} OOM retries.")
                            raise e
                    else:
                        raise e
        return wrapper
    return decorator
