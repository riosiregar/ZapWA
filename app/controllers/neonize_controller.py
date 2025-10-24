# app/controllers/neonize_controller.py
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import pandas as pd

from app.services.neonize_service import neonize
from app.helpers.phone import extract_msisdn_from_any

router = APIRouter(prefix="/neonize", tags=["neonize"])


@router.post("/start")
async def start_neonize(bg: BackgroundTasks):
    bg.add_task(neonize.boot)
    return {"status": "starting"}


@router.get("/qr")
async def get_qr():
    b64 = neonize.get_last_qr()
    if not b64:
        raise HTTPException(404, "QR belum tersedia")
    return {"png_b64": b64}


@router.get("/whoami")
async def whoami():
    return {"user": neonize.get_last_pair_user()}


@router.post("/destroy")
async def destroy():
    await neonize.destroy_sessions()
    return {"status": "ok"}


@router.post("/warmup")
async def warmup_now():
    await neonize.presence_now()
    return {"status": "ok"}


@router.post("/verify/excel")
async def verify_excel(file: UploadFile = File(...)):
    # Pandas + openpyxl
    df = pd.read_excel(file.file, dtype=str, engine="openpyxl")
    # Ambil semua sel yang mirip nomor
    numbers = extract_msisdn_from_any(df)
    result = await neonize.verify_numbers(numbers)
    return result
