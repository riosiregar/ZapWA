import asyncio
import pandas as pd
from sqlalchemy import insert, update, select
from app.config.db import AsyncSessionLocal
from app.models.verify_job import VerifyJob
from app.models.verify_result import VerifyResult
from app.models.enums import JobStatus
from app.helpers.phone import normalize_id_phone
from app.services.neonize_manager import registry


async def queue_verify_job(file_bytes: bytes) -> int:
    # parse excel
    import pandas as pd
    from io import BytesIO

    df = pd.read_excel(BytesIO(file_bytes), engine="openpyxl")
    col = df.columns[0]
    df["raw"] = df[col].astype(str)
    df["phone_e164"] = df["raw"].map(normalize_id_phone)
    dup_mask = df.duplicated("phone_e164", keep="first")

    async with AsyncSessionLocal() as db:
        res = await db.execute(
            insert(VerifyJob).values(
                status=JobStatus.queued, total=len(df), duplicates=int(dup_mask.sum())
            )
        )
        await db.commit()
        job_id = res.inserted_primary_key[0]

    asyncio.create_task(_run_job(job_id, df, dup_mask))
    return job_id


async def _run_job(job_id: int, df: pd.DataFrame, dup_mask):
    async with AsyncSessionLocal() as db:
        await db.execute(
            update(VerifyJob)
            .where(VerifyJob.id == job_id)
            .values(status=JobStatus.running)
        )
        await db.commit()

    has_wa = no_wa = 0
    neon = await registry.get("default")  # atau session_id yg sedang aktif

    for idx, row in df.iterrows():
        phone = row["phone_e164"]
        raw = row["raw"]
        if dup_mask.loc[idx]:
            status = "DUPLICATE"
        else:
            ok = await neon.is_registered(phone)
            status = "HAS_WA" if ok else "NO_WA"
            has_wa += int(ok)
            no_wa += int(not ok)

        async with AsyncSessionLocal() as db:
            await db.execute(
                insert(VerifyResult).values(
                    job_id=job_id, phone_e164=phone, raw_input=raw, status=status
                )
            )
            await db.commit()

    async with AsyncSessionLocal() as db:
        await db.execute(
            update(VerifyJob)
            .where(VerifyJob.id == job_id)
            .values(status=JobStatus.done, has_wa=has_wa, no_wa=no_wa)
        )
        await db.commit()
