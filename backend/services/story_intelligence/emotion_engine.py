import logging
import math
from typing import List

logger = logging.getLogger(__name__)

class StoryIntelligenceEngine:
    """
    Calculates emotional tension curves for a script to dictate pacing and music intensity.
    """
    def __init__(self, script: str):
        self.script = script
        self.paragraphs = [p.strip() for p in script.split("\n") if p.strip()]
        
    def generate_tension_curve(self) -> List[float]:
        """
        Maps the emotional intensity from 0.0 to 1.0 across all scenes.
        Creates a standard cinematic 3-act structure curve.
        """
        total = len(self.paragraphs)
        if total == 0:
            return []
            
        curve = []
        for i in range(total):
            progress = i / max(1, (total - 1))
            # Sine wave simulation for tension: peaks around 80% of the film (climax)
            # base formula: f(x) = sin(x * pi) * x + 0.2
            intensity = math.sin(progress * math.pi) * progress + 0.2
            # Cap between 0.1 and 1.0
            intensity = max(0.1, min(1.0, intensity))
            curve.append(round(intensity, 2))
            
        logger.info(f"Generated Emotional Tension Curve: {curve}")
        return curve
