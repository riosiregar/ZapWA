# main.py
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.config.db import engine
from app.logs.logging_conf import setup_logging
from app.models.base import Base
from app.routes import api  # router gabungan
from app.services.neonize_service import neonize  # <-- start/stop neonize di lifecycle

settings = get_settings()
setup_logging()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # boot neonize (QR, events, keepalive) sebagai background task
    asyncio.create_task(neonize.boot())


@app.on_event("shutdown")
async def shutdown():
    # rapikan sesi WA & DB
    try:
        await neonize.destroy_sessions()
    finally:
        await engine.dispose()


# optional: health check sederhana
@app.get("/healthz")
async def healthz():
    return {"ok": True}


# register all routes (REST + WS)
app.include_router(api)
