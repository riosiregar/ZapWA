from sqlalchemy import Integer, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.models.enums import JobStatus


class VerifyJob(Base):
    __tablename__ = "verify_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.queued)
    total: Mapped[int] = mapped_column(Integer, default=0)
    has_wa: Mapped[int] = mapped_column(Integer, default=0)
    no_wa: Mapped[int] = mapped_column(Integer, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)
