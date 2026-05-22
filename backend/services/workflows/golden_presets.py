import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class GoldenPresetsManager:
    """
    Manages reusable, production-ready cinematic workflow presets for ShadowReel AI.
    These are highly tuned configurations that guarantee high-quality generation.
    """
    PRESETS = {
        "ancient_history": {
            "name": "Ancient History",
            "prompt_template": "cinematic documentary footage, ancient civilization, dust motes, warm sunset lighting, historically accurate, highly detailed, 8k resolution",
            "soundtrack_profile": "Hans Zimmer style, deep cellos, slow tribal percussion",
            "narration_pacing": "slow_authoritative",
            "transition_preset": "slow_crossfade",
            "thumbnail_styles": "cinematic_portrait, high_contrast, gold_typography",
            "subtitle_styling": "classic_serif, yellow_tint, subtle_shadow",
            "export_configuration": "4k_24fps_prores",
            "camera_movement": "slow_pan_right",
            "lut_profile": "warm_golden_hour"
        },
        "war_documentary": {
            "name": "War Documentary",
            "prompt_template": "historical war footage style, grainy film, desaturated colors, gritty realism, smoke and debris, intense cinematic lighting, 4k",
            "soundtrack_profile": "Heavy brass, snare rolls, melancholic strings",
            "narration_pacing": "grave_serious",
            "transition_preset": "hard_cut, flash_frame",
            "thumbnail_styles": "gritty_action, desaturated, bold_impact_typography",
            "subtitle_styling": "bold_sans_serif, white, heavy_shadow",
            "export_configuration": "4k_24fps_h265_high_bitrate",
            "camera_movement": "handheld_shake",
            "lut_profile": "bleach_bypass"
        },
        "crime_mystery": {
            "name": "Crime & Mystery",
            "prompt_template": "true crime documentary style, gritty realism, cold fluorescent lighting, shallow depth of field, forensic photography style, 4k",
            "soundtrack_profile": "Minimalist piano, low drone, ticking clock tension",
            "narration_pacing": "deliberate_suspenseful",
            "transition_preset": "hard_cut",
            "thumbnail_styles": "red_tape, forensic_macro, dark_vignette",
            "subtitle_styling": "typewriter_font, white, high_contrast_background",
            "export_configuration": "4k_30fps_h264",
            "camera_movement": "static_locked_off",
            "lut_profile": "cold_desaturated"
        },
        "horror_storytelling": {
            "name": "Horror Storytelling",
            "prompt_template": "found footage style, low light, disturbing atmosphere, film grain, creepy shadows, high contrast, claustrophobic framing, 4k",
            "soundtrack_profile": "Atmos drone, sudden stingers, whispering voices",
            "narration_pacing": "whispered_tense",
            "transition_preset": "glitch_fade",
            "thumbnail_styles": "jump_scare_frame, high_contrast_red_text, extreme_vignette",
            "subtitle_styling": "distressed_font, blood_red, flickering_opacity",
            "export_configuration": "1080p_24fps_grainy",
            "camera_movement": "creeping_zoom_in",
            "lut_profile": "green_tint_dark"
        },
        "space_documentary": {
            "name": "Space Documentary",
            "prompt_template": "astrophotography, deep space, nebula, awe-inspiring, cosmic scale, stark lighting, imax 70mm, 8k",
            "soundtrack_profile": "Ambient electronic, ethereal choir, vast reverb",
            "narration_pacing": "slow_wonder",
            "transition_preset": "fade_to_black",
            "thumbnail_styles": "cosmic_vista, bright_stars, sleek_modern_typography",
            "subtitle_styling": "clean_sans, cyan_glow, no_background",
            "export_configuration": "8k_60fps_hdr",
            "camera_movement": "slow_orbit",
            "lut_profile": "high_dynamic_range"
        },
        "cyberpunk_narrative": {
            "name": "Cyberpunk Narrative",
            "prompt_template": "neon lit, cyberpunk aesthetic, dark rainy city streets, volumetric fog, anamorphic lens flare, high contrast, cinematic, 8k",
            "soundtrack_profile": "Synthwave, heavy bass, analog synthesizer pulses",
            "narration_pacing": "fast_urgent",
            "transition_preset": "glitch_cut",
            "thumbnail_styles": "neon_glow, dynamic_angle, glitch_typography",
            "subtitle_styling": "monospaced, neon_pink, glow_effect",
            "export_configuration": "4k_60fps_h265",
            "camera_movement": "dutch_angle_push_in",
            "lut_profile": "neon_high_contrast"
        },
        "conspiracy_documentary": {
            "name": "Conspiracy Documentary",
            "prompt_template": "classified documents, redacted text, hidden camera aesthetic, dark web style, high contrast, uneasy angles, 4k",
            "soundtrack_profile": "Pulsing synth bass, distorted radio static, tense ticking",
            "narration_pacing": "rapid_paranoid",
            "transition_preset": "static_glitch",
            "thumbnail_styles": "redacted_tape, glowing_red_eyes, warning_typography",
            "subtitle_styling": "courier_new, green_phosphor, digital_glitch_effect",
            "export_configuration": "1080p_30fps_h264",
            "camera_movement": "security_cam_pan",
            "lut_profile": "green_matrix"
        },
        "ai_future_documentary": {
            "name": "AI Future Documentary",
            "prompt_template": "clean futuristic laboratory, glowing neural networks, pristine white and blue, high tech, optimistic but sterile, 8k",
            "soundtrack_profile": "Clean digital arpeggios, sparse electronic beats, optimistic swells",
            "narration_pacing": "calm_objective",
            "transition_preset": "smooth_wipe",
            "thumbnail_styles": "holographic_interface, sterile_white, minimal_typography",
            "subtitle_styling": "futuristic_sans, ice_blue, semi_transparent_bg",
            "export_configuration": "4k_60fps_prores",
            "camera_movement": "drone_smooth_flythrough",
            "lut_profile": "clean_clinical"
        },
        "dark_philosophy": {
            "name": "Dark Philosophy",
            "prompt_template": "surreal landscapes, abstract shapes, deep shadows, melancholic atmosphere, liminal spaces, highly artistic, 4k",
            "soundtrack_profile": "Slow cello solos, ambient wind noise, silence",
            "narration_pacing": "slow_contemplative",
            "transition_preset": "long_fade",
            "thumbnail_styles": "abstract_silhouette, monochrome, elegant_serif",
            "subtitle_styling": "thin_serif, muted_grey, elegant_fade_in",
            "export_configuration": "4k_24fps_h265",
            "camera_movement": "slow_pull_back",
            "lut_profile": "monochrome_high_contrast"
        },
        "psychological_thriller": {
            "name": "Psychological Thriller",
            "prompt_template": "distorted reality, mirrors, uneasy framing, harsh shadows, claustrophobic, unsettling atmosphere, 4k",
            "soundtrack_profile": "Dissonant strings, heartbeats, low rumbling",
            "narration_pacing": "erratic_intense",
            "transition_preset": "jump_cut",
            "thumbnail_styles": "split_face, distorted_vision, psychological_typography",
            "subtitle_styling": "messy_handwriting, jagged_edges, rapid_appearance",
            "export_configuration": "4k_24fps_h265",
            "camera_movement": "vertigo_effect",
            "lut_profile": "sickly_green_yellow"
        }
    }

    @classmethod
    def get_preset(cls, preset_id: str) -> Dict:
        """Retrieves a golden preset by ID."""
        preset = cls.PRESETS.get(preset_id)
        if not preset:
            logger.warning(f"Preset {preset_id} not found, defaulting to crime_mystery")
            return cls.PRESETS["crime_mystery"]
        return preset
        
    @classmethod
    def list_presets(cls) -> List[Dict]:
        """Lists all available golden presets."""
        return [{"id": k, "name": v["name"]} for k, v in cls.PRESETS.items()]
