from fastapi import APIRouter
from .session import router as session_router
from .verify import router as verify_router
from .warmup import router as warmup_router

api = APIRouter()
api.include_router(session_router)
api.include_router(verify_router)
api.include_router(warmup_router)
