# app/utils/ws_hub.py
from typing import Set
from fastapi import WebSocket
import asyncio
import json


class WSHub:
    def __init__(self):
        self.conns: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self.conns.add(ws)

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            self.conns.discard(ws)

    async def broadcast_json(self, data: dict):
        payload = json.dumps(data)
        async with self._lock:
            for ws in list(self.conns):
                try:
                    await ws.send_text(payload)
                except Exception:
                    self.conns.discard(ws)


ws_hub = WSHub()
