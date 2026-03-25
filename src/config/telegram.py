"""
Telegram Bot Configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class TelegramSettings(BaseSettings):
    """Telegram-specific settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="",
        case_sensitive=False
    )
    
    # Bot Settings
    BOT_TOKEN: str = Field(default="", alias="BOT_TOKEN")
    BOT_USERNAME: str = Field(default="", alias="BOT_USERNAME")
    
    # Webhook Settings
    WEBHOOK_URL: str = Field(default="", alias="WEBHOOK_URL")
    WEBHOOK_SECRET: str = Field(default="", alias="WEBHOOK_SECRET")
    
    # Polling Settings
    POLLING_TIMEOUT: int = Field(default=30, alias="POLLING_TIMEOUT")
    
    # Rate Limiting
    RATE_LIMIT_MESSAGES: int = Field(default=30, alias="RATE_LIMIT_MESSAGES")
    RATE_LIMIT_WINDOW: int = Field(default=60, alias="RATE_LIMIT_WINDOW")


telegram_settings = TelegramSettings()
