"""
ShadowReel AI — Cinematic Prompt Enhancer
Rule-based prompt enhancement system for professional cinematic output.
No external AI dependencies required.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────────────────────────
# Preset Definitions
# ─────────────────────────────────────────────────────────────

@dataclass
class CinematicPreset:
    name: str
    label: str
    description: str
    positive_suffix: str
    negative_additions: str
    cfg: float
    steps: int
    sampler: str
    scheduler: str
    style_tag: str
    # Optional theme keywords that auto-activate this preset
    trigger_keywords: list[str]


PRESETS: dict[str, CinematicPreset] = {
    "dark_documentary": CinematicPreset(
        name="dark_documentary",
        label="Dark Documentary",
        description="Raw, gritty investigative footage feel",
        positive_suffix=(
            "shot on RED V-Raptor, Cooke S4 lenses, dark documentary photography, "
            "investigative journalism, handheld camera, natural harsh lighting, raw organic film grain, "
            "unfiltered truth, shadow detail, photojournalism, 35mm, muted desaturated palette, moody atmosphere"
        ),
        negative_additions="colorful, bright, clean, polished, studio lighting, CGI",
        cfg=6.5,
        steps=28,
        sampler="euler",
        scheduler="karras",
        style_tag="Dark Documentary",
        trigger_keywords=["investigation", "crime", "mystery", "dark", "noir", "surveillance"],
    ),
    "war_archives": CinematicPreset(
        name="war_archives",
        label="War Archives",
        description="Historical wartime archival photography",
        positive_suffix=(
            "historical wartime archival photograph, shot on vintage 16mm Bell & Howell camera, "
            "1940s documentary, aged sepia film, military authenticity, heavy organic film grain, scratches, "
            "period-accurate detail, dramatic wartime lighting, photojournalism, intense atmosphere, vintage press photo"
        ),
        negative_additions="modern, colorful, CGI, clean, digital, fake, cartoon",
        cfg=7.0,
        steps=30,
        sampler="dpm_2",
        scheduler="karras",
        style_tag="War Archives",
        trigger_keywords=["war", "battle", "soldier", "military", "ww2", "wwii", "combat", "trench"],
    ),
    "cinematic_realism": CinematicPreset(
        name="cinematic_realism",
        label="Cinematic Realism",
        description="Hollywood-grade cinematic photography",
        positive_suffix=(
            "cinematic photography, shot on Arri Alexa LF, Zeiss Master Prime lenses, "
            "anamorphic flare, dramatic lighting, shallow depth of field, professional color grading, "
            "movie still, epic composition, cinematic atmosphere, golden hour, organic film grain, masterpiece"
        ),
        negative_additions="cartoon, illustration, anime, flat, low quality, blurry",
        cfg=7.5,
        steps=35,
        sampler="euler_ancestral",
        scheduler="karras",
        style_tag="Cinematic",
        trigger_keywords=["cinematic", "film", "movie", "dramatic", "epic", "scene"],
    ),
    "neo_noir": CinematicPreset(
        name="neo_noir",
        label="Neo Noir",
        description="Moody detective thriller aesthetic",
        positive_suffix=(
            "neo-noir film style, shot on Panavision Panaflex, anamorphic lens, "
            "chiaroscuro lighting, deep shadows, rain-soaked streets, neon reflections, "
            "high contrast black and white with color accents, 1950s detective aesthetic, "
            "cigarette smoke, venetian blind shadows, mystery, rich organic film grain"
        ),
        negative_additions="bright, cheerful, colorful, daytime, happy, flat",
        cfg=8.0,
        steps=32,
        sampler="dpm_2_ancestral",
        scheduler="karras",
        style_tag="Dark Noir",
        trigger_keywords=["noir", "detective", "mystery", "rain", "night", "shadow", "crime"],
    ),
    "analog_film": CinematicPreset(
        name="analog_film",
        label="Analog Film",
        description="Authentic analog film photography",
        positive_suffix=(
            "analog film photograph, shot on Leica M6, Summicron 35mm lens, 35mm Kodak Portra 400, "
            "rich organic film grain, light leaks, warm tones, slightly faded colors, vignette, "
            "authentic film texture, vintage photography, nostalgic atmosphere, organic imperfections"
        ),
        negative_additions="digital, clean, sharp, HDR, oversaturated, CGI",
        cfg=6.0,
        steps=25,
        sampler="euler",
        scheduler="normal",
        style_tag="Analog Film",
        trigger_keywords=["film", "analog", "vintage", "retro", "nostalgic", "kodak"],
    ),
    "horror_atmosphere": CinematicPreset(
        name="horror_atmosphere",
        label="Horror Atmosphere",
        description="Unsettling psychological horror aesthetic",
        positive_suffix=(
            "psychological horror atmosphere, shot on RED V-Raptor, Cooke lenses, deeply unsettling, "
            "dim cold lighting, fog and mist, desaturated palette, creeping dread, isolation, "
            "found footage aesthetic, shadows concealing, moonlight, desolate, harsh digital noise and organic grain"
        ),
        negative_additions="bright, cheerful, colorful, safe, warm, comfortable",
        cfg=8.5,
        steps=35,
        sampler="dpm_2",
        scheduler="karras",
        style_tag="Horror",
        trigger_keywords=["horror", "scary", "dark", "haunted", "creepy", "ghost", "abandoned"],
    ),
    "sci_fi_future": CinematicPreset(
        name="sci_fi_future",
        label="Sci-Fi Future",
        description="Futuristic science fiction concept art",
        positive_suffix=(
            "futuristic sci-fi concept art, shot on Hasselblad H6D-100c, sharp details, "
            "advanced technology, neon lighting, holographic displays, megastructures, "
            "cyberpunk influence, cinematic wide shot, hyperdetailed, 8K, volumetric lighting, alien world"
        ),
        negative_additions="ancient, historical, natural, organic, medieval, primitive",
        cfg=7.0,
        steps=30,
        sampler="euler",
        scheduler="karras",
        style_tag="Sci-Fi",
        trigger_keywords=["sci-fi", "future", "space", "robot", "cyberpunk", "neon", "tech", "alien"],
    ),
    "historical_reconstruction": CinematicPreset(
        name="historical_reconstruction",
        label="Historical Reconstruction",
        description="Photorealistic historical scene recreation",
        positive_suffix=(
            "photorealistic historical reconstruction, shot on Arri Alexa, Zeiss Master Prime, "
            "period-accurate architecture, authentic costumes and props, natural period lighting, "
            "documentary style, historical photograph quality, academic accuracy, detailed craftsmanship, organic film grain"
        ),
        negative_additions="modern, futuristic, anachronistic, digital artifacts, CGI",
        cfg=7.0,
        steps=30,
        sampler="euler",
        scheduler="karras",
        style_tag="Historical",
        trigger_keywords=["historical", "ancient", "medieval", "renaissance", "century", "era", "period"],
    ),
    "drone_shot": CinematicPreset(
        name="drone_shot",
        label="Drone Shot",
        description="Cinematic aerial drone photography",
        positive_suffix=(
            "aerial drone photography, shot on Hasselblad L2D-20c camera, bird's eye view, "
            "sweeping landscape, golden hour, cinematic aerial composition, vast scale, "
            "topographic patterns, perfect exposure, 4K aerial footage, cinematic color grade"
        ),
        negative_additions="indoor, close-up, portrait, underground, cave",
        cfg=6.5,
        steps=25,
        sampler="euler",
        scheduler="normal",
        style_tag="Aerial",
        trigger_keywords=["aerial", "drone", "above", "overhead", "birds eye", "landscape", "top down"],
    ),
    "apocalypse": CinematicPreset(
        name="apocalypse",
        label="Apocalypse",
        description="Post-apocalyptic devastation and ruin",
        positive_suffix=(
            "post-apocalyptic cinematic photography, shot on Arri Alexa, Cooke lenses, "
            "ruins and devastation, dramatic overcast sky, ash and smoke, overgrown abandoned structures, "
            "desolate wasteland, epic destruction, survival atmosphere, epic cinematic composition, "
            "color grading — orange teal, organic film grain"
        ),
        negative_additions="clean, modern intact, cheerful, populated, bright",
        cfg=8.0,
        steps=32,
        sampler="dpm_2",
        scheduler="karras",
        style_tag="Apocalypse",
        trigger_keywords=["apocalypse", "ruins", "destroyed", "wasteland", "aftermath", "collapse", "end"],
    ),
}


# ─────────────────────────────────────────────────────────────
# Base Style Suffixes
# ─────────────────────────────────────────────────────────────

BASE_STYLE_SUFFIXES: dict[str, str] = {
    "Cinematic": (
        "cinematic photography, shot on Arri Alexa LF, Zeiss Master Prime, anamorphic flare, "
        "dramatic lighting, shallow depth of field, organic film grain, 35mm, professional color grading, movie still"
    ),
    "Documentary": (
        "documentary photograph, shot on RED V-Raptor, Cooke lenses, candid, photojournalism, "
        "natural lighting, raw organic film grain, gritty, authentic, real"
    ),
    "Dark Noir": (
        "film noir style, shot on Panavision Panaflex, dark shadows, high contrast, dramatic lighting, moody, "
        "detective aesthetic, heavy shadows, chiaroscuro, organic film grain"
    ),
    "Anime": (
        "anime art style, studio ghibli inspired, vibrant colors, detailed illustration, "
        "cel shading, beautiful scenery, high quality animation"
    ),
    "Hyper Realistic": (
        "hyperrealistic photograph, shot on Hasselblad H6D-100c, 8k resolution, ultra-detailed, "
        "photorealistic, professional camera, perfect lighting, crisp details, award-winning photography"
    ),
    "Vintage War": (
        "vintage war photograph, shot on Bell & Howell 16mm, sepia tone, aged film, historical, "
        "military documentary, damaged film, period authentic, archival, heavy organic film grain"
    ),
    "Sci-Fi": (
        "science fiction concept art, shot on Hasselblad, futuristic, advanced technology, neon lights, "
        "space age, cyberpunk, digital painting, sci-fi aesthetic, hyperdetailed, volumetric lighting"
    ),
}

# Universal quality boosters appended to every prompt
QUALITY_SUFFIX = (
    "masterpiece, best quality, highly detailed, sharp focus"
)

# Universal negative prompt base
BASE_NEGATIVE = (
    "blurry, low quality, distorted, ugly, deformed, bad anatomy, "
    "watermark, text overlay, logo, signature, nsfw, oversaturated, "
    "jpeg artifacts, noise, overexposed, underexposed"
)


# ─────────────────────────────────────────────────────────────
# Enhancer
# ─────────────────────────────────────────────────────────────

@dataclass
class EnhancedPrompt:
    positive: str
    negative: str
    detected_preset: Optional[str] = None
    applied_style: Optional[str] = None


def auto_detect_preset(prompt: str) -> Optional[str]:
    """
    Scan prompt for trigger keywords and return the best matching preset name.
    Returns None if no strong match found.
    """
    lower = prompt.lower()
    best_preset: Optional[str] = None
    best_score = 0

    for preset_name, preset in PRESETS.items():
        score = sum(1 for kw in preset.trigger_keywords if kw in lower)
        if score > best_score:
            best_score = score
            best_preset = preset_name

    return best_preset if best_score >= 1 else None


def enhance_prompt(
    prompt: str,
    style: str = "Cinematic",
    negative_prompt: str = "",
    preset_name: Optional[str] = None,
    auto_detect: bool = True,
    quality_boost: bool = True,
) -> EnhancedPrompt:
    """
    Build an enhanced positive and negative prompt for cinematic generation.

    Args:
        prompt:         Raw user prompt
        style:          Style preset name (from UI style buttons)
        negative_prompt: User-provided negative prompt additions
        preset_name:    Explicit preset key (overrides auto-detect)
        auto_detect:    Whether to auto-detect preset from keywords
        quality_boost:  Append universal quality suffix

    Returns:
        EnhancedPrompt with enhanced positive + negative strings
    """
    prompt = prompt.strip()
    detected_preset: Optional[str] = None

    # 1. Resolve preset
    active_preset: Optional[CinematicPreset] = None
    if preset_name and preset_name in PRESETS:
        active_preset = PRESETS[preset_name]
        detected_preset = preset_name
    elif auto_detect:
        detected_key = auto_detect_preset(prompt)
        if detected_key:
            active_preset = PRESETS[detected_key]
            detected_preset = detected_key

    # 2. Build positive
    parts = [prompt]

    if active_preset:
        parts.append(active_preset.positive_suffix)
    elif style in BASE_STYLE_SUFFIXES:
        parts.append(BASE_STYLE_SUFFIXES[style])

    if quality_boost:
        parts.append(QUALITY_SUFFIX)

    positive = ", ".join(p.strip().rstrip(",") for p in parts if p.strip())

    # 3. Build negative
    neg_parts = [BASE_NEGATIVE]
    if active_preset and active_preset.negative_additions:
        neg_parts.append(active_preset.negative_additions)
    if negative_prompt.strip():
        neg_parts.append(negative_prompt.strip())

    negative = ", ".join(n.strip().rstrip(",") for n in neg_parts if n.strip())

    return EnhancedPrompt(
        positive=positive,
        negative=negative,
        detected_preset=detected_preset,
        applied_style=active_preset.label if active_preset else style,
    )


def get_preset_params(preset_name: str) -> dict:
    """
    Return generation parameter overrides for a given preset.
    Frontend can apply these when user selects a preset.
    """
    if preset_name not in PRESETS:
        return {}
    p = PRESETS[preset_name]
    return {
        "cfg_scale": p.cfg,
        "steps": p.steps,
        "sampler": p.sampler,
        "scheduler": p.scheduler,
        "style": p.style_tag,
    }


def list_presets() -> list[dict]:
    """Return all presets as frontend-friendly list."""
    return [
        {
            "name": p.name,
            "label": p.label,
            "description": p.description,
            "style_tag": p.style_tag,
            "cfg": p.cfg,
            "steps": p.steps,
            "sampler": p.sampler,
            "scheduler": p.scheduler,
        }
        for p in PRESETS.values()
    ]
