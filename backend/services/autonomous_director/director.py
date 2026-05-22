import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class AutonomousCinematicDirector:
    """
    Core AI logic that autonomously dictates scene compositions,
    camera movement, and rhythm pacing based on emotional curves.
    """
    def __init__(self, project_id: str):
        self.project_id = project_id

    def generate_scene_logic(self, scene_index: int, total_scenes: int, emotion_intensity: float) -> Dict:
        """
        Determines exactly how a scene should look and move.
        """
        logger.info(f"Director: Planning Scene {scene_index + 1}/{total_scenes} (Intensity: {emotion_intensity})")
        
        # Adaptive Scene Duration Balancing
        # Higher tension scenes should be shorter and punchier.
        base_duration = 5.0
        if emotion_intensity < 0.4:
            movement = "slow cinematic pan, graceful ease-in"
            composition = "wide establishing shot"
            transition = "fade to black"
            optimal_duration = base_duration * 1.5 # 7.5 seconds
        elif emotion_intensity < 0.7:
            movement = "steady track forward, parallax depth"
            composition = "medium shot, rule of thirds"
            transition = "match cut"
            optimal_duration = base_duration * 1.0 # 5.0 seconds
        else:
            movement = "handheld shake, rapid zoom"
            composition = "extreme close-up, dramatic angle"
            transition = "glitch flash cut"
            optimal_duration = base_duration * 0.6 # 3.0 seconds
            
        return {
            "camera_movement": movement,
            "composition": composition,
            "transition": transition,
            "optimal_duration_sec": optimal_duration,
            "pacing_speed": "fast" if emotion_intensity > 0.7 else "slow"
        }
