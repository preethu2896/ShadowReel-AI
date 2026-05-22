import logging
from typing import Dict

logger = logging.getLogger(__name__)

class VisualDNAEngine:
    """
    Maintains a persistent visual identity profile across an entire project.
    Ensures that framing styles, color palettes, and lens characteristics stay consistent.
    """
    def __init__(self, project_id: str):
        self.project_id = project_id
        
    def generate_dna_profile(self, style_mode: str) -> Dict:
        """
        Creates the persistent DNA for the film.
        """
        logger.info(f"Generating Visual DNA for project {self.project_id} with style {style_mode}")
        
        # In a real app, this would use an LLM or pre-computed embeddings matrix
        if "Dark" in style_mode or "Noir" in style_mode:
            return {
                "color_palette": ["#0F172A", "#1E293B", "#38BDF8"],
                "lighting_pattern": "high contrast, low key, volumetric fog",
                "lens_emulation": "anamorphic 35mm, subtle chromatic aberration",
                "particle_system": "floating dust motes, heavy rain"
            }
        elif "War" in style_mode or "Historical" in style_mode:
            return {
                "color_palette": ["#451A03", "#78350F", "#D97706"],
                "lighting_pattern": "harsh sunlight, dusty atmosphere",
                "lens_emulation": "vintage 16mm film, heavy grain, vignetting",
                "particle_system": "falling ash, smoke plumes"
            }
        else:
            return {
                "color_palette": ["#020617", "#334155", "#F8FAFC"],
                "lighting_pattern": "soft diffused lighting, cinematic rim light",
                "lens_emulation": "spherical 50mm, shallow depth of field",
                "particle_system": "clean air, subtle lens flare"
            }
            
    def get_prompt_injection(self, dna: Dict) -> str:
        """Returns the specific string modifiers to inject into ComfyUI prompts."""
        return f"{dna['lighting_pattern']}, {dna['lens_emulation']}"
        
    def cleanup_prompt(self, raw_prompt: str) -> str:
        """
        Automatic Prompt Cleanup.
        Removes contradictory styling tags, trims bloated sentences, and ensures the 
        final prompt is optimized for FLUX/SDXL embedding spaces.
        """
        clean = raw_prompt.lower()
        # Remove common anti-patterns
        anti_patterns = ["ugly", "bad anatomy", "poorly drawn", "text", "watermark", "blurry"]
        for ap in anti_patterns:
            clean = clean.replace(ap, "")
            
        # Ensure cinematic prefix
        if "cinematic" not in clean:
            clean = f"cinematic, {clean}"
            
        # Clean up whitespace
        clean = " ".join(clean.split())
        return clean.strip(", ")
