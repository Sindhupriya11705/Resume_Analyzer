import httpx

from app.core.config import settings


async def broadcast(event: str, data: dict, room: str = "global"):
    url = f"http://{settings.WS_SERVER_HOST}:{settings.WS_SERVER_PORT}/broadcast"
    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            await client.post(url, json={"event": event, "data": data, "room": room})
        except Exception:
            # Realtime is best-effort; API should still succeed.
            return

