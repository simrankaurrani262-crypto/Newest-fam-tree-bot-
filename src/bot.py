"""
Telegram Bot Instance and Setup
"""
import logging
from typing import Tuple

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from src.config.settings import settings
from src.config.telegram import telegram_settings
from src.handlers.router import setup_routers
from src.middlewares import setup_middlewares
from src.core.state_machine import state_manager

logger = logging.getLogger(__name__)


async def create_bot() -> Tuple[Bot, Dispatcher]:
    """Create and configure bot instance"""
    
    # Create bot
    bot = Bot(
        token=telegram_settings.BOT_TOKEN,
        parse_mode=ParseMode.HTML
    )
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"Bot: @{bot_info.username} (ID: {bot_info.id})")
    
    # Create dispatcher with Redis storage
    storage = RedisStorage.from_url(settings.REDIS_URL)
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


import asyncio
