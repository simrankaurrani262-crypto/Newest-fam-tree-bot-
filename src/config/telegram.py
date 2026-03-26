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
    WEBHOOK_ENABLED: bool = Field(default=False, alias="WEBHOOK_ENABLED")
    WEBHOOK_URL: str = Field(default="", alias="WEBHOOK_URL")
    WEBHOOK_SECRET: str = Field(default="", alias="WEBHOOK_SECRET")
    WEBHOOK_HOST: str = Field(default="", alias="WEBHOOK_HOST")
    WEBHOOK_PATH: str = Field(default="/webhook", alias="WEBHOOK_PATH")
    WEBHOOK_PORT: int = Field(default=8443, alias="WEBHOOK_PORT")
    
    # Polling Settings
    POLLING_TIMEOUT: int = Field(default=30, alias="POLLING_TIMEOUT")
    
    # Rate Limiting
    RATE_LIMIT_MESSAGES: int = Field(default=30, alias="RATE_LIMIT_MESSAGES")
    RATE_LIMIT_WINDOW: int = Field(default=60, alias="RATE_LIMIT_WINDOW")
    
    # Bot Mode
    USE_POLLING: bool = Field(default=True, alias="USE_POLLING")


telegram_settings = TelegramSettings()
    
