"""
Database Connection Management
"""
import logging
import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from src.config.settings import settings
from src.config.database import database_settings

logger = logging.getLogger(__name__)

# Base class for models
Base = declarative_base()

# Engine and session factory
engine = None
async_session_maker = None


def get_engine_kwargs():
    """Get engine configuration based on environment"""
    kwargs = {
        "echo": database_settings.ECHO,
        "pool_size": database_settings.POOL_SIZE,
        "max_overflow": database_settings.MAX_OVERFLOW,
        "pool_timeout": database_settings.POOL_TIMEOUT,
        "pool_recycle": database_settings.POOL_RECYCLE,
    }
    
    # For Render PostgreSQL, we need to handle SSL
    if "render.com" in settings.DATABASE_URL:
        # Render PostgreSQL requires SSL
        connect_args = {
            "ssl": "require"
        }
        kwargs["connect_args"] = connect_args
        logger.info("Using SSL connection for Render PostgreSQL")
    
    return kwargs


async def init_database():
    """Initialize database connection with retry logic"""
    global engine, async_session_maker
    
    logger.info("Initializing database connection...")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    
    max_retries = database_settings.MAX_RETRIES
    retry_delay = database_settings.RETRY_DELAY
    
    for attempt in range(1, max_retries + 1):
        try:
            engine_kwargs = get_engine_kwargs()
            
            engine = create_async_engine(
                settings.DATABASE_URL,
                **engine_kwargs
            )
            
            async_session_maker = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False
            )
            
            # Test connection
            async with engine.connect() as conn:
                result = await conn.execute("SELECT 1")
                await result.fetchone()
            
            logger.info("Database connection test successful")
            
            # Create tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database initialized successfully")
            return
            
        except Exception as e:
            logger.error(f"Database connection attempt {attempt}/{max_retries} failed: {e}")
            
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("All database connection attempts failed")
                raise


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


async def check_database_health() -> bool:
    """Check if database connection is healthy"""
    try:
        if not engine:
            return False
        
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            await result.fetchone()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
