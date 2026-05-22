import logging
import time
from typing import Dict
from collections import deque

logger = logging.getLogger(__name__)

class PerformanceBenchmarker:
    """
    Internal benchmark suite to track execution quality, VRAM stability, and queue health.
    Avoids theoretical abstractions and focuses purely on production metrics.
    """
    def __init__(self):
        self.generation_times = deque(maxlen=100)
        self.export_times = deque(maxlen=100)
        self.vram_efficiency_ratios = deque(maxlen=100)
        self.ssim_estimations = deque(maxlen=100)
        self.failed_tasks = 0
        self.retry_attempts = 0
        self.total_processed = 0

    def record_task(self, task_type: str, duration_sec: float, success: bool):
        """Records telemetry for an executed job to build internal dashboards."""
        self.total_processed += 1
        
        if not success:
            self.failed_tasks += 1
            logger.error(f"Benchmark: {task_type} failed after {duration_sec:.2f}s.")
            return
            
        if task_type == "generation":
            self.generation_times.append(duration_sec)
        elif task_type == "export":
            self.export_times.append(duration_sec)

    def record_vram_efficiency(self, ratio: float):
        """Records the VRAM efficiency ratio (used vs available/allocated)."""
        self.vram_efficiency_ratios.append(ratio)
        logger.info(f"VRAM efficiency ratio recorded: {ratio:.2f}")

    def record_retry(self):
        """Records a retry attempt."""
        self.retry_attempts += 1
        logger.info("Task retry attempt recorded.")

    def record_ssim(self, ssim: float):
        """Records SSIM (Structural Similarity Index Measure) estimation."""
        self.ssim_estimations.append(ssim)
        logger.info(f"SSIM estimation recorded: {ssim:.4f}")

    def get_dashboard_metrics(self) -> Dict:
        """Returns aggregated metrics for the admin OS."""
        avg_gen = sum(self.generation_times) / max(1, len(self.generation_times))
        avg_exp = sum(self.export_times) / max(1, len(self.export_times))
        avg_vram_eff = sum(self.vram_efficiency_ratios) / max(1, len(self.vram_efficiency_ratios)) if self.vram_efficiency_ratios else 1.0
        avg_ssim = sum(self.ssim_estimations) / max(1, len(self.ssim_estimations)) if self.ssim_estimations else 0.95
        
        failure_rate = (self.failed_tasks / max(1, self.total_processed)) * 100
        retry_rate = (self.retry_attempts / max(1, self.total_processed)) * 100
        
        return {
            "average_generation_sec": round(avg_gen, 2),
            "average_export_sec": round(avg_exp, 2),
            "average_vram_efficiency_ratio": round(avg_vram_eff, 2),
            "average_ssim_estimation": round(avg_ssim, 4),
            "failure_rate_percent": round(failure_rate, 2),
            "retry_rate_percent": round(retry_rate, 2),
            "total_processed": self.total_processed,
            "status": "Healthy" if failure_rate < 5 else "Degraded"
        }

# Global instance for the worker nodes
global_benchmarker = PerformanceBenchmarker()
