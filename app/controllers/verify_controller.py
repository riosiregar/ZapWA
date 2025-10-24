from fastapi import UploadFile, File, HTTPException, Depends
from sqlalchemy import select
from app.services.verify_service import queue_verify_job
from app.models.verify_job import VerifyJob
from app.models.verify_result import VerifyResult
from app.utils.schemas import JobCreateResp, JobStatusResp
from app.config.db import get_db


async def upload_excel(file: UploadFile = File(...)) -> JobCreateResp:
    if not file.filename.lower().endswith((".xlsx", ".xlsm", ".xltx", ".xltm")):
        raise HTTPException(400, "File harus Excel (.xlsx)")
    data = await file.read()
    job_id = await queue_verify_job(data)
    return JobCreateResp(job_id=job_id)


async def job_status(job_id: int, db=Depends(get_db)) -> JobStatusResp:
    job = (
        await db.execute(select(VerifyJob).where(VerifyJob.id == job_id))
    ).scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Job tidak ditemukan")
    return JobStatusResp(
        job_id=job.id,
        status=job.status.value,
        total=job.total,
        has_wa=job.has_wa,
        no_wa=job.no_wa,
        duplicates=job.duplicates,
        error=job.error,
    )


async def job_results(job_id: int, db=Depends(get_db)):
    rows = (
        await db.execute(select(VerifyResult).where(VerifyResult.job_id == job_id))
    ).all()
    return [
        {"phone": r[0].phone_e164, "raw": r[0].raw_input, "status": r[0].status}
        for r in rows
    ]
