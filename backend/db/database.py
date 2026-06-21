
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import get_settings
from db.base import Base

settings = get_settings()


def _resolve_async_database_url() -> str:
    if hasattr(settings, "async_database_url"):
        return settings.async_database_url

    user = getattr(settings, "POSTGRES_USER", None) or getattr(settings, "database_user", "admin")
    password = getattr(settings, "POSTGRES_PASSWORD", None) or getattr(settings, "database_password", "admin_tca")
    if hasattr(password, "get_secret_value"):
        password = password.get_secret_value()

    host = getattr(settings, "POSTGRES_HOST", None) or getattr(settings, "database_host", "localhost")
    port = getattr(settings, "POSTGRES_PORT", None) or getattr(settings, "database_port", 5433)
    database = getattr(settings, "POSTGRES_DB", None) or getattr(settings, "database_name", "tca_chatbot")

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"


engine = create_async_engine(_resolve_async_database_url(), echo=False)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)