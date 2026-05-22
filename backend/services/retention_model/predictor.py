import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class RetentionPredictionModel:
    """
    Predicts audience drop-off points, emotional fatigue, and hook effectiveness.
    Analyzes the script and visual pacing to generate retention heatmaps.
    Optimized for both long-form documentaries and viral shorts.
    """
    def __init__(self, script: str, pacing_curve: List[float], is_short_form: bool = False):
        self.script = script
        self.pacing_curve = pacing_curve
        self.is_short_form = is_short_form

    def evaluate_hook_effectiveness(self) -> float:
        """Evaluates the first 3 seconds for viral short retention (Hook-first pacing)."""
        if not self.pacing_curve or len(self.pacing_curve) == 0:
            return 0.0
        # In shorts, the initial tension/pacing must be extremely high
        initial_tension = sum(self.pacing_curve[:2]) / max(1, len(self.pacing_curve[:2]))
        hook_score = min(1.0, initial_tension * 1.5)
        logger.info(f"RetentionModel: Hook effectiveness evaluated at {hook_score:.1%}")
        return hook_score

    def generate_retention_heatmap(self) -> Dict:
        """
        Maps out potential audience drop-off zones based on pacing stagnation.
        Applies different tolerances for short-form vs long-form content.
        """
        logger.info("RetentionModel: Analyzing narrative for viewer drop-off probabilities.")
        
        heatmap = []
        drop_off_risk = 0.0
        stagnation_tolerance = 0.02 if self.is_short_form else 0.05
        
        for i, tension in enumerate(self.pacing_curve):
            # If tension is flat or low for too long, drop-off risk increases
            if i > 0 and abs(tension - self.pacing_curve[i-1]) < stagnation_tolerance:
                drop_off_risk += 0.25 if self.is_short_form else 0.15 # Shorts penalize stagnation heavier
            else:
                drop_off_risk = max(0.0, drop_off_risk - 0.1)
                
            heatmap.append({
                "scene_index": i,
                "tension": tension,
                "drop_off_probability": min(0.95, drop_off_risk)
            })
            
        hook_score = self.evaluate_hook_effectiveness()
        # Shorts heavily weight the hook score
        base_virality = 100 - (sum(h["drop_off_probability"] for h in heatmap) * (15 if self.is_short_form else 10))
        virality_score = (base_virality * 0.6) + (hook_score * 100 * 0.4) if self.is_short_form else base_virality
        
        return {
            "heatmap": heatmap,
            "virality_probability_score": max(1, int(virality_score)),
            "hook_effectiveness": f"{hook_score:.1%}",
            "optimization_suggestions": [
                f"Scene {h['scene_index']} has high drop-off risk ({h['drop_off_probability']:.1%}). " + 
                ("Suggest using a fast-cut transition or zoom-in." if self.is_short_form else "Suggest adding a B-roll cutaway or cinematic bass impact.")
                for h in heatmap if h["drop_off_probability"] > (0.4 if self.is_short_form else 0.5)
            ]
        }
