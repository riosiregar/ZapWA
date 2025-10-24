from app.services.warmup_service import start, stop


async def warmup_start(session_id: str):
    await start(session_id)
    return {"ok": True}


async def warmup_stop(session_id: str):
    await stop(session_id)
    return {"ok": True}
