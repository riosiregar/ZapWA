from fastapi import APIRouter
from app.controllers import warmup_controller as c

router = APIRouter(prefix="/warmup", tags=["warmup"])


@router.post("/start/{session_id}")
async def start(session_id: str):
    return await c.warmup_start(session_id)


@router.post("/stop/{session_id}")
async def stop(session_id: str):
    return await c.warmup_stop(session_id)
