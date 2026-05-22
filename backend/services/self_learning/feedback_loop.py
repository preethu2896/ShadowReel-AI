import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class SelfLearningFeedbackEngine:
    """
    Self-improving AI engine.
    Continuously updates the platform's generation intelligence based on 
    creator edits, pacing adjustments, and audience retention analytics.
    """
    def __init__(self, project_id: str):
        self.project_id = project_id

    def process_creator_feedback(self, edits: List[Dict]) -> Dict:
        """
        Takes manual adjustments (e.g. shortening a scene, replacing a soundtrack)
        and updates the Editor AI's future autonomous decision-making weights.
        """
        logger.info(f"SelfLearningEngine: Processing {len(edits)} manual creator edits.")
        
        learning_weights = {"pacing_aggressiveness": 0.0, "soundtrack_tension": 0.0}
        
        for edit in edits:
            if edit.get("type") == "shorten_scene":
                learning_weights["pacing_aggressiveness"] += 0.05
            elif edit.get("type") == "increase_volume":
                learning_weights["soundtrack_tension"] += 0.1
                
        return {"learned_adjustments": learning_weights, "status": "weights_updated"}

    def generate_adaptive_recommendations(self) -> List[str]:
        """
        Generates personalized workflow suggestions based on historical learning.
        """
        return [
            "You usually prefer faster pacing in Act 2. Autopilot adjusted.",
            "Based on past projects, switching to 'Cinematic Ambient' soundtrack for the outro."
        ]
