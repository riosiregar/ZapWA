from pydantic import BaseModel


class CreateSessionReq(BaseModel):
    session_id: str


class SessionInfo(BaseModel):
    id: str
    status: str
    phone: str | None = None
    pushname: str | None = None
    device: str | None = None


class JobCreateResp(BaseModel):
    job_id: int


class JobStatusResp(BaseModel):
    job_id: int
    status: str
    total: int
    has_wa: int
    no_wa: int
    duplicates: int
    error: str | None = None
