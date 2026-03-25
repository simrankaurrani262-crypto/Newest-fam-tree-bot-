"""
Main Settings Configuration
"""
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Environment
    ENVIRONMENT: str = Field(default="development", alias="ENVIRONMENT")
    DEBUG: bool = Field(default=True, alias="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Bot
    BOT_TOKEN_ALPHA: str = Field(default="", alias="BOT_TOKEN_ALPHA")
    BOT_TOKEN_BETA: str = Field(default="", alias="BOT_TOKEN_BETA")
    BOT_NAME_ALPHA: str = Field(default="fam_tree_bot", alias="BOT_NAME_ALPHA")
    BOT_NAME_BETA: str = Field(default="famtreebbot", alias="BOT_NAME_BETA")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/famtreebot",
        alias="DATABASE_URL"
    )
    DB_HOST: str = Field(default="localhost", alias="DB_HOST")
    DB_PORT: int = Field(default=5432, alias="DB_PORT")
    DB_NAME: str = Field(default="famtreebot", alias="DB_NAME")
    DB_USER: str = Field(default="famtree_user", alias="DB_USER")
    DB_PASSWORD: str = Field(default="", alias="DB_PASSWORD")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    REDIS_HOST: str = Field(default="localhost", alias="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, alias="REDIS_PORT")
    REDIS_DB: int = Field(default=0, alias="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    
    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        alias="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        alias="CELERY_RESULT_BACKEND"
    )
    CELERY_WORKER_CONCURRENCY: int = Field(default=4, alias="CELERY_WORKER_CONCURRENCY")
    
    # Webhook
    WEBHOOK_HOST: str = Field(default="", alias="WEBHOOK_HOST")
    WEBHOOK_PATH: str = Field(default="/webhook", alias="WEBHOOK_PATH")
    WEBHOOK_PORT: int = Field(default=8443, alias="WEBHOOK_PORT")
    WEBHOOK_SECRET: str = Field(default="", alias="WEBHOOK_SECRET")
    WEBHOOK_ENABLED: bool = Field(default=False, alias="WEBHOOK_ENABLED")
    
    # AI/ML
    OPENAI_API_KEY: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None, alias="HUGGINGFACE_API_KEY")
    AI_ENABLED: bool = Field(default=False, alias="AI_ENABLED")
    
    # Blockchain
    ETHEREUM_RPC_URL: Optional[str] = Field(default=None, alias="ETHEREUM_RPC_URL")
    POLYGON_RPC_URL: Optional[str] = Field(default=None, alias="POLYGON_RPC_URL")
    SOLANA_RPC_URL: Optional[str] = Field(default=None, alias="SOLANA_RPC_URL")
    BLOCKCHAIN_ENABLED: bool = Field(default=False, alias="BLOCKCHAIN_ENABLED")
    
    # Security
    SECRET_KEY: str = Field(default="change-me", alias="SECRET_KEY")
    ENCRYPTION_KEY: str = Field(default="change-me-32-chars-long-key", alias="ENCRYPTION_KEY")
    JWT_SECRET: str = Field(default="change-me", alias="JWT_SECRET")
    
    # External APIs
    WEATHER_API_KEY: Optional[str] = Field(default=None, alias="WEATHER_API_KEY")
    NEWS_API_KEY: Optional[str] = Field(default=None, alias="NEWS_API_KEY")
    IMGUR_CLIENT_ID: Optional[str] = Field(default=None, alias="IMGUR_CLIENT_ID")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    PROMETHEUS_PORT: int = Field(default=9090, alias="PROMETHEUS_PORT")
    
    # Supported Languages
    SUPPORTED_LANGUAGES: List[str] = Field(
        default=["en", "ru", "fr", "es", "de", "zh", "it", "uk"],
        alias="SUPPORTED_LANGUAGES"
    )
    DEFAULT_LANGUAGE: str = Field(default="en", alias="DEFAULT_LANGUAGE")
    
    # System Limits
    MAX_FRIENDS: int = Field(default=100, alias="MAX_FRIENDS")
    MAX_PARTNERS: int = Field(default=7, alias="MAX_PARTNERS")
    MAX_CHILDREN: int = Field(default=8, alias="MAX_CHILDREN")
    MAX_ROBBERY_PER_DAY: int = Field(default=8, alias="MAX_ROBBERY_PER_DAY")
    MAX_KILLS_PER_DAY: int = Field(default=5, alias="MAX_KILLS_PER_DAY")
    MAX_WORKERS: int = Field(default=5, alias="MAX_WORKERS")
    GARDEN_START_SLOTS: int = Field(default=9, alias="GARDEN_START_SLOTS")
    GARDEN_MAX_SLOTS: int = Field(default=12, alias="GARDEN_MAX_SLOTS")
    BARN_SIZE: int = Field(default=500, alias="BARN_SIZE")
    MAX_INSURANCE: int = Field(default=10, alias="MAX_INSURANCE")
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
