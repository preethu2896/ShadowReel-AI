import logging

logger = logging.getLogger(__name__)

class ExportMasteringEngine:
    """
    Intelligently optimizes the final FFmpeg render settings based on the target platform.
    """
    def __init__(self):
        pass

    def get_ffmpeg_mastering_filters(self, is_short: bool, style_mode: str) -> list[str]:
        """
        Returns the appropriate FFmpeg video filter (-vf) chain for mastering.
        """
        logger.info(f"Mastering Export. Is Short: {is_short}, Style: {style_mode}")
        filters = []
        
        # 1. Shorts / Social Content Pipeline (9:16 Vertical)
        if is_short:
            # Crop to 9:16 and emulate fast-cut hook pacing by slightly speeding up
            filters.append("crop=ih*9/16:ih")
            filters.append("setpts=0.95*PTS")
            
        # 3. Cinematic Realism & Video Quality Optimization
        # Deflicker for stable AI video generation
        filters.append("deflicker=mode=pm:size=10")
        # Cinematic optical distortion (subtle barrel distortion)
        filters.append("lenscorrection=cx=0.5:cy=0.5:k1=-0.015:k2=0.01")
        # Temporal coherence enhancement (motion interpolation prep with scene change detection to avoid morphing artifacts)
        filters.append("minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:scd=fd")
        
        # 4. Dynamic Color Grading adjustment via EQ
        if "Dark" in style_mode or "Noir" in style_mode:
            filters.append("eq=contrast=1.2:brightness=-0.05:saturation=0.9")
        elif "War" in style_mode:
            filters.append("eq=contrast=1.1:saturation=0.7")
        else:
            filters.append("eq=contrast=1.05:saturation=1.1")
            
        # 5. Vignette / Lens simulation
        filters.append("vignette=PI/4")
        
        return ["-vf", ",".join(filters)] if filters else []
 
    def get_encoding_parameters(self, is_short: bool) -> list[str]:
        """
        Returns the x264 encoding parameters optimized for YouTube/TikTok compression.
        """
        # High quality profile, slower preset for better quality-to-rate control via CRF (18 landscape / 20 vertical)
        return [
            "-c:v", "libx264", 
            "-preset", "slow",
            "-profile:v", "high",
            "-crf", "20" if is_short else "18",
            "-g", "48", # Keyframe interval (2 seconds at 24fps)
            "-pix_fmt", "yuv420p"
        ]

    def get_audio_mastering_filters(self) -> list[str]:
        """
        Returns FFmpeg audio filter (-af) chain for dynamic audio mastering.
        Includes compression, loudnorm, and cinematic bass boost.
        """
        return ["-af", "acompressor=ratio=4,loudnorm=I=-16:TP=-1.5:LRA=11,bass=g=5:f=80"]
