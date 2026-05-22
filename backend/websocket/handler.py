"""
FastAPI WebSocket endpoint.
Clients connect to ws://.../ws/jobs/{job_id} to receive real-time updates.
The handler subscribes to the Redis pub/sub channel for that job.
"""
import asyncio
import json
import logging
from typing import Dict, Set

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from services.redis_client import subscribe_job_events, get_job_state

logger = logging.getLogger(__name__)

# Track active connections per job for cleanup
_connections: Dict[str, Set[WebSocket]] = {}


async def job_websocket_handler(job_id: str, websocket: WebSocket):
    await websocket.accept()
    logger.info(f"WS connected: job={job_id}")

    # Register connection
    _connections.setdefault(job_id, set()).add(websocket)

    try:
        # Send current state immediately so client doesn't wait
        current = await get_job_state(job_id)
        if current:
            await websocket.send_text(json.dumps(current))

        # Subscribe and relay events
        async for event in subscribe_job_events(job_id):
            if websocket.client_state != WebSocketState.CONNECTED:
                break
            try:
                await websocket.send_text(json.dumps(event))
            except Exception:
                break

            # Stop relaying once terminal state is reached
            if event.get("type") in ("completed", "error"):
                break

    except WebSocketDisconnect:
        logger.info(f"WS disconnected: job={job_id}")
    except Exception as e:
        logger.error(f"WS error job={job_id}: {e}")
    finally:
        _connections.get(job_id, set()).discard(websocket)
        try:
            await websocket.close()
        except Exception:
            pass
