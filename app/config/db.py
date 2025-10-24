from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config.settings import get_settings

settings = get_settings()
engine = create_async_engine(settings.DB_URI, pool_pre_ping=True, pool_recycle=3600)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as s:
        yield s
