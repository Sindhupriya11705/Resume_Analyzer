from __future__ import annotations

import asyncio
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from pydantic import BaseModel


class Settings(BaseModel):
    JWT_SECRET: str = "dev_only_change_me"
    JWT_ALG: str = "HS256"


settings = Settings()


def _load_env():
    import os

    settings.JWT_SECRET = os.getenv("JWT_SECRET", settings.JWT_SECRET)
    settings.JWT_ALG = os.getenv("JWT_ALG", settings.JWT_ALG)


class ConnectionManager:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.active: dict[str, set[WebSocket]] = {"global": set()}

    async def connect(self, websocket: WebSocket, room: str = "global"):
        await websocket.accept()
        async with self._lock:
            self.active.setdefault(room, set()).add(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            for room in list(self.active.keys()):
                self.active[room].discard(websocket)
                if room != "global" and not self.active[room]:
                    self.active.pop(room, None)

    async def broadcast(self, payload: dict[str, Any], room: str = "global"):
        async with self._lock:
            sockets = list(self.active.get(room, set())) + list(self.active.get("global", set()))
        dead: list[WebSocket] = []
        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws)


manager = ConnectionManager()
app = FastAPI(title="SkillForge Realtime", version="0.1.0")


@app.on_event("startup")
async def startup():
    _load_env()


@app.get("/health")
async def health():
    return {"ok": True}


def _verify_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token", "")
    room = websocket.query_params.get("room", "global")
    if token:
        try:
            _verify_token(token)
        except JWTError:
            await websocket.close(code=4401)
            return

    await manager.connect(websocket, room=room)
    try:
        while True:
            msg = await websocket.receive_json()
            # Minimal protocol: client can join rooms.
            if isinstance(msg, dict) and msg.get("type") == "join" and isinstance(msg.get("room"), str):
                await manager.disconnect(websocket)
                await manager.connect(websocket, room=msg["room"])
                await websocket.send_json({"event": "room:joined", "data": {"room": msg["room"]}})
            else:
                await websocket.send_json({"event": "echo", "data": msg})
    except WebSocketDisconnect:
        await manager.disconnect(websocket)


class BroadcastRequest(BaseModel):
    event: str
    data: dict[str, Any]
    room: str = "global"


@app.post("/broadcast")
async def broadcast(req: BroadcastRequest):
    await manager.broadcast({"event": req.event, "data": req.data}, room=req.room)
    return {"ok": True}

