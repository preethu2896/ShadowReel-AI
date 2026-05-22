import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

@dataclass
class VideoWorkflowParams:
    prompt: str
    negative_prompt: str = ""
    width: int = 848
    height: int = 480
    length: int = 49  # 49 frames for ~2s at 24fps
    seed: int = -1
    motion_preset: str = "Pan Right"
    image_path: Optional[str] = None  # if img2vid

MOTION_PRESETS = {
    "Pan Right": "camera panning slowly to the right, smooth motion, high temporal consistency",
    "Pan Left": "camera panning slowly to the left, smooth motion, high temporal consistency",
    "Tilt Up": "camera tilting up, slow dramatic tilt reveal, cinematic panning",
    "Tilt Down": "camera tilting down, slow dramatic tilt reveal, cinematic panning",
    "Slow Zoom In": "slow camera zoom in, push in shot, focusing on details, telephoto compression, cinematic push",
    "Slow Zoom Out": "slow camera pull back, zoom out, revealing wide environment, cinematic pull",
    "Handheld Shake": "gritty handheld camera movement, realistic subtle camera shake, documentary style, candid motion",
    "Drone Orbit": "cinematic aerial drone orbit, slow rotation, sweeping landscape view, high altitude perspective",
    "Static Locked-off": "locked-off static tripod shot, zero camera movement, stable composition, archival observation style",
}

def _build_wan21_t2v_workflow(params: VideoWorkflowParams) -> Dict[str, Any]:
    """
    Builds a basic ComfyUI workflow for Wan2.1 Text-to-Video.
    """
    # Snap frame length to multiple of 4 plus 1 for Wan2.1 3D VAE compat
    snapped_length = max(5, ((params.length - 1) // 4) * 4 + 1)

    # Enhance prompt with motion presets
    motion_text = MOTION_PRESETS.get(params.motion_preset, "")
    final_prompt = params.prompt
    if motion_text:
        final_prompt = f"{final_prompt}, {motion_text}"

    return {
        "1": {
            "inputs": {"unet_name": "wan2.1_t2v_1.3B.safetensors", "weight_dtype": "default"},
            "class_type": "UNETLoader"
        },
        "2": {
            "inputs": {"vae_name": "wan_2.1_vae.safetensors"},
            "class_type": "VAELoader"
        },
        "3": {
            "inputs": {"clip_name": "t5xxl_fp16.safetensors", "type": "wan"},
            "class_type": "DualCLIPLoader"
        },
        "4": {
            "inputs": {"text": final_prompt, "clip": ["3", 1]},
            "class_type": "CLIPTextEncode"
        },
        "5": {
            "inputs": {"text": params.negative_prompt, "clip": ["3", 1]},
            "class_type": "CLIPTextEncode"
        },
        "6": {
            "inputs": {"width": params.width, "height": params.height, "length": snapped_length, "batch_size": 1},
            "class_type": "EmptyWanLatentVideo"
        },
        "7": {
            "inputs": {"seed": params.seed, "steps": 30, "cfg": 6.0, "sampler_name": "uni_pc", "scheduler": "normal", "denoise": 1.0, "model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0]},
            "class_type": "KSampler"
        },
        "8": {
            "inputs": {"samples": ["7", 0], "vae": ["2", 0]},
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {"filename_prefix": "shadowreel_video", "fps": 24, "format": "video/h264-mp4", "pix_fmt": "yuv420p", "crf": 19, "save_metadata": True, "pingpong": False, "save_output": True, "images": ["8", 0]},
            "class_type": "VideoCombine"
        }
    }

def _build_svd_i2v_workflow(params: VideoWorkflowParams) -> Dict[str, Any]:
    """
    Builds a basic ComfyUI workflow for Stable Video Diffusion Image-to-Video.
    """
    # Map motion presets to SVD motion_bucket_id
    motion_buckets = {
        "Static Locked-off": 15,
        "Slow Zoom In": 60,
        "Slow Zoom Out": 60,
        "Pan Right": 90,
        "Pan Left": 90,
        "Handheld Shake": 120,
        "Drone Orbit": 140,
    }
    bucket_id = motion_buckets.get(params.motion_preset, 127)

    return {
        "1": {
            "inputs": {"ckpt_name": "svd_xt.safetensors"},
            "class_type": "ImageOnlyCheckpointLoader"
        },
        "2": {
            "inputs": {"image": params.image_path, "upload": "image"},
            "class_type": "LoadImage"
        },
        "3": {
            "inputs": {"width": params.width, "height": params.height, "video_frames": params.length, "motion_bucket_id": bucket_id, "fps": 24, "augmentation_level": 0.0, "clip_vision": ["1", 1], "init_image": ["2", 0], "vae": ["1", 2]},
            "class_type": "SVD_img2vid_Conditioning"
        },
        "4": {
            "inputs": {"seed": params.seed, "steps": 20, "cfg": 2.5, "sampler_name": "euler", "scheduler": "karras", "denoise": 1.0, "model": ["1", 0], "positive": ["3", 0], "negative": ["3", 1], "latent_image": ["3", 2]},
            "class_type": "KSampler"
        },
        "5": {
            "inputs": {"samples": ["4", 0], "vae": ["1", 2]},
            "class_type": "VAEDecode"
        },
        "6": {
            "inputs": {"filename_prefix": "shadowreel_video", "fps": 24, "format": "video/h264-mp4", "pix_fmt": "yuv420p", "crf": 19, "save_metadata": True, "pingpong": False, "save_output": True, "images": ["5", 0]},
            "class_type": "VideoCombine"
        }
    }

def build_video_workflow(model: str, params: VideoWorkflowParams, pipeline: str = "text2video") -> Dict[str, Any]:
    """
    Dispatcher for video generation workflows.
    """
    # Simple fallback structure
    if pipeline == "image2video" or params.image_path:
        return _build_svd_i2v_workflow(params)
    
    # Default text2video
    return _build_wan21_t2v_workflow(params)
