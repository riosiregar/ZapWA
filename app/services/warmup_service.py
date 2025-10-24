import asyncio
from app.config.settings import get_settings
from app.services.neonize_manager import registry

settings = get_settings()
_tasks: dict[str, asyncio.Task] = {}


async def start(session_id: str):
    if session_id in _tasks and not _tasks[session_id].done():
        return

    async def loop():
        client = await registry.get(session_id)
        while True:
            await client.ping()
            await asyncio.sleep(settings.PING_INTERVAL_SEC)

    _tasks[session_id] = asyncio.create_task(loop())


async def stop(session_id: str):
    t = _tasks.get(session_id)
    if t:
        t.cancel()
