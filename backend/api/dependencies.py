import logging
import time
import jwt
from fastapi import Request, HTTPException, Security, Depends, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings

logger = logging.getLogger(__name__)

# Basic Security Hardening Setup
security = HTTPBearer()

# JWT Validator using PyJWT
def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Validates JWT tokens for API security using PyJWT.
    Supports expiration (exp), issue time (iat), and subject (sub) verification.
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Authentication token required")
    
    # Development fallback
    if settings.DEBUG and token == "mock-token-for-dev-verification":
        return {"user_id": "mock_authenticated_user", "email": "dev@shadowreel.ai"}
        
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token is missing subject (sub) claim")
        return {"user_id": user_id, "email": payload.get("email")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token signature has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# In-memory rate limiting fallback
RATE_LIMIT_STORE = {}

async def rate_limiter(request: Request):
    """
    Prevents queue abuse by rate limiting generation requests.
    Uses Redis sorted sets for sliding window rate limiting, with an in-memory fallback.
    """
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    limit = settings.RATE_LIMIT_PER_MINUTE
    key = f"rate_limit:{client_ip}"
    
    try:
        from services.redis_client import get_redis
        r = await get_redis()
        # Clean up timestamps older than 60 seconds
        await r.zremrangebyscore(key, 0, now - 60)
        # Count remaining requests in current window
        count = await r.zcard(key)
        
        if count >= limit:
            logger.warning(f"Rate limit exceeded (Redis) for IP: {client_ip}")
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
            
        # Record the current request timestamp
        await r.zadd(key, {str(now): now})
        await r.expire(key, 60)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Redis rate limiter failed, falling back to in-memory: {e}")
        # In-memory fallback
        if client_ip not in RATE_LIMIT_STORE:
            RATE_LIMIT_STORE[client_ip] = []
        RATE_LIMIT_STORE[client_ip] = [t for t in RATE_LIMIT_STORE[client_ip] if now - t < 60]
        
        if len(RATE_LIMIT_STORE[client_ip]) >= limit:
            logger.warning(f"Rate limit exceeded (In-Memory) for IP: {client_ip}")
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
            
        RATE_LIMIT_STORE[client_ip].append(now)
        
    return True

async def validate_media_upload(file: UploadFile):
    """
    Validates uploaded media file sizes and MIME types.
    """
    # 1. MIME Type check
    allowed_types = {
        "image/jpeg", "image/png", "image/webp", 
        "video/mp4", "video/quicktime",
        "audio/mpeg", "audio/wav", "audio/x-wav", "audio/ogg"
    }
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(allowed_types)}"
        )
        
    # 2. File Size check
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    try:
        # Attempt standard file seek
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
    except Exception:
        # Fallback reading chunk size
        size = 0
        while True:
            chunk = await file.read(8192)
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE_MB}MB"
                )
        await file.seek(0)
        
    if size > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE_MB}MB"
        )
        
    return file

