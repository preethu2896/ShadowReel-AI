import asyncio
import json
import logging
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

_redis_pool = None
_fakeredis_server = None   # shared fakeredis server instance


def _get_fakeredis_server():
    global _fakeredis_server
    if _fakeredis_server is None:
        import fakeredis
        _fakeredis_server = fakeredis.FakeServer()
    return _fakeredis_server


async def get_redis():
    global _redis_pool
    if _redis_pool is None:
        if settings.USE_FAKE_REDIS:
            import fakeredis.aioredis as fake_aio
            _redis_pool = fake_aio.FakeRedis(
                server=_get_fakeredis_server(),
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("Using in-memory fakeredis (no Redis server required)")
        else:
            import redis.asyncio as aioredis
            _redis_pool = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
    return _redis_pool


# ─────────────────────────────────────────────────────────────
# Job State in Redis (fast, ephemeral — DB is source of truth)
# ─────────────────────────────────────────────────────────────

JOB_TTL = 3600 * 24  # 24 hours


async def set_job_state(job_id: str, state: dict):
    r = await get_redis()
    await r.set(f"job:{job_id}", json.dumps(state), ex=JOB_TTL)


async def get_job_state(job_id: str) -> Optional[dict]:
    r = await get_redis()
    raw = await r.get(f"job:{job_id}")
    if raw:
        return json.loads(raw)
    return None


async def update_job_progress(job_id: str, progress: int, status: str = "processing", extra: dict = None):
    state = await get_job_state(job_id) or {}
    state.update({"progress": progress, "status": status})
    if extra:
        state.update(extra)
    await set_job_state(job_id, state)


# ─────────────────────────────────────────────────────────────
# WebSocket Pub/Sub
# ─────────────────────────────────────────────────────────────

def _channel(job_id: str) -> str:
    return f"job_events:{job_id}"


async def publish_event(job_id: str, event: dict):
    r = await get_redis()
    await r.publish(_channel(job_id), json.dumps(event))


async def subscribe_job_events(job_id: str):
    """Async generator yielding events from the Redis pub/sub channel."""
    if settings.USE_FAKE_REDIS:
        import fakeredis.aioredis as fake_aio
        r = fake_aio.FakeRedis(
            server=_get_fakeredis_server(),
            encoding="utf-8",
            decode_responses=True,
        )
    else:
        import redis.asyncio as aioredis
        r = await aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    pubsub = r.pubsub()
    await pubsub.subscribe(_channel(job_id))
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    yield json.loads(message["data"])
                except Exception:
                    pass
    finally:
        await pubsub.unsubscribe(_channel(job_id))
        await r.aclose()
