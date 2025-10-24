from fastapi import APIRouter, UploadFile, File
from app.controllers import verify_controller as c
from app.utils.schemas import JobCreateResp, JobStatusResp

router = APIRouter(prefix="/verify", tags=["verify"])


@router.post("/upload", response_model=JobCreateResp)
async def upload(file: UploadFile = File(...)):
    return await c.upload_excel(file)


@router.get("/status/{job_id}", response_model=JobStatusResp)
async def status(job_id: int):
    return await c.job_status(job_id)


@router.get("/results/{job_id}")
async def results(job_id: int):
    return await c.job_results(job_id)
