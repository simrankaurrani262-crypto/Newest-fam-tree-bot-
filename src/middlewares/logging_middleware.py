"""
Logging Middleware
"""
import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Log all incoming updates"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        if isinstance(event, Message):
            if event.text and event.text.startswith('/'):
                logger.info(
                    f"Command: {event.text} | "
                    f"User: {event.from_user.id} (@{event.from_user.username}) | "
                    f"Chat: {event.chat.id}"
                )
        
        return await handler(event, data)
