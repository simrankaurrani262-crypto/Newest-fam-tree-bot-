"""
Decorators for Fam Tree Bot
"""
import functools
import logging
from typing import Callable, Optional
from datetime import datetime, timedelta

from aiogram import types
from aiogram.exceptions import TelegramAPIError

from src.core.exceptions import (
    ValidationError,
    RateLimitError,
    UserNotFoundError,
    FamTreeBotException
)
from src.core.rate_limiter import rate_limiter
from src.database.repositories.user_repo import UserRepository
from src.database.connection import get_session

logger = logging.getLogger(__name__)


def require_user(create_if_missing: bool = True):
    """
    Decorator to ensure user exists in database.
    Creates user if not found and create_if_missing is True.
    """
    def decorator(handler: Callable):
        @functools.wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            async for session in get_session():
                user_repo = UserRepository(session)
                try:
                    user = await user_repo.get_by_telegram_id(message.from_user.id)
                    if not user and create_if_missing:
                        user = await user_repo.create_from_telegram_user(message.from_user)
                        logger.info(f"Created new user: {user.telegram_id}")
                    
                    if not user:
                        raise UserNotFoundError("User not found")
                    
                    # Add user to kwargs
                    kwargs["db_user"] = user
                    kwargs["session"] = session  # Also pass session for reuse
                    return await handler(message, *args, **kwargs)
                except Exception as e:
                    logger.exception(f"Error in require_user decorator: {e}")
                    raise
        return wrapper
    return decorator


def rate_limit(command: str, max_requests: int = 30, window: int = 60):
    """
    Decorator to rate limit commands.
    
    Args:
        command: Command name for rate limiting
        max_requests: Maximum requests allowed in window
        window: Time window in seconds
    """
    def decorator(handler: Callable):
        @functools.wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            user_id = message.from_user.id
            
            is_allowed, retry_after = await rate_limiter.is_allowed(
                user_id=user_id,
                command=command,
                max_requests=max_requests,
                window=window
            )
            
            if not is_allowed:
                await message.reply(
                    f"⏳ <b>Rate Limited!</b>\n"
                    f"Please wait {retry_after} seconds before using this command again."
                )
                raise RateLimitError(retry_after)
            
            return await handler(message, *args, **kwargs)
        return wrapper
    return decorator


def require_reply(error_message: str = "Please reply to a user message."):
    """Decorator to require message to be a reply"""
    def decorator(handler: Callable):
        @functools.wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            if not message.reply_to_message:
                return await message.reply(f"❌ {error_message}")
            return await handler(message, *args, **kwargs)
        return wrapper
    return decorator


def require_group(error_message: str = "This command can only be used in groups."):
    """Decorator to require command to be used in a group"""
    def decorator(handler: Callable):
        @functools.wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            if message.chat.type == "private":
                return await message.reply(f"❌ {error_message}")
            return await handler(message, *args, **kwargs)
        return wrapper
    return decorator


def require_private(error_message: str = "This command can only be used in private chat."):
    """Decorator to require command to be used in private chat"""
    def decorator(handler: Callable):
        @functools.wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            if message.chat.type != "private":
                return await message.reply(f"❌ {error_message}")
            return await handler(message, *args, **kwargs)
        return wrapper
    return decorator


def handle_errors():
    """Decorator to handle common exceptions"""
    def decorator(handler: Callable):
        @functools.wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            try:
                return await handler(message, *args, **kwargs)
            except ValidationError as e:
                await message.reply(f"❌ {e.message}")
            except FamTreeBotException as e:
                await message.reply(f"❌ {str(e)}")
            except TelegramAPIError as e:
                logger.error(f"Telegram API error: {e}")
                await message.reply("❌ An error occurred. Please try again later.")
            except Exception as e:
                logger.exception(f"Unexpected error in handler: {e}")
                await message.reply("❌ An unexpected error occurred. Our team has been notified.")
        return wrapper
    return decorator


def log_command():
    """Decorator to log command usage"""
    def decorator(handler: Callable):
        @functools.wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            logger.info(
                f"Command: {message.text} | "
                f"User: {message.from_user.id} (@{message.from_user.username}) | "
                f"Chat: {message.chat.id} ({message.chat.type})"
            )
            return await handler(message, *args, **kwargs)
        return wrapper
    return decorator


def admin_required():
    """Decorator to require admin privileges"""
    def decorator(handler: Callable):
        @functools.wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            # Check if user is admin in the chat
            chat_member = await message.bot.get_chat_member(
                chat_id=message.chat.id,
                user_id=message.from_user.id
            )
            
            if chat_member.status not in ["administrator", "creator"]:
                return await message.reply(
                    "❌ <b>Admin Required!</b>\n"
                    "This command can only be used by chat administrators."
                )
            
            return await handler(message, *args, **kwargs)
        return wrapper
    return decorator


def owner_required():
    """Decorator to require bot owner privileges"""
    def decorator(handler: Callable):
        @functools.wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            # Bot owner IDs should be in config
            from src.config.settings import settings
            
            owner_ids = getattr(settings, "BOT_OWNER_IDS", [])
            
            if message.from_user.id not in owner_ids:
                return await message.reply(
                    "❌ <b>Owner Only!</b>\n"
                    "This command can only be used by the bot owner."
                )
            
            return await handler(message, *args, **kwargs)
        return wrapper
    return decorator


def cooldown(seconds: int):
    """Decorator to add cooldown between command uses"""
    cooldowns = {}
    
    def decorator(handler: Callable):
        @functools.wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            user_id = message.from_user.id
            now = datetime.utcnow()
            
            if user_id in cooldowns:
                last_used = cooldowns[user_id]
                elapsed = (now - last_used).total_seconds()
                
                if elapsed < seconds:
                    remaining = int(seconds - elapsed)
                    return await message.reply(
                        f"⏳ <b>Cooldown!</b>\n"
                        f"Please wait {remaining} seconds before using this command again."
                    )
            
            cooldowns[user_id] = now
            return await handler(message, *args, **kwargs)
        return wrapper
    return decorator
