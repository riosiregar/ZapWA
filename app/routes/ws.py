# app/routes/ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.ws_hub import ws_hub

router = APIRouter()


@router.websocket("/ws/neonize")
async def ws_neonize(ws: WebSocket):
    await ws_hub.connect(ws)
    try:
        while True:
            await ws.receive_text()  # optional ping from client UI
    except WebSocketDisconnect:
        await ws_hub.disconnect(ws)
