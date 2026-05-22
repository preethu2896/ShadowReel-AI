import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class ThumbnailOptimizationEngine:
    """
    Improves title readability, face composition, cinematic contrast, 
    CTR-focused framing, and emotional expression enhancement.
    Generates text-safe zones and A/B variants.
    """
    def __init__(self, project_title: str):
        self.project_title = project_title

    def generate_optimized_variants(self, base_scene_prompt: str) -> List[Dict]:
        """
        Takes a base scene prompt and optimizes it specifically for a YouTube thumbnail.
        Generates multiple A/B variants for testing.
        """
        logger.info(f"Thumbnail Engine: Optimizing thumbnail variants for {self.project_title}")
        
        base_modifiers = "close up face, hyper detailed, high contrast cinematic lighting, sharp focus, 8k, CTR-focused framing, emotional expression enhancement"
        
        return [
            {
                "variant": "High Emotion (A)",
                "prompt": f"{base_scene_prompt}, {base_modifiers}, intense emotional expression, wide eyes, dramatic side lighting, subject placed on left third",
                "safe_zone": "right_half_text_safe",
                "overlay_style": "bold_glow"
            },
            {
                "variant": "Mystery Contrast (B)",
                "prompt": f"{base_scene_prompt}, {base_modifiers}, silhouette lighting, glowing eyes, dark cinematic shadow, centralized composition",
                "safe_zone": "top_third_text_safe",
                "overlay_style": "minimalist_shadow"
            },
            {
                "variant": "Action Impact (C)",
                "prompt": f"{base_scene_prompt}, {base_modifiers}, dynamic motion blur, high action, bright colors, dutch angle",
                "safe_zone": "bottom_third_text_safe",
                "overlay_style": "heavy_outline"
            }
        ]

    def get_overlay_parameters(self, overlay_style: str) -> Dict:
        """
        Calculates optimal font colors, cinematic overlays, and shadows for readability.
        """
        styles = {
            "bold_glow": {
                "font_family": "Impact or bold sans-serif",
                "text_color": "#FFFFFF",
                "drop_shadow": "0px 0px 20px rgba(255,200,0,0.8)",
                "contrast_boost": 1.4,
                "cinematic_overlay": "vignette_heavy"
            },
            "minimalist_shadow": {
                "font_family": "Cinematic Serif",
                "text_color": "#F0F0F0",
                "drop_shadow": "10px 10px 25px rgba(0,0,0,1.0)",
                "contrast_boost": 1.2,
                "cinematic_overlay": "dark_gradient_top"
            },
            "heavy_outline": {
                "font_family": "Thick Sans",
                "text_color": "#FFEA00",
                "drop_shadow": "0px 0px 5px #000000, 5px 5px 15px rgba(0,0,0,0.9)",
                "contrast_boost": 1.5,
                "cinematic_overlay": "lens_flare_corner"
            }
        }
        return styles.get(overlay_style, styles["bold_glow"])

    def calculate_text_safe_zones(self, resolution_w: int, resolution_h: int) -> Dict:
        """Returns coordinate boundaries for automatic text-safe zones to avoid UI overlap."""
        return {
            "right_half_text_safe": {"x_start": int(resolution_w * 0.5), "y_start": int(resolution_h * 0.1), "x_end": int(resolution_w * 0.95), "y_end": int(resolution_h * 0.8)},
            "top_third_text_safe": {"x_start": int(resolution_w * 0.1), "y_start": int(resolution_h * 0.05), "x_end": int(resolution_w * 0.9), "y_end": int(resolution_h * 0.35)},
            "bottom_third_text_safe": {"x_start": int(resolution_w * 0.1), "y_start": int(resolution_h * 0.65), "x_end": int(resolution_w * 0.9), "y_end": int(resolution_h * 0.95)}
        }

    def refine_thumbnail_image(self, base_image_path: str, text: str, style: str) -> str:
        """
        Enhances the thumbnail image using PIL:
        1. Boosts contrast and saturation.
        2. Draws a high-impact, mobile-safe styled text overlay.
        Saves the result to a new file and returns the path.
        """
        from PIL import Image, ImageEnhance, ImageDraw, ImageFont
        import os
        from pathlib import Path
        
        logger.info(f"Refining thumbnail image: {base_image_path} with text: {text}")
        
        img = Image.open(base_image_path)
        w, h = img.size
        
        # 1. Enhance Contrast and Saturation
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(1.3)  # boost contrast by 30%
        
        color_enhancer = ImageEnhance.Color(img)
        img = color_enhancer.enhance(1.2)  # boost saturation by 20%
        
        # 2. Draw styled text overlay
        draw = ImageDraw.Draw(img)
        
        params = self.get_overlay_parameters(style)
        safe_zones = self.calculate_text_safe_zones(w, h)
        
        zone_name = "right_half_text_safe"
        if style == "minimalist_shadow":
            zone_name = "top_third_text_safe"
        elif style == "heavy_outline":
            zone_name = "bottom_third_text_safe"
            
        zone = safe_zones.get(zone_name, safe_zones["right_half_text_safe"])
        
        # Try loading a bold font, fallback to default
        font = None
        font_path = "C:/Windows/Fonts/arialbd.ttf"
        font_size = int(h * 0.08)  # dynamic size based on height
        
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, font_size)
            except Exception:
                pass
                
        if font is None:
            font = ImageFont.load_default()
            
        # Helper to find text width safely across all Pillow versions
        def get_line_width(line_text, draw_obj, font_obj):
            try:
                bbox = draw_obj.textbbox((0, 0), line_text, font=font_obj)
                return bbox[2] - bbox[0]
            except AttributeError:
                try:
                    return font_obj.getlength(line_text)
                except AttributeError:
                    return draw_obj.textsize(line_text, font=font_obj)[0]
            
        # Draw text wrapping logic
        words = text.split()
        lines = []
        current_line = []
        max_width = zone["x_end"] - zone["x_start"]
        
        for word in words:
            test_line = " ".join(current_line + [word])
            test_width = get_line_width(test_line, draw, font)
                
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
            
        # Draw each line
        text_color = params.get("text_color", "#FFFFFF")
        if text_color.startswith('#'):
            r = int(text_color[1:3], 16)
            g = int(text_color[3:5], 16)
            b = int(text_color[5:7], 16)
            color_tuple = (r, g, b)
        else:
            color_tuple = (255, 255, 255)
            
        y = zone["y_start"]
        line_height = int(font_size * 1.2)
        
        for line in lines:
            # Drop shadow / outline styling
            if style == "heavy_outline":
                outline_color = (0, 0, 0)
                outline_w = 2
                for dx in [-outline_w, 0, outline_w]:
                    for dy in [-outline_w, 0, outline_w]:
                        if dx != 0 or dy != 0:
                            draw.text((zone["x_start"] + dx, y + dy), line, font=font, fill=outline_color)
            elif style == "bold_glow":
                glow_color = (255, 200, 0)
                glow_w = 4
                for dx in [-glow_w, 0, glow_w]:
                    for dy in [-glow_w, 0, glow_w]:
                        if dx != 0 or dy != 0:
                            draw.text((zone["x_start"] + dx, y + dy), line, font=font, fill=glow_color)
            elif style == "minimalist_shadow":
                draw.text((zone["x_start"] + 3, y + 3), line, font=font, fill=(0, 0, 0))
                
            # Draw main text
            draw.text((zone["x_start"], y), line, font=font, fill=color_tuple)
            y += line_height
            if y + line_height > zone["y_end"]:
                break
                
        base_path = Path(base_image_path)
        out_name = f"{base_path.stem}_refined{base_path.suffix}"
        out_path = base_path.parent / out_name
        img.save(out_path)
        
        logger.info(f"Refined thumbnail saved to: {out_path}")
        return str(out_path)
