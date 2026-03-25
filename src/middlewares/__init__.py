"""
Middlewares Module
"""
from aiogram import Dispatcher

from src.middlewares.logging_middleware import LoggingMiddleware
from src.middlewares.rate_limit_middleware import RateLimitMiddleware
from src.middlewares.user_middleware import UserMiddleware


def setup_middlewares(dp: Dispatcher):
    """Setup all middlewares"""
    # Add middlewares in order (outer to inner)
    dp.update.outer_middleware(LoggingMiddleware())
    dp.update.outer_middleware(RateLimitMiddleware())
    dp.update.outer_middleware(UserMiddleware())
