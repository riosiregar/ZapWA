from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class VerifyResult(Base):
    __tablename__ = "verify_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("verify_jobs.id", ondelete="CASCADE")
    )
    phone_e164: Mapped[str] = mapped_column(String(32))
    raw_input: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16))  # HAS_WA / NO_WA / DUPLICATE
