import os
import asyncio
from pathlib import Path
from config import settings
import logging

logger = logging.getLogger(__name__)

def format_srt_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"

def write_srt_file(text: str, duration: float, srt_path: Path):
    start = format_srt_time(0.0)
    end = format_srt_time(duration)
    srt_content = f"1\n{start} --> {end}\n{text}\n"
    srt_path.write_text(srt_content, encoding="utf-8")

async def get_media_duration(file_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        return float(stdout.decode().strip())
    except Exception as e:
        logger.warning(f"Failed to probe duration for {file_path}: {e}")
        return 5.0

async def assemble_documentary(scenes: list, output_filename: str, is_short: bool = False) -> str:
    """
    Composites video and audio using FFmpeg with transitions and burned subtitles.
    Expects scenes to be a list of dicts with 'video_url', 'audio_url', and 'script_text'.
    If is_short is True, crops the output to 9:16 vertical format.
    """
    output_dir = Path(settings.OUTPUT_DIR) / "documentaries"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    
    concat_file_path = output_dir / f"{output_filename}.txt"
    processed_clips = []
    srt_paths = []
    durations = []
    
    try:
        for i, scene in enumerate(scenes):
            vid_path = Path(settings.OUTPUT_DIR) / Path(scene["video_url"]).name
            aud_path = Path(settings.OUTPUT_DIR) / "audio" / Path(scene["audio_url"]).name
            out_clip = output_dir / f"temp_clip_{i}_{output_filename}"
            
            # Use the new Export Mastering Engine
            from services.mastering_engine.master import ExportMasteringEngine
            mastering = ExportMasteringEngine()
            
            video_filters = mastering.get_ffmpeg_mastering_filters(is_short=is_short, style_mode="Dark Documentary")
            audio_filters = mastering.get_audio_mastering_filters()
            encoding_params = mastering.get_encoding_parameters(is_short)
            
            # Determine audio duration and create subtitles file
            aud_duration = await get_media_duration(str(aud_path))
            durations.append(aud_duration)
            
            srt_filename = f"temp_sub_{i}_{output_filename.replace('.mp4', '')}.srt"
            srt_path = Path(srt_filename)
            write_srt_file(scene["script_text"], aud_duration, srt_path)
            srt_paths.append(srt_path)
            
            # Combine subtitles filter with mastering filters
            vf_content = ""
            if video_filters and len(video_filters) > 1:
                vf_content = video_filters[1]
                
            # Windows-friendly relative subtitles path for FFmpeg subtitles filter
            sub_filter_path = srt_filename.replace('\\', '/')
            sub_filter_str = f"subtitles={sub_filter_path}:force_style='Fontname=Arial,Fontsize=18,PrimaryColour=&H00FFFF,Bold=1,Outline=2,Shadow=1'"
            if vf_content:
                vf_content = f"{vf_content},{sub_filter_str}"
            else:
                vf_content = sub_filter_str
            
            video_filters_arg = ["-vf", vf_content]
            
            cmd = [
                "ffmpeg", "-y",
                "-stream_loop", "-1", "-i", str(vid_path),  # Loop video
                "-i", str(aud_path),
                "-c:a", "aac",
                "-shortest",  # End when audio ends
            ]
            cmd.extend(encoding_params)
            cmd.extend(video_filters_arg)
            cmd.extend(audio_filters)
            cmd.extend([
                str(out_clip)
            ])
            
            logger.info(f"Processing clip {i} with subtitles and mastering.")
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            if proc.returncode == 0:
                processed_clips.append(out_clip)
            else:
                logger.error(f"Failed to process clip {i}")

        if not processed_clips:
            raise Exception("No valid clips were generated for assembly.")

        # Check transition feasibility (need at least 2 clips, and all clips > 2.0s)
        min_clip_duration = min(durations) if durations else 0.0
        transition_duration = 1.0
        if min_clip_duration <= transition_duration * 2.0:
            transition_duration = max(0.1, min_clip_duration / 2.5)

        if len(processed_clips) > 1 and min_clip_duration > 0.5:
            logger.info("Orchestrating smooth scene transitions using xfade and acrossfade.")
            concat_cmd = ["ffmpeg", "-y"]
            for clip in processed_clips:
                concat_cmd.extend(["-i", str(clip)])
                
            filter_complex = []
            
            # Video transition chain
            last_v = "[0:v]"
            running_duration = durations[0]
            for i in range(1, len(processed_clips)):
                scene_transition = scenes[i-1].get('transition', 'crossfade')
                trans_dur = transition_duration if scene_transition != 'hard_cut' else 0.01
                # Ensure transition duration doesn't exceed clip boundaries
                trans_dur = min(trans_dur, durations[i-1] / 2.1, durations[i] / 2.1)
                
                trans_type = scene_transition if scene_transition in ['crossfade', 'fade', 'wipeleft', 'wiperight', 'slideup', 'slidedown'] else 'crossfade'
                if scene_transition == 'hard_cut':
                    trans_type = 'fade'  # use fade with tiny duration (0.01) as hard cut equivalent under xfade
                    
                offset = running_duration - trans_dur
                next_v = f"[v{i}]"
                filter_complex.append(f"{last_v}[{i}:v]xfade=transition={trans_type}:duration={trans_dur:.3f}:offset={offset:.3f}{next_v}")
                last_v = next_v
                running_duration = running_duration + durations[i] - trans_dur
                
            # Audio transition chain
            last_a = "[0:a]"
            running_duration_a = durations[0]
            for i in range(1, len(processed_clips)):
                scene_transition = scenes[i-1].get('transition', 'crossfade')
                trans_dur = transition_duration if scene_transition != 'hard_cut' else 0.01
                trans_dur = min(trans_dur, durations[i-1] / 2.1, durations[i] / 2.1)
                
                next_a = f"[a{i}]"
                filter_complex.append(f"{last_a}[{i}:a]acrossfade=d={trans_dur:.3f}:c1=tri:c2=tri{next_a}")
                last_a = next_a
                running_duration_a = running_duration_a + durations[i] - trans_dur
                
            concat_cmd.extend([
                "-filter_complex", ";".join(filter_complex),
                "-map", last_v,
                "-map", last_a,
            ])
            
            # Apply final mastering encoding
            from services.mastering_engine.master import ExportMasteringEngine
            mastering = ExportMasteringEngine()
            encoding_params = mastering.get_encoding_parameters(is_short)
            concat_cmd.extend(encoding_params)
            concat_cmd.append(str(output_path))
        else:
            # Fall back to standard flat copy concat
            logger.info("Falling back to flat copy concat.")
            with open(concat_file_path, "w") as f:
                for clip in processed_clips:
                    f.write(f"file '{clip.resolve()}'\n")
                    
            concat_cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file_path),
                "-c", "copy",
                str(output_path)
            ]
            
        proc = await asyncio.create_subprocess_exec(
            *concat_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        
        if proc.returncode != 0:
            raise Exception("FFmpeg concat / blend failed.")
            
    finally:
        # Cleanup temporary files
        if concat_file_path.exists():
            try:
                concat_file_path.unlink()
            except Exception:
                pass
        for srt_path in srt_paths:
            if srt_path.exists():
                try:
                    srt_path.unlink()
                except Exception:
                    pass
        for clip in processed_clips:
            if clip.exists():
                try:
                    clip.unlink()
                except Exception:
                    pass
            
    return f"{settings.STATIC_URL_PREFIX}/documentaries/{output_filename}"
