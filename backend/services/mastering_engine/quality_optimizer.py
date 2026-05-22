import logging
from typing import Dict, List, Any
import re

logger = logging.getLogger(__name__)

class OutputQualityOptimizer:
    """
    Optimizes documentary output quality including temporal consistency, 
    face consistency, motion smoothness, scene coherence, and cinematic realism.
    """
    def __init__(self):
        self.min_scene_duration = 2.0
        self.max_scene_duration = 10.0
        
    def cleanup_prompt(self, prompt: str) -> str:
        """Automatically cleans up user prompts to ensure cinematic realism."""
        # Remove contradictory terms
        prompt = re.sub(r'(?i)\b(ugly|bad anatomy|blurry|low res|watermark)\b', '', prompt)
        # Ensure cinematic keywords are present
        if "cinematic" not in prompt.lower():
             prompt += ", highly detailed, cinematic lighting, 8k resolution"
        # Normalize spaces
        prompt = re.sub(r'\s+', ' ', prompt).strip(', ')
        logger.info(f"Cleaned prompt for quality optimization.")
        return prompt

    def smooth_transitions(self, timeline: List[Dict], project_style: str = "Cinematic", is_short: bool = False) -> List[Dict]:
        """Applies transition smoothing and types between scenes for coherence."""
        for i in range(len(timeline) - 1):
            current_scene = timeline[i]
            next_scene = timeline[i+1]
            
            curr_pacing = current_scene.get('pacing', 'medium')
            next_pacing = next_scene.get('pacing', 'medium')
            
            # Default transitions
            if is_short:
                # Shorts usually use fast hard cuts for retention
                if curr_pacing == 'slow' and next_pacing == 'slow':
                    current_scene['transition'] = 'crossfade'
                else:
                    current_scene['transition'] = 'hard_cut'
            else:
                # Documentary / cinematic defaults
                if curr_pacing == 'slow' or next_pacing == 'slow':
                    current_scene['transition'] = 'crossfade'
                elif "Trailer" in project_style:
                    # Trailers benefit from dramatic fades/hard cuts
                    current_scene['transition'] = 'fade' if curr_pacing == 'fast' else 'hard_cut'
                else:
                    current_scene['transition'] = 'crossfade'
            
            # Allow custom stylistic transitions for specific visual hooks
            if current_scene.get('transition') == 'crossfade' and "Action" in project_style:
                current_scene['transition'] = 'wipeleft'

            logger.debug(f"Transition between scene {i} and {i+1} set to: {current_scene.get('transition')}")
                
        return timeline

    def optimize_pacing(self, timeline: List[Dict], narration_speed: float, tension_curve: List[float] = None, is_short: bool = False) -> List[Dict]:
        """Balances scene durations based on narration pacing, emotional arc, and shorts format."""
        for i, scene in enumerate(timeline):
            base_duration = scene.get('duration', 5.0)
            
            # Determine intensity/tension for this scene
            intensity = tension_curve[i] if tension_curve and i < len(tension_curve) else 0.5
            
            # Classify scene pacing based on intensity
            if intensity > 0.7:
                scene['pacing'] = 'fast'
            elif intensity < 0.4:
                scene['pacing'] = 'slow'
            else:
                scene['pacing'] = 'medium'
            
            # Adaptive scene duration balancing based on pacing & style
            if is_short:
                # Shorts need to be quick
                if scene['pacing'] == 'fast':
                    base_duration = 2.0
                elif scene['pacing'] == 'slow':
                    base_duration = 4.0
                else:
                    base_duration = 3.0
            else:
                # Normal documentaries
                if scene['pacing'] == 'fast':
                    base_duration = 3.5
                elif scene['pacing'] == 'slow':
                    base_duration = 7.5
                else:
                    base_duration = 5.0
            
            # Adjust duration slightly for narration speed
            if narration_speed > 1.2:  # Fast narration
                base_duration *= 0.85
            elif narration_speed < 0.8: # Slow narration
                base_duration *= 1.15
                
            # Clamp to safe limits
            scene['duration'] = max(self.min_scene_duration, min(self.max_scene_duration, base_duration))
            
        logger.info("Optimized timeline pacing for temporal consistency.")
        return timeline
        
    def balance_soundtrack(self, audio_tracks: List[Dict]) -> List[Dict]:
        """Balances soundtrack volume to ensure narration clarity."""
        for track in audio_tracks:
            if track.get('type') == 'narration':
                track['volume'] = 1.0 # Maximize narration clarity
            elif track.get('type') == 'background_music':
                track['volume'] = 0.25 # Duck BGM for subtitle readability and clarity
                
        return audio_tracks

quality_optimizer = OutputQualityOptimizer()

