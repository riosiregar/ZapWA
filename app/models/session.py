from sqlalchemy import String, Enum, LargeBinary, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.models.base import Base
from app.models.enums import SessionStatus


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    phone: Mapped[str | None] = mapped_column(String(32))
    pushname: Mapped[str | None] = mapped_column(String(128))
    device: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), default=SessionStatus.disconnected
    )
    session_blob: Mapped[bytes | None] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )
