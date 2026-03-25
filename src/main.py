"""
Fam Tree Bot - Main Entry Point
"""
import asyncio
import logging
import sys

from src.config.settings import settings
from src.bot import create_bot, start_bot
from src.database.connection import init_database, close_database
from src.core.logging import setup_logging


async def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 50)
    logger.info("🌳 Fam Tree Bot Starting...")
    logger.info(f"Version: 1.0.0")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("=" * 50)
    
    try:
        # Initialize database
        logger.info("📦 Initializing database...")
        await init_database()
        logger.info("✅ Database initialized")
        
        # Create and start bot
        logger.info("🤖 Creating bot...")
        bot, dp = await create_bot()
        
        logger.info("🚀 Starting bot...")
        await start_bot(bot, dp)
        
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.exception(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        logger.info("🧹 Cleaning up...")
        await close_database()
        logger.info("✅ Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main())
