"""
Configuration module
"""
from src.config.settings import settings, Settings, get_settings
from src.config.database import database_settings, DatabaseSettings
from src.config.telegram import telegram_settings, TelegramSettings

__all__ = [
    "settings",
    "Settings",
    "get_settings",
    "database_settings",
    "DatabaseSettings",
    "telegram_settings",
    "TelegramSettings",
]
