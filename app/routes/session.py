from fastapi import APIRouter, WebSocket
from app.controllers import session_controller as c
from app.utils.schemas import CreateSessionReq, SessionInfo

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/create", response_model=SessionInfo)
async def create(req: CreateSessionReq):
    return await c.create_session(req)


@router.websocket("/qr/{session_id}")
async def qr(ws: WebSocket, session_id: str):
    return await c.qr_ws(ws, session_id)


@router.get("/info/{session_id}", response_model=SessionInfo)
async def info(session_id: str):
    return await c.info(session_id)


@router.delete("/{session_id}")
async def destroy(session_id: str):
    return await c.destroy(session_id)
