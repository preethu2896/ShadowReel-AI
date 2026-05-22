"""
ShadowReel AI — Dynamic ComfyUI Workflow Builder
Generates proper ComfyUI API-format workflow JSON for all supported pipelines.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Literal


ModelType = Literal["flux", "sdxl"]
PipelineType = Literal["text2img", "img2img", "upscale"]


@dataclass
class WorkflowParams:
    positive: str
    negative: str
    width: int = 1024
    height: int = 1024
    steps: int = 20
    cfg: float = 7.0
    seed: int = -1
    sampler: str = "euler"
    scheduler: str = "normal"
    denoise: float = 1.0
    # Advanced / Cinematic params
    guidance: float = 3.5
    lora_name: str | None = None
    lora_strength: float = 1.0
    # img2img
    init_image_b64: str | None = None
    # model filenames (overridable)
    flux_unet: str = "flux1-dev.safetensors"
    flux_clip1: str = "t5xxl_fp16.safetensors"
    flux_clip2: str = "clip_l.safetensors"
    flux_vae: str = "ae.safetensors"
    sdxl_checkpoint: str = "sd_xl_base_1.0.safetensors"
    upscale_model: str = "RealESRGAN_x4plus.pth"

    def __post_init__(self):
        if self.seed == -1:
            self.seed = random.randint(0, 2 ** 32 - 1)


# ─────────────────────────────────────────────────────────────
# FLUX Text-to-Image
# ─────────────────────────────────────────────────────────────

def build_flux_t2i(p: WorkflowParams) -> dict:
    """
    FLUX.1-dev text-to-image workflow.
    Uses SamplerCustomAdvanced + BasicScheduler + BasicGuider + RandomNoise + FluxGuidance + optional LoraLoader.
    """
    workflow = {
        # Dual CLIP encoder for FLUX (T5 + CLIP-L)
        "1": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": p.flux_clip1,
                "clip_name2": p.flux_clip2,
                "type": "flux",
            },
        },
        # VAE
        "2": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": p.flux_vae},
        },
        # UNET loader
        "3": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": p.flux_unet,
                "weight_dtype": "default",
            },
        },
        # Empty latent
        "6": {
            "class_type": "EmptySD3LatentImage",
            "inputs": {"width": p.width, "height": p.height, "batch_size": 1},
        },
        # Noise
        "7": {
            "class_type": "RandomNoise",
            "inputs": {"noise_seed": p.seed},
        },
        # Sampler selector
        "9": {
            "class_type": "KSamplerSelect",
            "inputs": {"sampler_name": p.sampler},
        },
        # VAE decode
        "12": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["11", 0], "vae": ["2", 0]},
        },
        # Save
        "13": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "shadowreel", "images": ["12", 0]},
        },
    }

    # Connect model and clip loaders.
    # If a LoRA is requested, chain it between loaders and conditioning/guidance.
    model_source = ["3", 0]
    clip_source = ["1", 0]

    if p.lora_name:
        workflow["15"] = {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": p.lora_name,
                "strength_model": p.lora_strength,
                "strength_clip": p.lora_strength,
                "model": ["3", 0],
                "clip": ["1", 0],
            }
        }
        model_source = ["15", 0]
        clip_source = ["15", 1]

    # Positive conditioning
    workflow["4"] = {
        "class_type": "CLIPTextEncode",
        "inputs": {"text": p.positive, "clip": clip_source},
    }
    # Negative conditioning (empty for FLUX, but kept for compat)
    workflow["5"] = {
        "class_type": "CLIPTextEncode",
        "inputs": {"text": p.negative, "clip": clip_source},
    }

    # FluxGuidance node for cinematic prompt guidance control
    workflow["14"] = {
        "class_type": "FluxGuidance",
        "inputs": {
            "guidance": p.guidance,
            "model": model_source,
        }
    }

    # Guider (FLUX uses BasicGuider, ignores negative)
    workflow["8"] = {
        "class_type": "BasicGuider",
        "inputs": {"model": ["14", 0], "conditioning": ["4", 0]},
    }
    
    # Scheduler
    workflow["10"] = {
        "class_type": "BasicScheduler",
        "inputs": {
            "model": ["14", 0],
            "scheduler": p.scheduler,
            "steps": p.steps,
            "denoise": p.denoise,
        },
    }
    # Advanced sampler
    workflow["11"] = {
        "class_type": "SamplerCustomAdvanced",
        "inputs": {
            "noise": ["7", 0],
            "guider": ["8", 0],
            "sampler": ["9", 0],
            "sigmas": ["10", 0],
            "latent_image": ["6", 0],
        },
    }

    return workflow


# ─────────────────────────────────────────────────────────────
# SDXL Text-to-Image
# ─────────────────────────────────────────────────────────────

def build_sdxl_t2i(p: WorkflowParams) -> dict:
    """Standard SDXL KSampler workflow with optional LoRA loading."""
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": p.sdxl_checkpoint},
        },
        "2": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": p.width, "height": p.height, "batch_size": 1},
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "shadowreel", "images": ["6", 0]},
        },
    }

    model_source = ["1", 0]
    clip_source = ["1", 1]

    if p.lora_name:
        workflow["15"] = {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": p.lora_name,
                "strength_model": p.lora_strength,
                "strength_clip": p.lora_strength,
                "model": ["1", 0],
                "clip": ["1", 1],
            }
        }
        model_source = ["15", 0]
        clip_source = ["15", 1]

    workflow["3"] = {
        "class_type": "CLIPTextEncode",
        "inputs": {"text": p.positive, "clip": clip_source},
    }
    workflow["4"] = {
        "class_type": "CLIPTextEncode",
        "inputs": {"text": p.negative, "clip": clip_source},
    }
    workflow["5"] = {
        "class_type": "KSampler",
        "inputs": {
            "seed": p.seed,
            "steps": p.steps,
            "cfg": p.cfg,
            "sampler_name": p.sampler,
            "scheduler": p.scheduler,
            "denoise": p.denoise,
            "model": model_source,
            "positive": ["3", 0],
            "negative": ["4", 0],
            "latent_image": ["2", 0],
        },
    }

    return workflow


# ─────────────────────────────────────────────────────────────
# ESRGAN Upscale Workflow
# ─────────────────────────────────────────────────────────────

def build_upscale_workflow(image_filename: str, model_name: str = "RealESRGAN_x4plus.pth") -> dict:
    """
    Upscale an existing ComfyUI output image using ESRGAN.
    `image_filename` must be a filename already in ComfyUI's output folder.
    """
    return {
        "1": {
            "class_type": "LoadImage",
            "inputs": {"image": image_filename, "upload": "image"},
        },
        "2": {
            "class_type": "UpscaleModelLoader",
            "inputs": {"model_name": model_name},
        },
        "3": {
            "class_type": "ImageUpscaleWithModel",
            "inputs": {"upscale_model": ["2", 0], "image": ["1", 0]},
        },
        "4": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "shadowreel_upscale", "images": ["3", 0]},
        },
    }


# ─────────────────────────────────────────────────────────────
# SDXL Image-to-Image
# ─────────────────────────────────────────────────────────────

def build_sdxl_img2img(p: WorkflowParams) -> dict:
    """SDXL img2img — loads a base image then denoises with KSampler."""
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": p.sdxl_checkpoint},
        },
        "2": {
            "class_type": "LoadImage",
            "inputs": {"image": "init_image.png", "upload": "image"},
        },
        "3": {
            "class_type": "VAEEncode",
            "inputs": {"pixels": ["2", 0], "vae": ["1", 2]},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": p.positive, "clip": ["1", 1]},
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": p.negative, "clip": ["1", 1]},
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "seed": p.seed,
                "steps": p.steps,
                "cfg": p.cfg,
                "sampler_name": p.sampler,
                "scheduler": p.scheduler,
                "denoise": max(0.1, min(p.denoise, 1.0)),
                "model": ["1", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["3", 0],
            },
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["6", 0], "vae": ["1", 2]},
        },
        "8": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "shadowreel_i2i", "images": ["7", 0]},
        },
    }


# ─────────────────────────────────────────────────────────────
# Main Builder — entry point
# ─────────────────────────────────────────────────────────────

def build_workflow(
    model: ModelType,
    params: WorkflowParams,
    pipeline: PipelineType = "text2img",
) -> dict:
    """
    Returns a ready-to-submit ComfyUI API workflow dict.

    Args:
        model:    "flux" or "sdxl"
        params:   WorkflowParams dataclass instance
        pipeline: "text2img" | "img2img" | "upscale"
    """
    if pipeline == "upscale":
        return build_upscale_workflow(params.positive, params.upscale_model)

    if pipeline == "img2img":
        # FLUX img2img not standard — fall back to SDXL
        return build_sdxl_img2img(params)

    # text2img
    if model == "flux":
        return build_flux_t2i(params)
    return build_sdxl_t2i(params)


# ─────────────────────────────────────────────────────────────
# Aspect Ratio → Dimensions
# ─────────────────────────────────────────────────────────────

ASPECT_RATIO_MAP: dict[str, tuple[int, int]] = {
    "1:1":  (1024, 1024),
    "16:9": (1344, 768),
    "9:16": (768, 1344),
    "4:3":  (1152, 896),
    "3:4":  (896, 1152),
    "21:9": (1536, 640),
    "2:3":  (832, 1216),
    "3:2":  (1216, 832),
}


def ratio_to_dims(ratio: str, model: ModelType = "flux") -> tuple[int, int]:
    """Return (width, height) for the given aspect ratio, snapped to 64px multiples."""
    w, h = ASPECT_RATIO_MAP.get(ratio, (1024, 1024))
    # SDXL works best at 1024 base; FLUX at 1024 too
    return w, h
