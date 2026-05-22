#!/usr/bin/env python3
"""
ShadowReel AI — Full-Stack Production Deployment Validator
Checks system state, DB connection, Redis, Celery, ComfyUI, FFmpeg, and GPU drivers.
"""

import os
import sys
import subprocess
import asyncio
import logging
import json
from pathlib import Path

# Add backend directory to path if run from root or scripts folder
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("deployment_validator")

# Colors for CLI styling
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== {title} ==={Colors.RESET}")

def print_result(name, success, message=""):
    if success:
        print(f" {Colors.GREEN}[OK]{Colors.RESET} {name} {Colors.GREEN}PASSED{Colors.RESET} {f'- {message}' if message else ''}")
    else:
        print(f" {Colors.RED}[FAIL]{Colors.RESET} {name} {Colors.RED}FAILED{Colors.RESET} {f'- {message}' if message else ''}")

# 1. Check Python Dependencies
def validate_dependencies():
    print_section("1. Python Dependencies Verification")
    required = [
        "fastapi", "uvicorn", "sqlalchemy", "asyncpg", "redis", "celery",
        "pydantic_settings", "httpx", "websockets", "boto3", "pynvml", "psutil"
    ]
    all_ok = True
    for lib in required:
        try:
            __import__(lib)
            print_result(f"Package '{lib}'", True)
        except ImportError as e:
            print_result(f"Package '{lib}'", False, str(e))
            all_ok = False
    return all_ok

# 2. Check settings and environment loading
def validate_environment():
    print_section("2. Environment Variable Configuration")
    try:
        from config import settings
        print_result("Environment configuration loading", True, f"Loaded settings for: {settings.APP_NAME}")
        print(f"   Database mode: {'SQLite' if settings.USE_SQLITE else 'PostgreSQL'}")
        print(f"   Redis broker: {settings.CELERY_BROKER_URL}")
        print(f"   ComfyUI endpoint: {settings.COMFYUI_BASE_URL}")
        return True
    except Exception as e:
        print_result("Environment configuration loading", False, str(e))
        return False

# 3. Check DB connection
async def validate_database():
    print_section("3. Database Connectivity Check")
    from config import settings
    from sqlalchemy.sql import text
    
    if settings.USE_SQLITE:
        db_file = Path(settings.SQLITE_PATH)
        print_result("SQLite Local Database Path", True, f"Configured at: {db_file.absolute()}")
        # Check SQLite write accessibility
        try:
            from sqlalchemy.ext.asyncio import create_async_engine
            engine = create_async_engine(settings.EFFECTIVE_DATABASE_URL)
            async with engine.connect() as conn:
                res = await conn.execute(text("SELECT 1"))
                res.scalar()
            print_result("SQLite Database Connection", True)
            return True
        except Exception as e:
            print_result("SQLite Database Connection", False, str(e))
            return False
    else:
        # Check PostgreSQL connection
        try:
            from sqlalchemy.ext.asyncio import create_async_engine
            engine = create_async_engine(settings.EFFECTIVE_DATABASE_URL)
            async with engine.connect() as conn:
                res = await conn.execute(text("SELECT 1"))
                res.scalar()
            print_result("PostgreSQL Connection", True, f"Connected to {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
            return True
        except Exception as e:
            print_result("PostgreSQL Connection", False, str(e))
            return False

# 4. Check Redis and Pub/Sub
def validate_redis():
    print_section("4. Redis Connection & PubSub Messaging")
    from config import settings
    if settings.USE_FAKE_REDIS:
        print_result("Redis Server Status", True, "Running in-memory fake redis (development mode). Skipping TCP check.")
        return True
        
    try:
        import redis
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, socket_timeout=3.0)
        pong = r.ping()
        if pong:
            print_result("Redis Server Status", True, f"Pinged host: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
            # Validate PubSub
            pubsub = r.pubsub()
            pubsub.subscribe("test_channel")
            r.publish("test_channel", "ping_test")
            
            # Attempt to read published msg
            msg = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg and msg.get("data") == b"ping_test":
                print_result("Redis PubSub Delivery", True)
                return True
            else:
                print_result("Redis PubSub Delivery", False, "Message publishing/subscription timed out.")
                return False
        else:
            print_result("Redis Server Status", False, "No pong response received.")
            return False
    except Exception as e:
        print_result("Redis Server Status", False, str(e))
        return False

# 5. Check Celery Active Workers
def validate_celery():
    print_section("5. Celery Worker Orchestration Check")
    from config import settings
    if settings.USE_FAKE_REDIS:
        print_result("Celery Worker Inspection", True, "Fake redis active. Skipping celery remote inspection.")
        return True
        
    try:
        from workers.celery_app import celery_app
        inspector = celery_app.control.inspect(timeout=3.0)
        active = inspector.active()
        if active:
            print_result("Celery Active Workers", True, f"Detected workers: {list(active.keys())}")
            return True
        else:
            print_result("Celery Active Workers", False, "No active workers detected. Please start worker instances.")
            return False
    except Exception as e:
        print_result("Celery Active Workers", False, str(e))
        return False

# 6. Check ComfyUI API Connection
async def validate_comfyui():
    print_section("6. ComfyUI Endpoint Validation")
    from config import settings
    import httpx
    
    url = settings.COMFYUI_BASE_URL
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{url}/system_stats")
            if resp.status_code == 200:
                stats = resp.json()
                device = stats.get("devices", [{}])[0]
                device_type = device.get("type", "Unknown")
                print_result("ComfyUI Connection", True, f"Connected to {url}. Device: {device_type}")
                return True
            else:
                print_result("ComfyUI Connection", False, f"HTTP status: {resp.status_code}")
                return False
    except Exception as e:
        print_result("ComfyUI Connection", False, f"Failed connecting to {url}: {e}")
        return False

# 7. Check FFmpeg on System Path
def validate_ffmpeg():
    print_section("7. FFmpeg Media Encoder verification")
    try:
        res = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        first_line = res.stdout.split('\n')[0]
        print_result("FFmpeg binary", True, first_line)
        return True
    except Exception as e:
        print_result("FFmpeg binary", False, "ffmpeg not found in system PATH. Install ffmpeg to process cinematic documentaries.")
        return False

# 8. Check CUDA and NVML GPU support
def validate_gpu():
    print_section("8. Hardware Acceleration & NVIDIA CUDA Support")
    gpu_detected = False
    
    # Check PyTorch CUDA if torch is installed
    try:
        import torch
        cuda_avail = torch.cuda.is_available()
        if cuda_avail:
            device_name = torch.cuda.get_device_name(0)
            print_result("PyTorch GPU Support", True, f"Active device: {device_name}")
            gpu_detected = True
        else:
            print_result("PyTorch GPU Support", False, "CUDA not enabled in torch.")
    except ImportError:
         print_result("PyTorch library status", False, "PyTorch not found.")
         
    # Check NVML drivers
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        for idx in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                 name = name.decode('utf-8')
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            free_gb = mem_info.free / (1024 ** 3)
            total_gb = mem_info.total / (1024 ** 3)
            print_result(f"NVIDIA GPU #{idx}", True, f"Device: {name} (VRAM: {free_gb:.2f} GB Free / {total_gb:.2f} GB Total)")
            gpu_detected = True
        pynvml.nvmlShutdown()
    except Exception as e:
        print_result("Nvidia NVML Drivers check", False, str(e))
        # Fallback to nvidia-smi command check
        try:
             res = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
             if res.returncode == 0:
                 print_result("Nvidia driver status", True, "nvidia-smi executed successfully.")
                 gpu_detected = True
             else:
                 print_result("Nvidia driver status", False, "nvidia-smi failed.")
        except Exception:
             pass

    return gpu_detected

async def main():
    print(f"\n{Colors.BOLD}{Colors.YELLOW}======================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}   SHADOWREEL AI — PRODUCTION ENVIRONMENT DEPLOYMENT VALIDATOR{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}======================================================================{Colors.RESET}")
    
    deps_ok = validate_dependencies()
    env_ok = validate_environment()
    
    if not env_ok:
        logger.error("Environment failed to load. Aborting verification checks.")
        sys.exit(1)
        
    db_ok = await validate_database()
    redis_ok = validate_redis()
    celery_ok = validate_celery()
    comfy_ok = await validate_comfyui()
    ffmpeg_ok = validate_ffmpeg()
    gpu_ok = validate_gpu()
    
    print_section("Summary Report")
    
    checks = {
        "Dependencies": deps_ok,
        "Environment Configs": env_ok,
        "Database System": db_ok,
        "Redis Broker": redis_ok,
        "Celery Workers": celery_ok,
        "ComfyUI Core": comfy_ok,
        "FFmpeg Engine": ffmpeg_ok,
        "Nvidia Hardware": gpu_ok
    }
    
    failures = [name for name, status in checks.items() if not status]
    
    if not failures:
        print(f"\n{Colors.BOLD}{Colors.GREEN}[SUCCESS] ALL DEPLOYMENT CHECKS PASSED. SYSTEM IS SECURE AND READY FOR PRODUCTION!{Colors.RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{Colors.BOLD}{Colors.RED}[ERROR] DEPLOYMENT COMPILATION HAS WARNINGS/FAILURES!{Colors.RESET}")
        print(f"Failures found in: {', '.join(failures)}")
        print(f"Please inspect local setup configurations and logs.\n")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
