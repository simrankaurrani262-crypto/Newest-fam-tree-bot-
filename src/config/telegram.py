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
        extra="ignore"
    )
    
    # Bot Token (use ALPHA for development)
    BOT_TOKEN: str = Field(default="", alias="BOT_TOKEN_ALPHA")
    
    # Bot Info
    BOT_USERNAME: str = Field(default="fam_tree_bot", alias="BOT_NAME_ALPHA")
    BOT_VERSION: str = "1.0.0"
    
    # Webhook Settings
    WEBHOOK_ENABLED: bool = Field(default=False, alias="WEBHOOK_ENABLED")
    WEBHOOK_HOST: str = Field(default="", alias="WEBHOOK_HOST")
    WEBHOOK_PATH: str = Field(default="/webhook", alias="WEBHOOK_PATH")
    WEBHOOK_PORT: int = Field(default=8443, alias="WEBHOOK_PORT")
    WEBHOOK_SECRET: str = Field(default="", alias="WEBHOOK_SECRET")
    
    # Rate Limiting (per user)
    RATE_LIMIT_DEFAULT: int = 30  # commands per minute
    RATE_LIMIT_BURST: int = 10    # burst allowance
    
    # Parse Mode
    DEFAULT_PARSE_MODE: str = "HTML"
    
    # Timeouts
    MESSAGE_TIMEOUT: int = 60
    CALLBACK_TIMEOUT: int = 300


telegram_settings = TelegramSettings()
