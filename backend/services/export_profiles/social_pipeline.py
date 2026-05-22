import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SocialContentPipeline:
    """
    Dedicated workflows for YouTube Shorts, TikTok, and Instagram Reels.
    Focuses on retention optimization, hook-first pacing, and mobile-safe framing.
    """
    
    PLATFORM_SPECS = {
        "youtube_shorts": {
            "aspect_ratio": "9:16",
            "resolution": "1080x1920",
            "max_duration_sec": 60,
            "hook_duration_sec": 3.0,
            "subtitle_safe_zone": "middle_center",
            "pacing": "fast_cut",
        },
        "tiktok": {
            "aspect_ratio": "9:16",
            "resolution": "1080x1920",
            "max_duration_sec": 180,
            "hook_duration_sec": 2.0, # Faster hook for TikTok
            "subtitle_safe_zone": "middle_center_high",
            "pacing": "hyper_fast",
        },
        "instagram_reels": {
            "aspect_ratio": "9:16",
            "resolution": "1080x1920",
            "max_duration_sec": 90,
            "hook_duration_sec": 3.0,
            "subtitle_safe_zone": "middle_center",
            "pacing": "aesthetic_smooth",
        }
    }

    def optimize_for_platform(self, project_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Applies platform-specific retention optimizations and framing."""
        if platform not in self.PLATFORM_SPECS:
            logger.warning(f"Platform {platform} not supported. Defaulting to youtube_shorts.")
            platform = "youtube_shorts"
            
        specs = self.PLATFORM_SPECS[platform]
        
        optimized_project = project_data.copy()
        
        # Apply Mobile-safe framing
        optimized_project['resolution'] = specs['resolution']
        optimized_project['aspect_ratio'] = specs['aspect_ratio']
        
        # Subtitle burn-in with safe zones
        optimized_project['subtitles'] = {
            "enabled": True,
            "burn_in": True,
            "safe_zone": specs['subtitle_safe_zone'],
            "style": "bold_impact" # high retention style
        }
        
        # Hook-first pacing adjustments
        if 'timeline' in optimized_project and len(optimized_project['timeline']) > 0:
            first_scene = optimized_project['timeline'][0]
            first_scene['duration'] = min(first_scene.get('duration', 5.0), specs['hook_duration_sec'])
            first_scene['transition'] = specs['pacing']
            
        logger.info(f"Optimized content pipeline for {platform} with {specs['pacing']} pacing.")
        return optimized_project

social_pipeline = SocialContentPipeline()
