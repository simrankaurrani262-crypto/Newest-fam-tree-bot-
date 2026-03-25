"""
Database Connection Management
"""
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base

from src.config.settings import settings
from src.config.database import database_settings

logger = logging.getLogger(__name__)

# Base class for models
Base = declarative_base()

# Engine and session factory
engine = None
async_session_maker = None


async def init_database():
    """Initialize database connection"""
    global engine, async_session_maker
    
    logger.info("Initializing database connection...")
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=database_settings.ECHO,
        pool_size=database_settings.POOL_SIZE,
        max_overflow=database_settings.MAX_OVERFLOW,
        pool_timeout=database_settings.POOL_TIMEOUT,
        pool_recycle=database_settings.POOL_RECYCLE
    )
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialized successfully")


async def close_database():
    """Close database connection"""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncSession:
    """Get database session (for dependency injection)"""
    async with async_session_maker() as session:
        return session
