"""
Rate Limit Middleware
"""
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from src.core.rate_limiter import rate_limiter


class RateLimitMiddleware(BaseMiddleware):
    """Rate limit middleware"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        if isinstance(event, Message) and event.text:
            # Skip rate limiting for non-commands
            if not event.text.startswith('/'):
                return await handler(event, data)
            
            # Extract command name
            command = event.text.split()[0].replace('/', '').split('@')[0]
            
            # Check rate limit
            is_allowed, retry_after = await rate_limiter.is_allowed(
                user_id=event.from_user.id,
                command=command,
                max_requests=30,
                window=60
            )
            
            if not is_allowed:
                await event.reply(
                    f"⏳ <b>Rate Limited!</b>\n"
                    f"Please wait {retry_after} seconds."
                )
                return None
        
        return await handler(event, data)
