from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.adapters.orm import start_mappers
from app.common.settings import StageEnum, db_settings, settings

engine: AsyncEngine | None = None
autocommit_engine: AsyncEngine | None = None
async_transactional_session_factory: sessionmaker | None = None
async_autocommit_session_factory: sessionmaker | None = None


if settings.stage != StageEnum.TEST or settings.working_on_pipeline is True:
    engine = create_async_engine(
        db_settings.url,
        pool_pre_ping=True,
        pool_size=db_settings.pool_size,
        max_overflow=db_settings.max_overflow,
        future=True,
    )
    async_transactional_session_factory = sessionmaker(
        engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
    )
    autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")
    async_autocommit_session_factory = sessionmaker(autocommit_engine, expire_on_commit=False, class_=AsyncSession)
    start_mappers()
