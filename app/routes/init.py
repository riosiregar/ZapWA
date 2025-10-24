from fastapi import APIRouter
from app.controllers import neonize_controller
from app.routes import ws as ws_routes

router = APIRouter()
router.include_router(neonize_controller.router)
router.include_router(ws_routes.router)
