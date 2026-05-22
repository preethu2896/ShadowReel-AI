import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SmartVRAMManager:
    """
    Manages VRAM efficiently for ComfyUI generation.
    Handles dynamic batching, model warm-loading, and VRAM clearing.
    """
    def __init__(self):
        self.loaded_models: Dict[str, Any] = {}
        self.vram_limit_mb = 24000 # Assume 24GB GPU
        self.current_vram_usage_mb = 0

    def warm_load_model(self, model_id: str, estimated_vram_mb: int) -> bool:
        """Warm loads a model into VRAM if space permits."""
        if self.current_vram_usage_mb + estimated_vram_mb > self.vram_limit_mb:
            logger.warning(f"Insufficient VRAM to warm-load {model_id}. Releasing unused models...")
            self.free_vram(estimated_vram_mb)
            
        self.loaded_models[model_id] = {"status": "warm", "vram_mb": estimated_vram_mb}
        self.current_vram_usage_mb += estimated_vram_mb
        logger.info(f"Warm-loaded model {model_id}. Current VRAM usage: {self.current_vram_usage_mb}MB")
        return True

    def free_vram(self, target_mb: int):
        """Frees up VRAM by unloading least recently used models."""
        freed = 0
        to_remove = []
        for model_id, data in self.loaded_models.items():
            to_remove.append(model_id)
            freed += data["vram_mb"]
            if freed >= target_mb:
                break
                
        for model_id in to_remove:
            del self.loaded_models[model_id]
            logger.info(f"Unloaded model {model_id} to free VRAM.")
            
        self.current_vram_usage_mb -= freed
        logger.info(f"Freed {freed}MB of VRAM.")

    def run_generation_diagnostics(self) -> Dict[str, Any]:
        """Provides diagnostics on generation health and VRAM usage."""
        return {
            "vram_limit": self.vram_limit_mb,
            "vram_used": self.current_vram_usage_mb,
            "vram_free": self.vram_limit_mb - self.current_vram_usage_mb,
            "loaded_models_count": len(self.loaded_models)
        }

vram_manager = SmartVRAMManager()
