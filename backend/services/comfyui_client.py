import json
import asyncio
import logging
from typing import Optional, AsyncGenerator
import websockets
import httpx

from config import settings

logger = logging.getLogger(__name__)



# ---------------------------------------------------------------------------
# ComfyUI Client
# ---------------------------------------------------------------------------

class ComfyUIClient:
    def __init__(self):
        self.base_url = settings.COMFYUI_BASE_URL
        self.ws_url = settings.COMFYUI_WS_URL
        self.timeout = httpx.Timeout(10.0, read=30.0)

    async def health_check(self) -> bool:
        """Returns True if ComfyUI is reachable."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.get(f"{self.base_url}/system_stats")
                return r.status_code == 200
        except Exception as e:
            logger.warning(f"ComfyUI health check failed: {e}")
            return False

    async def queue_prompt(self, workflow: dict, client_id: str) -> str:
        """Submit a workflow and return the prompt_id."""
        payload = {"prompt": workflow, "client_id": client_id}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/prompt", json=payload)
            r.raise_for_status()
            data = r.json()
            prompt_id = data.get("prompt_id")
            if not prompt_id:
                raise RuntimeError(f"ComfyUI did not return prompt_id: {data}")
            return prompt_id

    async def get_history(self, prompt_id: str) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(f"{self.base_url}/history/{prompt_id}")
            if r.status_code == 200:
                return r.json().get(prompt_id)
        return None

    async def get_image_bytes(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            r = await client.get(f"{self.base_url}/view", params=params)
            r.raise_for_status()
            return r.content

    async def stream_progress(
        self,
        prompt_id: str,
        client_id: str,
        progress_callback=None,
    ) -> AsyncGenerator[dict, None]:
        """
        Connect to ComfyUI WebSocket and yield progress events until completion.
        """
        ws_url = f"{self.ws_url}?clientId={client_id}"
        try:
            async with websockets.connect(ws_url) as ws:
                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                    except Exception:
                        continue

                    msg_type = msg.get("type")
                    data = msg.get("data", {})

                    if msg_type == "progress":
                        step = data.get("value", 0)
                        total = data.get("max", 1)
                        pct = int((step / max(total, 1)) * 100)
                        event = {"type": "progress", "progress": pct, "step": step, "total": total}
                        if progress_callback:
                            await progress_callback(event)
                        yield event

                    elif msg_type == "executing":
                        if data.get("node") is None and data.get("prompt_id") == prompt_id:
                            # Execution finished
                            yield {"type": "completed", "progress": 100}
                            return

                    elif msg_type == "execution_error":
                        error = data.get("exception_message", "Unknown ComfyUI error")
                        yield {"type": "error", "message": error}
                        return

        except Exception as e:
            logger.error(f"WebSocket stream error: {e}")
            yield {"type": "error", "message": str(e)}

    async def extract_output_images(self, history: dict) -> list[str]:
        """Parse history dict → list of output filenames."""
        filenames = []
        for node_id, node_output in history.get("outputs", {}).items():
            images = node_output.get("images", [])
            for img in images:
                filenames.append(img["filename"])
        return filenames


comfyui_client = ComfyUIClient()
