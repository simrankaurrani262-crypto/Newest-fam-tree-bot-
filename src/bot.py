"""
Telegram Bot Instance and Setup
"""
import asyncio
import logging
from typing import Tuple

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.config.settings import settings
from src.config.telegram import telegram_settings
from src.handlers.router import setup_routers
from src.middlewares import setup_middlewares
from src.core.state_machine import state_manager
from src.core.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)


async def create_bot() -> Tuple[Bot, Dispatcher]:
    """Create and configure bot instance"""
    
    # Validate BOT_TOKEN
    if not telegram_settings.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN is not set! Please set the BOT_TOKEN environment variable.")
        logger.error("   You can get a bot token from @BotFather on Telegram.")
        raise ValueError("BOT_TOKEN is required but not set")
    
    # Initialize Redis-dependent components
    logger.info("Initializing Redis-dependent components...")
    await state_manager.init()
    await rate_limiter.init()
    
    # Create bot
    bot = Bot(
        token=telegram_settings.BOT_TOKEN,
        parse_mode=ParseMode.HTML
    )
    
    # Get bot info
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot: @{bot_info.username} (ID: {bot_info.id})")
    except Exception as e:
        logger.error(f"Failed to get bot info: {e}")
        logger.error("Please check if your BOT_TOKEN is valid.")
        raise
    
    # Create dispatcher with Memory storage (no Redis needed)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Setup middlewares
    setup_middlewares(dp)
    
    # Setup routers
    setup_routers(dp)
    
    return bot, dp


async def start_bot(bot: Bot, dp: Dispatcher):
    """Start the bot"""
    
    if telegram_settings.WEBHOOK_ENABLED:
        # Webhook mode (production)
        logger.info("Starting in webhook mode...")
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
        from aiohttp import web
        
        app = web.Application()
        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=telegram_settings.WEBHOOK_SECRET
        )
        webhook_handler.register(app, path=telegram_settings.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        # Set webhook
        await bot.set_webhook(
            url=f"{telegram_settings.WEBHOOK_HOST}{telegram_settings.WEBHOOK_PATH}",
            secret_token=telegram_settings.WEBHOOK_SECRET
        )
        
        # Run web server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=telegram_settings.WEBHOOK_PORT)
        await site.start()
        
        logger.info(f"Webhook server started on port {telegram_settings.WEBHOOK_PORT}")
        
        # Keep running
        while True:
            await asyncio.sleep(3600)
    else:
        # Polling mode (development)
        logger.info("Starting in polling mode...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    
