import logging
import time
from typing import Dict, List
from collections import deque

logger = logging.getLogger(__name__)

class ProductionBenchmarkSuite:
    """
    Real benchmark suite for tracking platform execution health.
    Tracks: image generation speed, video render speed, VRAM usage, 
    worker throughput, export times, queue latency, failure recovery.
    """
    def __init__(self):
        self.metrics = {
            "image_generation_times": deque(maxlen=200),
            "video_render_times": deque(maxlen=200),
            "export_times": deque(maxlen=100),
            "queue_latency": deque(maxlen=100),
            "vram_efficiency_ratios": deque(maxlen=200),
            "ssim_estimations": deque(maxlen=200),
        }
        self.failed_tasks = 0
        self.recovered_tasks = 0
        self.total_processed = 0
        self.start_time = time.time()

    def record_latency(self, enqueue_time: float):
        latency = time.time() - enqueue_time
        self.metrics["queue_latency"].append(latency)

    def record_task(self, task_type: str, duration_sec: float, success: bool, recovered: bool = False):
        """Records telemetry for an executed job."""
        self.total_processed += 1
        
        if recovered:
            self.recovered_tasks += 1
            
        if not success:
            self.failed_tasks += 1
            logger.error(f"Benchmark: {task_type} failed after {duration_sec:.2f}s.")
            return
            
        if task_type in self.metrics:
            self.metrics[task_type].append(duration_sec)

    def record_vram_efficiency(self, ratio: float):
        """Records VRAM efficiency ratio."""
        self.metrics["vram_efficiency_ratios"].append(ratio)
        logger.info(f"Production Benchmark: VRAM efficiency ratio recorded: {ratio:.2f}")

    def record_ssim(self, ssim: float):
        """Records SSIM estimation."""
        self.metrics["ssim_estimations"].append(ssim)
        logger.info(f"Production Benchmark: SSIM estimation recorded: {ssim:.4f}")

    def get_dashboard_metrics(self) -> Dict:
        """Returns aggregated metrics for the admin analytics dashboard."""
        
        def _avg(metric_list):
            return sum(metric_list) / max(1, len(metric_list))
            
        failure_rate = (self.failed_tasks / max(1, self.total_processed)) * 100
        recovery_rate = (self.recovered_tasks / max(1, self.failed_tasks)) * 100 if self.failed_tasks > 0 else 100.0
        retry_rate = (self.recovered_tasks / max(1, self.total_processed)) * 100
        uptime_hours = (time.time() - self.start_time) / 3600
        
        avg_vram_eff = _avg(self.metrics["vram_efficiency_ratios"]) if self.metrics["vram_efficiency_ratios"] else 1.0
        avg_ssim = _avg(self.metrics["ssim_estimations"]) if self.metrics["ssim_estimations"] else 0.95
        
        # Pull latest VRAM usage if available
        current_vram_mb = 0
        try:
            from services.comfy_cache.vram_manager import vram_manager
            current_vram_mb = vram_manager.current_vram_usage_mb
        except Exception:
            pass
        
        return {
            "average_image_gen_sec": round(_avg(self.metrics["image_generation_times"]), 2),
            "average_video_render_sec": round(_avg(self.metrics["video_render_times"]), 2),
            "average_export_sec": round(_avg(self.metrics["export_times"]), 2),
            "average_queue_latency_sec": round(_avg(self.metrics["queue_latency"]), 2),
            "average_vram_efficiency_ratio": round(avg_vram_eff, 2),
            "average_ssim_estimation": round(avg_ssim, 4),
            "failure_rate_percent": round(failure_rate, 2),
            "recovery_rate_percent": round(recovery_rate, 2),
            "retry_rate_percent": round(retry_rate, 2),
            "vram_usage_mb": current_vram_mb,
            "total_processed": self.total_processed,
            "worker_throughput_per_hour": round(self.total_processed / max(0.1, uptime_hours), 2),
            "status": "Healthy" if failure_rate < 5 else "Degraded"
        }

# Global instance for the worker nodes
production_benchmarker = ProductionBenchmarkSuite()
