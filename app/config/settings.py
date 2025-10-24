from pydantic import BaseModel
import os
from functools import lru_cache


class Settings(BaseModel):
    APP_NAME: str = "WA Backend"
    DB_URI: str = os.getenv(
        "DB_URI", "mysql+aiomysql://user:pass@localhost:3306/wa_backend"
    )
    PING_INTERVAL_SEC: int = int(os.getenv("PING_INTERVAL_SEC", 60))
    QR_EXPIRE_SEC: int = 60
    CORS_ORIGINS: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
