from fastapi import Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy import select
from app.config.db import get_db
from app.models.session import Session
from app.utils.schemas import CreateSessionReq, SessionInfo
from app.services.neonize_manager import registry


async def create_session(req: CreateSessionReq, db=Depends(get_db)) -> SessionInfo:
    client = await registry.get(req.session_id)
    await client.connect()
    sess = (
        await db.execute(select(Session).where(Session.id == req.session_id))
    ).scalar_one()
    return SessionInfo(
        id=sess.id,
        status=sess.status.value,
        phone=sess.phone,
        pushname=sess.pushname,
        device=sess.device,
    )


async def qr_ws(ws: WebSocket, session_id: str):
    await ws.accept()
    client = await registry.get(session_id)
    try:
        while True:
            qr_b64 = await client.get_qr()
            if qr_b64:
                await ws.send_json({"type": "qr", "image": qr_b64, "expires_in": 60})
            else:
                await ws.send_json({"type": "heartbeat"})
    except WebSocketDisconnect:
        pass


async def info(session_id: str, db=Depends(get_db)) -> SessionInfo:
    sess = (
        await db.execute(select(Session).where(Session.id == session_id))
    ).scalar_one_or_none()
    if not sess:
        raise HTTPException(404, "Session tidak ditemukan")
    return SessionInfo(
        id=sess.id,
        status=sess.status.value,
        phone=sess.phone,
        pushname=sess.pushname,
        device=sess.device,
    )


async def destroy(session_id: str):
    client = await registry.get(session_id)
    await client.destroy()
    return {"ok": True}
