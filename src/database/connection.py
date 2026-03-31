"""
Database Connection Management
"""
import logging
import asyncio
import ssl
from typing import AsyncGenerator, Optional
from urllib.parse import urlparse, parse_qs
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


def get_database_url() -> str:
    """Get database URL with validation"""
    db_url = settings.DATABASE_URL
    
    if not db_url:
        # Construct from individual components
        if settings.DB_PASSWORD:
            db_url = (
                f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
                f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
            )
        else:
            db_url = (
                f"postgresql+asyncpg://{settings.DB_USER}@{settings.DB_HOST}"
                f":{settings.DB_PORT}/{settings.DB_NAME}"
            )
    
    # Validate URL
    if not db_url or "@" not in db_url:
        logger.error("❌ DATABASE_URL is not properly configured!")
        logger.error("   Please set DATABASE_URL or DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        raise ValueError("DATABASE_URL is required but not properly configured")
    
    # Remove any ssl/sslmode query params from URL - we'll handle SSL via connect_args
    db_url = _remove_ssl_params(db_url)
    
    return db_url


def _remove_ssl_params(db_url: str) -> str:
    """Remove SSL parameters from URL as we'll handle them via connect_args"""
    parsed = urlparse(db_url)
    query_params = parse_qs(parsed.query)
    
    # Remove ssl and sslmode params
    query_params.pop('ssl', None)
    query_params.pop('sslmode', None)
    
    # Rebuild query string
    from urllib.parse import urlencode, urlunparse
    new_query = urlencode(query_params, doseq=True) if query_params else ""
    
    # Rebuild URL
    new_url = urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
    )
    
    return new_url


def get_engine_kwargs():
    """Get engine configuration based on environment"""
    kwargs = {
        "echo": database_settings.ECHO,
        "pool_size": database_settings.POOL_SIZE,
        "max_overflow": database_settings.MAX_OVERFLOW,
        "pool_timeout": database_settings.POOL_TIMEOUT,
        "pool_recycle": database_settings.POOL_RECYCLE,
    }
    
    db_url = get_database_url()
    
    # For Render PostgreSQL or external databases, use SSL
    if "render.com" in db_url or "amazonaws.com" in db_url or "supabase.co" in db_url:
        # For asyncpg, we use ssl=True to enable SSL without verification
        # This works with Render's self-signed certificates
        kwargs["connect_args"] = {"ssl": True}
        logger.info("Using SSL=True for PostgreSQL connection")
    
    return kwargs


async def init_database():
    """Initialize database connection with retry logic"""
    global engine, async_session_maker
    
    logger.info("Initializing database connection...")
    
    try:
        db_url = get_database_url()
        # Mask password for logging
        safe_url = db_url
        if "@" in db_url:
            parts = db_url.split("@")
            safe_url = f"***@{parts[1]}"
        logger.info(f"Database URL: {safe_url}")
    except ValueError as e:
        logger.error(f"Database configuration error: {e}")
        raise
    
    max_retries = database_settings.MAX_RETRIES
    retry_delay = database_settings.RETRY_DELAY
    
    for attempt in range(1, max_retries + 1):
        try:
            engine_kwargs = get_engine_kwargs()
            
            engine = create_async_engine(
                get_database_url(),
                **engine_kwargs
            )
            
            async_session_maker = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False
            )
            
            # Test connection
            from sqlalchemy import text

            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                result.fetchone()
            
            logger.info("✅ Database connection test successful")
            
            # Create tables
            logger.info("Creating database tables...")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("✅ Database initialized successfully")
            return
            
        except Exception as e:
            logger.error(f"❌ Database connection attempt {attempt}/{max_retries} failed: {e}")
            
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("❌ All database connection attempts failed")
                logger.error("   Please check your database configuration:")
                logger.error("   - Ensure PostgreSQL is running")
                logger.error("   - Check your DATABASE_URL or DB_* settings")
                logger.error("   - Verify database credentials are correct")
                logger.error("   - Check if your IP is whitelisted in Render dashboard")
                raise


async def close_database():
    """Close database connection"""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    if not async_session_maker:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
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
        
        from sqlalchemy import text
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
.fetchone()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
    
