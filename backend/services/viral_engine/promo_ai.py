import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class AutonomousPromotionAI:
    """
    Autonomously creates teaser campaigns, generates social snippets, 
    and optimizes promotional pacing based on the main documentary content.
    """
    def __init__(self, project_id: str):
        self.project_id = project_id

    def generate_teaser_campaign(self, tension_curve: List[float], scenes: List[Dict]) -> Dict:
        """
        Extracts the highest-tension scenes and splices them into a rapid trailer format.
        """
        logger.info(f"Promo AI: Generating teaser campaign for project {self.project_id}")
        
        # Find peak tension scenes
        peak_scenes = []
        for i, tension in enumerate(tension_curve):
            if tension > 0.8 and i < len(scenes):
                peak_scenes.append(scenes[i])
                
        # Limit to top 3 for a teaser
        teaser_scenes = peak_scenes[:3] if len(peak_scenes) >= 3 else scenes[:3]
        
        return {
            "campaign_type": "High-Suspense TikTok Snippet",
            "teaser_scenes": [s.get('id') for s in teaser_scenes],
            "audio_overlay": "Inception-style bass horn drop",
            "social_copy": "You won't believe what they found... #Mystery #Documentary"
        }
